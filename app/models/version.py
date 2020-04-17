import fnmatch
import glob
import logging
import os
import platform
import shutil
from datetime import datetime

import svn.local
import svn.remote
from flask import current_app, render_template

from app.localemail import send_email
from app.utils import execute_cmd, fnmatch_file, switch_char
from app.utils.jenkins import (build_by_token, build_with_parameters,
                               get_jenkins_job)
from app.utils.svn import diff_summary_files
from app.utils.trans_path import trans_java


from .. import db


class Baseline(db.Model):
    __tablename__ = 'baselines'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    sqlno = db.Column(db.String(1024))
    pckno = db.Column(db.String(1024))
    rollbackno = db.Column(db.String(1024))
    created = db.Column(db.DateTime(), default=datetime.utcnow)
    updateno = db.Column(db.Integer, nullable=False)
    mantisno = db.Column(db.String(256))
    jenkins_last_build = db.Column(db.Boolean)
    jenkins_build_number = db.Column(db.Integer)
    versionno = db.Column(db.String(1024))
    mark = db.Column(db.Text)
    app_id = db.Column(db.Integer, db.ForeignKey('apps.id'))
    app = db.relationship('App', back_populates='baselines')
    package_id = db.Column(db.Integer, db.ForeignKey('packages.id'))
    package = db.relationship('Package', back_populates='baselines')
    developer_id = db.Column(db.Integer,db.ForeignKey('users.id'))
    developer = db.relationship('User')
    status_id = db.Column(db.Integer, db.ForeignKey('status.id'))
    status = db.relationship('Status', back_populates='baselines')
    irequirements = db.relationship('IssueRequirement',secondary='requirement_ass_baseline',back_populates='baselines')
    itasks = db.relationship('IssueTask', secondary='task_ass_baseline', back_populates='baselines')
    ibugs= db.relationship('IssueBug', secondary='bug_ass_baseline', back_populates='baselines')


    def update_baseline(self,flag=0,num='01'):
    # flag=0:单条基线更新，flag=1： 合并基线更新
    # num: 当天发布更新包的个数
        message = '*****开始更新基线*****\n'
        job_name = ''
        if self.versionno:
            version_list = self.versionno.split(',')
            compile_file_list = []  # 构建文件集
            for version in version_list:
                # SVN源代码的变更集
                source_files = diff_summary_files(self.app.source_dir, int(version)-1, int(version))
                # 构建后的变更集
                compile_file_list += [trans_java(self.app.subsystem.en_name,
                                             self.app.source_dir, f) for f in source_files]
                                             
            #　删除原有相同基线序号的变更文本                                
            old_file_list = glob.glob(os.path.join(self.app.jenkins_job_dir,'/')+'*_'+str(self.id)+'.txt')
            if old_file_list:
                for old_file in old_file_list:
                    os.remove(old_file)

            # 变更文件写入到变更文本
            compile_file_path = os.path.join(self.app.jenkins_job_dir, self.app.subsystem.en_name +
                                         '_'+datetime.utcnow().strftime("%Y%m%d")+'_'+str(self.id)+'.txt')
            print('本次基线的增量文本：'+compile_file_path)
            with open(compile_file_path, 'w') as fw:
                for line in compile_file_list:
                    fw.write('"'+line+'"'+'\n')

            #　判断前一次是否构建成功
            jenkins_job_dir = self.app.jenkins_job_dir
            dir_list = jenkins_job_dir.split('/')
            job_name_index = dir_list.index('jobs')+1
            job_name = dir_list[job_name_index]
            job = get_jenkins_job(job_name)
            jenkins_last_build = job.get_last_build().is_good()
            message += '开始构建程序.....'+job_name+'\n'
            if jenkins_last_build:
                message += '该系统上一次构建结果： 成功\n'
            else:
                message += '该系统上一次构建结果： 失败\n'

            jenkins_build_number = job.get_next_build_number()
            message += 'jenkins构建日志请查： '+job.url + \
                str(jenkins_build_number)+'/console'+'\n'
            print(message)

            # 判断是否存在打包脚本，不存在则创建
            self.app.package_script()

        # DB更新
        if self.sqlno or self.pckno:
            db_username = self.app.schema.username
            db_password = self.app.schema.password
            db_host = self.app.schema.instance.server.ip
            db_port = self.app.schema.instance.port
            db_instance = self.app.schema.instance.instance
            source_dbdir = self.app.project.source_dir
            source_sqldir = os.path.join(source_dbdir, '01-sql')
            source_pckdir = os.path.join(source_dbdir, '02-pck')
            source_rollbackdir = os.path.join(source_dbdir, '03-rollbackup')
            target_dir = self.app.project.target_dir
            if flag == 1:
                base_dir = os.path.join(target_dir, 'DB')
                log_dir = os.path.join(target_dir, 'LOG')
                source_pckdir = os.path.join(source_dbdir, '02-pck','puat')
            else:
                base_dir = os.path.join(target_dir, 'DB'+'_'+str(self.id))
                log_dir = os.path.join(target_dir, 'LOG'+'_'+str(self.id))
            target_sqldir = os.path.join(base_dir, 'SQL')
            target_pckdir = os.path.join(base_dir, 'PCK')
            target_rollbackdir = os.path.join(base_dir, 'ROLLBACK')
            # 重建更新包的DB和日志的目录,flag==1时在view重建
            if flag == 0:
                try:
                    if os.path.exists(base_dir):
                        shutil.rmtree(base_dir)
                    os.makedirs(target_sqldir)
                    os.mkdir(target_pckdir)
                    os.mkdir(target_rollbackdir)
                    if os.path.exists(log_dir):
                        shutil.rmtree(log_dir)
                    os.mkdir(log_dir)
                except OSError:
                    pass
            # 更新SVN中的DB
            r = svn.local.LocalClient(self.app.project.source_dir)
            r.update()
            # $base_DIR/HXUSER_20180409_01_ALL.sql
            DB_SCRIPT = os.path.join(base_dir, db_username.upper(
                    )+'_'+self.created.strftime("%Y%m%d")+'_'+num+'_ALL.sql')
            ROLLBACK_SCRIPT = os.path.join(target_rollbackdir, db_username.upper(
                    )+'_'+self.created.strftime("%Y%m%d")+'_'+'ALL_ROLLBACK_'+num+'.sql')
            # 将sql文件复制到base_dir，,并将路径加到ALL.sql
            if self.sqlno:
                for sql in self.sqlno.split(','):
                    # 找出匹配的SQL路径，/SVN/../423_HZJ_JSUSER_20180326.sql
                    sqlfile = glob.glob(source_sqldir+'/'+sql+'_*')
                    # 判断匹配的SQL是否唯一
                    if len(sqlfile) == 0:
                        current_app.logger.error(sql + '号sql文件不存在')
                        raise Exception(sql+'号sql文件不存在!') 
                    elif len(sqlfile) == 1:
                        sqlfile = sqlfile[0]
                        shutil.copy(sqlfile, target_sqldir)
                        with open(DB_SCRIPT, 'a') as sqlf:
                            sqlf.write('prompt '+os.path.join(target_sqldir,
                                                            os.path.basename(sqlfile))+'\n')
                            sqlf.write('@' + os.path.join(target_sqldir,
                                                        os.path.basename(sqlfile))+'\n')
                    else:
                        current_app.logger.error('存在多个相同的sql文件')
                        raise Exception(sql+'存在多个相同的sql文件!') 
            # 将pck文件复制到base_dir,并将路径加到ALL.sql
            if self.pckno:
                for pck in self.pckno.split(','):
                    pckfile = glob.glob(source_pckdir+'/'+pck+'_*')
                    if len(pckfile) == 0:
                        current_app.logger.error(pck + '号pck文件不存在')
                        raise Exception(pck+'号pck文件不存在')
                    elif len(pckfile) == 1:
                        shutil.copy(pckfile[0], target_pckdir)
                        with open(DB_SCRIPT, 'a') as pckf:
                            pckf.write('prompt ' + os.path.join(target_pckdir,
                                                                os.path.basename(pckfile[0])) + '\n')
                            pckf.write('@'+os.path.join(target_pckdir,
                                                        os.path.basename(pckfile[0]))+'\n')
                    else:
                        current_app.logger.error('更新DB失败,存在多个'+pck+'号文件')
                        raise Exception('更新DB失败,存在多个'+pck+'号文件')

            # 将rollback文件复制到base_dir,并将路径加到ALL.sql
            if self.rollbackno:
                for nu in self.rollbackno.split(','):
                    rollbackfile = glob.glob(source_rollbackdir+'/'+nu+'_*')
                    if len(rollbackfile) == 0:
                        current_app.logger.error(nu + '号rollback文件不存在')
                        raise Exception(nu+'号rollback文件不存在')
                    elif len(rollbackfile) == 1:
                        shutil.copy(rollbackfile[0], target_rollbackdir)
                        with open(ROLLBACK_SCRIPT, 'a') as rollbackf:
                            rollbackf.write(
                                'prompt ' + os.path.join(target_rollbackdir, os.path.basename(rollbackfile[0])) + '\n')
                            rollbackf.write(
                                '@'+os.path.join(target_rollbackdir, os.path.basename(rollbackfile[0]))+'\n')
                    else:
                        current_app.logger.error('更新DB失败，存在多个rollback'+nu+'号文件')
                        raise Exception('更新DB失败，存在多个rollback'+nu+'号文件')
                        

            # 将base_dir中的文件统一为utf-8
            if switch_char.switch_char(fnmatch_file.find_specific_files(base_dir)) is False:
                return '请检查DB文件的字符集是否为utf-8无BOM'

            # 处理ALL*脚本，并执行两次
            message += '\n开始更新DB....\n'
            start_content = 'spool '+log_dir+'/' + \
                os.path.basename(DB_SCRIPT).replace(
                    '.sql', '.log')+'\n'+'set define off'+'\n'
            end_content = 'commit;\nspool off'
            with open(DB_SCRIPT, 'r') as rf:
                content = rf.read().replace(start_content, '').replace(end_content, '')
            with open(DB_SCRIPT, 'w') as wf:
                wf.write(start_content+content)
            with open(DB_SCRIPT, 'a') as wf:
                wf.write(end_content)
            cmd = 'sqlplus {}/{}@{}:{}/{}'.format(db_username,
                                                db_password, db_host, db_port, db_instance)
            current_app.logger.info(cmd)
            update_content = '@'+DB_SCRIPT
            current_app.logger.info('开始更新'+DB_SCRIPT)
            returncode, output = execute_cmd.execute_cmd(cmd, update_content)
            returncode, output = execute_cmd.execute_cmd(cmd, update_content)
            if returncode != 0:
                message += 'sqlplus中执行db脚本失败,请检查！！！'+output.decode('utf-8')
                current_app.logger.error(message)
            else:
                output = output.decode('utf-8')
                current_app.logger.info(output)
                message += output

        # 根据基线的id触发Jenkins参数构建,先更新DB，再更新应用
        if self.versionno:
            build_with_parameters(job_name,baseline_id=self.id)
        return   message     

    # 发送基线更新邮件
    def baseline_email(self):
        # 基线邮件主题
        if self.updateno == 1:
            mailtheme = self.app.project.name + '-' + self.app.env.name + '-' + \
                self.created.strftime("%Y%m%d") + '-' + str(self.id)
        else:
            mailtheme = self.app.project.name + '-' + self.app.env.name + '-' + \
                self.created.strftime("%Y%m%d") + '-' + str(self.id)+'第'+str(self.updateno)+'次重更'
        #收件人为参与项目且账户激活的人      
        recipients = []
        users = self.app.project.users
        for user in users:
            if user.is_active:
                recipients.append(user.email)
        #附件，DB的更新日志
        log_dir = os.path.join(str(self.app.project.target_dir),
                'LOG' + '_' + str(self.id))
        attachments = fnmatch_file.find_specific_files(
            log_dir, '*log')
        #发送邮件
        send_email(['zhaoysz@sinosoft.com.cn'], mailtheme,
               'apis/v2/mail/vcs/baseline.html', attachments, baseline=self
                )
    
