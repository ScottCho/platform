import fnmatch
import glob
import logging
import os
import platform
import shutil
from datetime import datetime

import svn.local
import svn.remote
from flask import current_app

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
    status_id = db.Column(db.Integer, db.ForeignKey('blstatus.id'))
    status = db.relationship('Blstatus')

    def update_baseline(self,flag=0,num='01'):
    # flag=0:单条基线更新，flag=1： 合并基线更新
    # num: 当天发布更新包的个数
        message = '*****开始更新基线*****\n'
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
            dir_list = self.app.jenkins_job_dir.split('/')
            job_name_index = dir_list.index('jobs')+1
            job_name = dir_list[job_name_index]
            job = get_jenkins_job(job_name)
            jenkins_last_build = job.get_last_build().is_good()

            message += '开始构建程序.....'+job_name+'\n'
            if jenkins_last_build:
                mesagge += '该系统上一次构建结果： 成功\n'
            else:
                message += '该系统上一次构建结果： 失败\n'

            jenkins_build_number = job.get_next_build_number()
            message += 'jenkins构建日志请查： '+job.url + \
                str(jenkins_build_number)+'/console'+'\n'
            print(message)

        # DB更新
        if self.sqlno or self.pckno:
            db_username = self.app.schema.username
            db_password = self.app.schema.password
            db_host = self.app.schema.instance.machine.ip
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
                        return sql+'号sql文件不存在\n'
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
                        return '更新DB失败，可能存在多个'+sql+'号文件'
            # 将pck文件复制到base_dir,并将路径加到ALL.sql
            if self.pckno:
                for pck in self.pckno.split(','):
                    pckfile = glob.glob(source_pckdir+'/'+pck+'_*')
                    if len(pckfile) == 0:
                        current_app.logger.error(pck + '号pck文件不存在')
                        return pck+'号pck文件不存在'
                    elif len(pckfile) == 1:
                        shutil.copy(pckfile[0], target_pckdir)
                        with open(DB_SCRIPT, 'a') as pckf:
                            pckf.write('prompt ' + os.path.join(target_pckdir,
                                                                os.path.basename(pckfile[0])) + '\n')
                            pckf.write('@'+os.path.join(target_pckdir,
                                                        os.path.basename(pckfile[0]))+'\n')
                    else:
                        current_app.logger.error(pck + '号pck文件不存在')
                        return '更新DB失败，可能存在多个'+pck+'号文件'

            # 将rollback文件复制到base_dir,并将路径加到ALL.sql
            if self.rollbackno:
                for nu in self.rollbackno.split(','):
                    rollbackfile = glob.glob(source_rollbackdir+'/'+nu+'_*')
                    if len(rollbackfile) == 0:
                        current_app.logger.error(nu + '号rollback文件不存在')
                        return nu+'号rollback文件不存在'
                    elif len(rollbackfile) == 1:
                        shutil.copy(rollbackfile[0], target_rollbackdir)
                        with open(ROLLBACK_SCRIPT, 'a') as rollbackf:
                            rollbackf.write(
                                'prompt ' + os.path.join(target_rollbackdir, os.path.basename(rollbackfile[0])) + '\n')
                            rollbackf.write(
                                '@'+os.path.join(target_rollbackdir, os.path.basename(rollbackfile[0]))+'\n')
                    else:
                        current_app.logger.error(nu + '号rollback文件不存在')
                        return '更新DB失败，可能存在多个'+nu+'号文件'

            # 将base_dir中的文件统一为utf-8
            if switch_char.switch_char(fnmatch_file.find_specific_files(base_dir)) is False:
                return '请检查DB文件的字符集是否为utf-8无BOM'

            # 处理ALL*脚本，并执行两次
            message = '\n开始更新DB....\n'
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

            # 根据基线的id触发Jenkins参数构建
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
        send_email(recipients, mailtheme,
               'mail/version/baseline.html', attachments, baseline=self
                )
    # 发布程序
    def build_app_job(self, flag=0):
        # 1. 读取版本号，得到变更文件的增量部署文件
        version_list = self.versionno.split(',')  # 本次基线版本号list
        compile_file_list = []  # 增量部署文件
        for version in version_list:
            # 连接SVN服务器,得到一个变更集
            source_files = diff_summary_files(
                self.app.source_dir, int(version)-1, int(version))
            # 将变更集中的源代码路径编译后的路径写入list中
            compile_file_list += [trans_java(self.app.subsystem.en_name,
                                             self.app.source_dir, f) for f in source_files]

        # 2. 将compile_file_list中的文件写入到jenkins_job_home中的txt中（core_20191224_1246.txt)
        # 防止有相同基线序号的文件存在
        old_file_list = glob.glob(os.path.join(self.app.jenkins_job_dir,'/')+'*_'+str(self.id)+'.txt')
        if old_file_list:
            for old_file in old_file_list:
                os.remove(old_file)

        compile_file_path = os.path.join(self.app.jenkins_job_dir, self.app.subsystem.en_name +
                                         '_'+datetime.utcnow().strftime("%Y%m%d")+'_'+str(self.id)+'.txt')
        print(compile_file_path)
        with open(compile_file_path, 'w') as fw:
            for line in compile_file_list:
                fw.write('"'+line+'"'+'\n')

        
        #jenkins_job_dir=/root/.jenkins/jobs/WLink_CORE/WORKSPACE
        dir_list = self.app.jenkins_job_dir.split('/')
        job_name_index = dir_list.index('jobs')+1
        job_name = dir_list[job_name_index]
        job = get_jenkins_job(job_name)
        jenkins_last_build = job.get_last_build().is_good()

        msg = '开始构建程序.....'+job_name+'\n'
        if jenkins_last_build:
            msg += '该系统上一次构建结果： 成功\n'
        else:
            msg += '该系统上一次构建结果： 失败\n'
        jenkins_build_number = job.get_next_build_number()
        msg += 'jenkins构建日志请查： '+job.url + \
            str(jenkins_build_number)+'/console'+'\n'
        current_app.logger.info(msg)
        print(msg)

        # 3. 使用request触发Jenkins构建
        build_with_parameters(job_name,baseline_id=self.id)
        return msg

    # 发布DB,flag=0,发布SIT，flag=1基线合并发布,num为更新包次数
    def build_db_job(self, flag=0, num='01'):
        # DB的用户名实例密码
        db_username = self.app.schema.username
        db_password = self.app.schema.password
        db_host = self.app.schema.instance.machine.ip
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
                    return sql+'号sql文件不存在\n'
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
                    return '更新DB失败，可能存在多个'+sql+'号文件'
        # 将pck文件复制到base_dir,并将路径加到ALL.sql
        if self.pckno:
            for pck in self.pckno.split(','):
                pckfile = glob.glob(source_pckdir+'/'+pck+'_*')
                if len(pckfile) == 0:
                    current_app.logger.error(pck + '号pck文件不存在')
                    return pck+'号pck文件不存在'
                elif len(pckfile) == 1:
                    shutil.copy(pckfile[0], target_pckdir)
                    with open(DB_SCRIPT, 'a') as pckf:
                        pckf.write('prompt ' + os.path.join(target_pckdir,
                                                            os.path.basename(pckfile[0])) + '\n')
                        pckf.write('@'+os.path.join(target_pckdir,
                                                    os.path.basename(pckfile[0]))+'\n')
                else:
                    current_app.logger.error(pck + '号pck文件不存在')
                    return '更新DB失败，可能存在多个'+pck+'号文件'

        # 将rollback文件复制到base_dir,并将路径加到ALL.sql
        if self.rollbackno:
            for nu in self.rollbackno.split(','):
                rollbackfile = glob.glob(source_rollbackdir+'/'+nu+'_*')
                if len(rollbackfile) == 0:
                    current_app.logger.error(nu + '号rollback文件不存在')
                    return nu+'号rollback文件不存在'
                elif len(rollbackfile) == 1:
                    shutil.copy(rollbackfile[0], target_rollbackdir)
                    with open(ROLLBACK_SCRIPT, 'a') as rollbackf:
                        rollbackf.write(
                            'prompt ' + os.path.join(target_rollbackdir, os.path.basename(rollbackfile[0])) + '\n')
                        rollbackf.write(
                            '@'+os.path.join(target_rollbackdir, os.path.basename(rollbackfile[0]))+'\n')
                else:
                    current_app.logger.error(nu + '号rollback文件不存在')
                    return '更新DB失败，可能存在多个'+nu+'号文件'

        # 将base_dir中的文件统一为utf-8
        if switch_char.switch_char(fnmatch_file.find_specific_files(base_dir)) is False:
            return '请检查DB文件的字符集是否为utf-8无BOM'

        # 处理ALL*脚本，并执行两次
        db_result = '\n开始更新DB....\n'
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
            err_message = 'sqlplus中执行db脚本失败,请检查！！！'+output.decode('utf-8')
            current_app.logger.error(err_message)
            return err_message
        else:
            output = output.decode('utf-8')
            current_app.logger.info(output)
            db_result += output
        return db_result

# 基线状态表


class Blstatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(20), nullable=False, index=True)

# 更新包表


class Package(db.Model):
    __tablename__ = 'packages'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    rlsdate = db.Column(db.DateTime(), default=datetime.utcnow)
    blineno = db.Column(db.String(500), nullable=False)
    merge_blineno = db.Column(db.String(128))
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