# 更新包表
class Package(db.Model):
    __tablename__ = 'packages'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    rlsdate = db.Column(db.DateTime(), default=datetime.utcnow)
    blineno = db.Column(db.String(500), nullable=False)
    merge_blineno = db.Column(db.String(128))
    package_count = db.Column(db.String(64))
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    env_id = db.Column(db.Integer, db.ForeignKey('envs.id'))
    remark = db.Column(db.String(500))
    baselines = db.relationship('Baseline', back_populates='package')
    project = db.relationship('Project', back_populates='packages')
    env = db.relationship('Env', back_populates='packages')

    def release_package(self):
        target_dir = self.project.target_dir
        app_dir = os.path.join(target_dir, 'APP')
        db_dir = os.path.join(target_dir, 'DB')
        log_dir = os.path.join(target_dir, 'LOG')
        package_dir = os.path.join(target_dir, self.name)

        if os.path.exists(package_dir):
            shutil.rmtree(package_dir)
        os.mkdir(package_dir)
        if os.path.exists(app_dir) and os.listdir(app_dir):
            shutil.copytree(app_dir, os.path.join(package_dir, 'APP'))
        if os.path.exists(db_dir) and os.listdir(db_dir):
            shutil.copytree(db_dir, os.path.join(package_dir, 'DB'))
        returncode, output = execute_cmd.execute_cmd(
            'sh '+target_dir+'/relase_package.sh '+self.name)
        package_path = ''
        package_zip = glob.glob(target_dir+'/*zip')
        package_7z = glob.glob(target_dir+'/*7z')
        if package_zip:
            package_path = package_zip[0]
        else:
            package_path = package_7z[0]

        # 更新包接受者
        recipients = []
        users = self.project.users
        for user in users:
            if user.is_active and user.role.id in (3, 4):
                recipients.append(user.email)
        # 邮件主题
        mailtheme = self.project.name+'今日发包'

        attachments = [package_path]
        if os.path.exists(log_dir):
            logs = glob.glob(log_dir+'/*log')
            attachments += logs

        send_email(recipients, mailtheme,
                   'mail/version/package.html', attachments)


    def package_merge(self):
        merge_blineno = self.merge_blineno
        merge_msg = '开始合并基线....</br>'
        for blineno in merge_blineno.split(','):
            baseline = Baseline.query.get_or_404(blineno)
            app = baseline.app
            version_list = sorted(baseline.versionno.split(','))
            source_dir = app.source_dir
            workspace = app.jenkins_job_dir
            for version in version_list:
                #更新SVN中的Jenkins中的源码目录
                l = svn.local.LocalClient(workspace)
                l.update()
                # 合并,一个一个的版本合并提交，出现异常回滚
                source_log = l.run_command('log',[app.source_dir,'-c',version])[3]
                message = 'Merged revision {} from {}'.format(version,source_dir)
                current_app.logger.info(message)
                merge_msg += message
                try:
                    merge_result = l.run_command('merge',
                        [app.source_dir,workspace,'-c',version])
                    if len(merge_result) > 2 and 'conflicts' in merge_result[3]:
                        merge_msg += '合并'+version+'出现冲突\n'
                        current_app.logger.error(merge_msg)
                        l.run_command('revert',['-R',workspace])
                    else:
                        #提交
                        l.commit(message)
                        merge_msg += '合并成功.</br>'
                except:
                    merge_msg += '合并出现错误，请检查</br>'
                    current_app.logger.error(merge_msg)
                    l.run_command('revert',['-R',workspace])
        return merge_msg

    # 部署更新包
    def package_deploy(self):
        package_count = self.package_count
        project = self.project
        # 更新包中的基线状态修改为 '206 预UAT提测'
        baselines = self.baselines
        for baseline in baselines:
            baseline.status_id = 206
            db.session.add(baseline)
            db.session.commit()
        deploy_msg = ''
        # 合并发布之前重建APP和DB目录
        project.rebuild_relase_directory()
        merge_blineno = self.merge_blineno.split(',')
        for nu in merge_blineno:
            merge_baseline = Baseline.query.get_or_404(nu)
            deploy_msg += merge_baseline.update_baseline(flag=1,num=package_count)
        return deploy_msg


    #　发布更新包
    def package_release(self):
        # 更新包中的基线状态修改为 '213 已发布UAT'
        baselines = self.baselines
        for baseline in baselines:
            baseline.status_id = 213
            db.session.add(baseline)
            db.session.commit()

        #　删除合并基线
        merge_blineno = self.merge_blineno
        for nu in merge_blineno.split(','):
            merge_baseline = Baseline.query.get_or_404(nu)
            db.session.delete(merge_baseline)
            db.session.commit()

        target_dir = self.project.target_dir
        app_dir = os.path.join(target_dir, 'APP')
        db_dir = os.path.join(target_dir, 'DB')
        log_dir = os.path.join(target_dir, 'LOG')
        package_dir = os.path.join(target_dir, self.name)

        if os.path.exists(package_dir):
            shutil.rmtree(package_dir)
        os.mkdir(package_dir)
        if os.path.exists(app_dir) and os.listdir(app_dir):
            shutil.copytree(app_dir, os.path.join(package_dir, 'APP'))
        if os.path.exists(db_dir) and os.listdir(db_dir):
            shutil.copytree(db_dir, os.path.join(package_dir, 'DB'))
        returncode, output = execute_cmd.execute_cmd(
            'sh '+target_dir+'/relase_package.sh '+self.name)
        package_path = ''
        package_zip = glob.glob(target_dir+'/*zip')
        package_7z = glob.glob(target_dir+'/*7z')
        if package_zip:
            package_path = package_zip[0]
        elif package_7z:
            package_path = package_7z[0]

        # 更新包接受者
        recipients = []
        users = self.project.users
        for user in users:
            if user.is_active and user.role.id in (3, 4):
                recipients.append(user.email)
        # 邮件主题
        mailtheme = self.project.name+'今日发包'

        attachments = [package_path]
        if os.path.exists(log_dir):
            logs = glob.glob(log_dir+'/*log')
            attachments += logs

        send_email(recipients, mailtheme,
                   'mail/version/package.html', attachments)
        
        return '更新包已发布'