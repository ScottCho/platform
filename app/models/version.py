#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# AUTHOR: Zhao Yong
# FILE: /Code/githup/platform/app/models/version.py
# DATE: 2020/04/29 Wed
# TIME: 17:42:18

# DESCRIPTION:

import glob
import os
import shutil
from datetime import datetime
import urllib

import svn.local
import svn.remote
from flask import current_app, g, render_template, send_from_directory

from app.localemail import send_email
from app.models.service import App
from app.utils import execute_cmd, fnmatch_file, switch_char
from app.utils.jenkins import build_with_parameters, get_jenkins_job
from app.utils.svn import diff_summary_files, version_merge
from app.utils.trans_path import trans_java
from app.utils.mypath import dir_remake

from .. import db


class Baseline(db.Model):
    __tablename__ = 'baselines'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    sqlno = db.Column(db.String(1024))
    pckno = db.Column(db.String(1024))
    rollbackno = db.Column(db.String(1024))
    created = db.Column(db.DateTime(), default=datetime.utcnow)
    updateno = db.Column(db.Integer, default=0)
    mantisno = db.Column(db.String(256))
    jenkins_last_build = db.Column(db.Boolean)
    jenkins_build_number = db.Column(db.Integer)
    versionno = db.Column(db.String(1024))
    mark = db.Column(db.Text)
    app_id = db.Column(db.Integer, db.ForeignKey('apps.id'))
    app = db.relationship('App', back_populates='baselines')
    package_id = db.Column(db.Integer, db.ForeignKey('packages.id'))
    package = db.relationship('Package', back_populates='baselines')
    developer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    developer = db.relationship('User')
    status_id = db.Column(db.Integer, db.ForeignKey('status.id'), default=215)
    status = db.relationship('Status', back_populates='baselines')
    issue_requirements = db.relationship('IssueRequirement',
                                         secondary='requirement_ass_baseline',
                                         back_populates='baselines')
    issue_tasks = db.relationship('IssueTask',
                                  secondary='task_ass_baseline',
                                  back_populates='baselines')
    issue_bugs = db.relationship('IssueBug',
                                 secondary='bug_ass_baseline',
                                 back_populates='baselines')
    issue_category_id = db.Column(db.Integer,
                                  db.ForeignKey('issue_category.id'))
    issue_category = db.relationship('IssueCategory',
                                     back_populates='baselines')

    def render_package_script(self, flag=0):
        '''
        Jnekins编译后执行得打包脚本
        jar包存放目录为: '/update/WINGLUNG/{baseline_id}/APP'
        '''
        shell_script = render_template(
            'apis/v2/service/package_deploy.sh',
            jenkins_job_dir=self.app.jenkins_job_dir,
            port=self.app.port,
            alias=self.app.alias,
            deploy_host=self.app.server.ip,
            deploy_dir=self.app.deploy_dir,
            target_dir=self.app.project.target_dir,
            username=self.app.credence.username,
            flag=flag)

        # jenkin的workspace不存在package.sh,则重新创建
        package_script = os.path.join(self.app.jenkins_job_dir,
                                      'package_deploy.sh')
        print('渲染打包部署脚本：' + package_script)
        if not os.path.exists(package_script):
            with open(package_script, 'w') as f:
                f.write(shell_script)

    def update_app(self, flag=0, num='01'):
        '''
        更新基线中的应用
        flag=0:单条基线更新，flag=1： 合并基线更新
        num: 项目当天发布更新包的次数
        '''
        message = '*****开始更新应用*****\n'
        jenkins_job_name = self.app.jenkins_job_name
        version_list = self.versionno.split(',')
        compile_file_list = []  # 构建文件集
        for version in version_list:
            # SVN源代码的变更集
            source_files = diff_summary_files(self.app.source_dir,
                                              int(version) - 1, int(version))

            # 构建后的变更集
            compile_file_list += [
                trans_java(self.app.subsystem.en_name, self.app.source_dir,
                           urllib.request.unquote(f)) for f in source_files
            ]

        # 删除原有相同基线序号的变更文本
        old_file_list = glob.glob(
            os.path.join(self.app.jenkins_job_dir, '/') + '*_' + str(self.id) +
            '.txt')
        if old_file_list:
            for old_file in old_file_list:
                os.remove(old_file)

        # 变更文件写入到变更文本
        compile_file_path = os.path.join(
            self.app.jenkins_job_dir, self.app.subsystem.en_name + '_' +
            datetime.utcnow().strftime("%Y%m%d") + '_' + str(self.id) + '.txt')
        print('本次基线的增量文本：' + compile_file_path)
        with open(compile_file_path, 'w') as fw:
            for line in compile_file_list:
                fw.write('"' + line + '"' + '\n')

        # 判断前一次是否构建成功
        get_jenkins_job(jenkins_job_name, str(g.current_user.id))

        # 建立jar包存放目录
        jar_dir = os.path.join(self.app.project.target_dir, str(self.id),
                               'APP')
        dir_remake(jar_dir)

        # 判断是否存在打包脚本，不存在则创建
        self.render_package_script(flag=flag)

        # 触发jenkins构建
        print('触发jenkins job: ' + jenkins_job_name)
        build_with_parameters(jenkins_job_name,
                              str(g.current_user.id),
                              baseline_id=self.id)
        return message

    def update_db(self, flag=0, num='01'):
        '''
        DB更新
        '''
        print('DB更新')
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
            # pck从puat文件中读取
            source_pckdir = os.path.join(source_dbdir, '02-pck', 'puat')
        base_dir = os.path.join(target_dir, str(self.id), 'DB')
        log_dir = os.path.join(target_dir, str(self.id), 'LOG')
        target_sqldir = os.path.join(base_dir, 'SQL')
        target_pckdir = os.path.join(base_dir, 'PCK')
        target_rollbackdir = os.path.join(base_dir, 'ROLLBACK')

        # 建立DB和日志的目录，如果存在则删除重建
        # 目录名字为DB_{baseline_id},LOG_{baseline_id}
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
        source_dir = self.app.project.source_dir
        r = svn.local.LocalClient(source_dir)
        r.update()
        print('svn update ' + source_dir)

        # ALL脚本路径
        # /update/PICCHK/DB_2001/HXUSER_20180409_01_ALL.sql
        print('num: ' + num)
        DB_SCRIPT = os.path.join(
            base_dir,
            db_username.upper() + '_' + self.created.strftime("%Y%m%d") + '_' +
            num + '_ALL.sql')
        print('基线DB ALL脚本：' + DB_SCRIPT)
        # 回滚ALL脚本路径
        # /update/PICCHK/DB_2001/ROLLBACK/YLPROD_20191122_ALL_ROLLBACK_01.sql
        ROLLBACK_SCRIPT = os.path.join(
            target_rollbackdir,
            db_username.upper() + '_' + self.created.strftime("%Y%m%d") + '_' +
            'ALL_ROLLBACK_' + num + '.sql')

        # 将sql文件复制到DB_{baseline_id},并将路径加到ALL.sql
        if self.sqlno:
            for sql in self.sqlno.split(','):
                # 找出匹配的SQL路径，/SVN/../423_HZJ_JSUSER_20180326.sql
                sqlfile = glob.glob(source_sqldir + '/' + sql + '_*')
                # 判断匹配的SQL是否唯一
                if len(sqlfile) == 0:
                    current_app.logger.error(sql + '号sql文件不存在')
                    raise Exception(sql + '号sql文件不存在!')
                elif len(sqlfile) == 1:
                    sqlfile = sqlfile[0]
                    shutil.copy(sqlfile, target_sqldir)
                    with open(DB_SCRIPT, 'a') as sqlf:
                        sqlf.write('prompt ' + os.path.join(
                            target_sqldir, os.path.basename(sqlfile)) + '\n')
                        sqlf.write('@' + os.path.join(
                            target_sqldir, os.path.basename(sqlfile)) + '\n')
                else:
                    current_app.logger.error('存在多个相同的sql文件')
                    raise Exception(sql + '存在多个相同的sql文件!')

        # 将pck文件复制到base_dir,并将路径加到ALL.sql
        if self.pckno:
            for pck in self.pckno.split(','):
                pckfile = glob.glob(source_pckdir + '/' + pck + '_*')
                if len(pckfile) == 0:
                    current_app.logger.error(pck + '号pck文件不存在')
                    raise Exception(pck + '号pck文件不存在')
                elif len(pckfile) == 1:
                    shutil.copy(pckfile[0], target_pckdir)
                    with open(DB_SCRIPT, 'a') as pckf:
                        pckf.write('prompt ' + os.path.join(
                            target_pckdir, os.path.basename(pckfile[0])) +
                                   '\n')
                        pckf.write('@' + os.path.join(
                            target_pckdir, os.path.basename(pckfile[0])) +
                                   '\n')
                else:
                    current_app.logger.error('更新DB失败,存在多个' + pck + '号文件')
                    raise Exception('更新DB失败,存在多个' + pck + '号文件')

        # 将rollback文件复制到base_dir,并将路径加到ALL.sql
        if self.rollbackno:
            for nu in self.rollbackno.split(','):
                rollbackfile = glob.glob(source_rollbackdir + '/' + nu + '_*')
                if len(rollbackfile) == 0:
                    current_app.logger.error(nu + '号rollback文件不存在')
                    raise Exception(nu + '号rollback文件不存在')
                elif len(rollbackfile) == 1:
                    shutil.copy(rollbackfile[0], target_rollbackdir)
                    with open(ROLLBACK_SCRIPT, 'a') as rollbackf:
                        rollbackf.write(
                            'prompt ' +
                            os.path.join(target_rollbackdir,
                                         os.path.basename(rollbackfile[0])) +
                            '\n')
                        rollbackf.write(
                            '@' +
                            os.path.join(target_rollbackdir,
                                         os.path.basename(rollbackfile[0])) +
                            '\n')
                else:
                    current_app.logger.error('更新DB失败，存在多个rollback' + nu +
                                             '号文件')
                    raise Exception('更新DB失败，存在多个rollback' + nu + '号文件')

        # 将base_dir中的文件统一为utf-8
        if switch_char.switch_char(
                fnmatch_file.find_specific_files(base_dir)) is False:
            return '请检查DB文件的字符集是否为utf-8无BOM'

        # 处理ALL*脚本，并执行两次
        message = '\n开始更新DB....\n'
        print(message)
        start_content = 'spool '+log_dir+'/' + \
            os.path.basename(DB_SCRIPT).replace(
                '.sql', '.log')+'\n'+'set define off'+'\n'
        end_content = 'commit;\nspool off\nexit'
        with open(DB_SCRIPT, 'r') as rf:
            content = rf.read().replace(start_content,
                                        '').replace(end_content, '')
        with open(DB_SCRIPT, 'w') as wf:
            wf.write(start_content + content)
        with open(DB_SCRIPT, 'a') as wf:
            wf.write(end_content)
        cmd = 'sqlplus {}/{}@{}:{}/{}'.format(db_username, db_password,
                                              db_host, db_port, db_instance)
        current_app.logger.info(cmd)
        update_content = '@' + DB_SCRIPT
        current_app.logger.info('开始更新' + DB_SCRIPT)
        # returncode, output = execute_cmd.execute_cmd(cmd, update_content)
        # returncode, output = execute_cmd.execute_cmd(cmd, update_content)

        # if returncode != 0:
        #     message += 'sqlplus中执行db脚本失败,请检查！！！' + output.decode('utf-8')
        #     current_app.logger.error(message)
        # else:
        #     output = output.decode('utf-8')
        #     current_app.logger.info(output)
        #     message += outputg.current_user
        logfile = os.path.join(target_dir, str(self.id), 'log.txt')
        print(g.current_user.id)
        execute_cmd.socket_shell(cmd + ' ' + update_content,
                                 str(g.current_user.id),
                                 log=logfile)
        execute_cmd.socket_shell(cmd + ' ' + update_content,
                                 str(g.current_user.id),
                                 log=logfile)

    # 发送基线更新邮件
    def send_baseline_email(self):
        # 基线邮件主题
        if self.updateno == 1:
            mailtheme = self.app.project.name + '-' + \
                        self.app.env.name + '-' + \
                        self.created.strftime("%Y%m%d") + '-' + str(self.id)
        else:
            mailtheme = self.app.project.name + '-' + \
                        self.app.env.name + '-' + \
                        self.created.strftime("%Y%m%d") + '-' + \
                        str(self.id)+'第'+str(self.updateno)+'次重更'
        # 收件人为参与项目且账户激活的人
        recipients = []
        users = self.app.project.users
        for user in users:
            if user.is_active:
                recipients.append(user.email)
        # 附件，DB的更新日志
        log_dir = os.path.join(str(self.app.project.target_dir), str(self.id),
                               'LOG')
        attachments = fnmatch_file.find_specific_files(log_dir, '*log')
        # 发送邮件
        send_email(recipients,
                   mailtheme,
                   'apis/v2/mail/vcs/baseline.html',
                   attachments,
                   baseline=self)


# 更新包表
class Package(db.Model):
    __tablename__ = 'packages'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    features = db.Column(db.Text)
    rlsdate = db.Column(db.DateTime(), default=datetime.now)
    blineno = db.Column(db.String(500), nullable=False)
    merge_blineno = db.Column(db.String(128))
    package_count = db.Column(db.String(64), default='01')
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    env_id = db.Column(db.Integer, db.ForeignKey('envs.id'))
    remark = db.Column(db.String(500))
    baselines = db.relationship('Baseline', back_populates='package')
    project = db.relationship('Project', back_populates='packages')
    env = db.relationship('Env', back_populates='packages')
    status_id = db.Column(db.Integer, db.ForeignKey('status.id'), default=214)
    status = db.relationship('Status', back_populates='packages')

    def render_package_script(self):
        '''
        发布更新包执行的脚本
        脚本路径: project.target_dir+'/release_package_'+project.name.lower()+'.sh' 
        shell脚本参数： 更新包的名字： self.name
        '''

        # 建立jar包存放目录
        script_name = 'release_package_' + self.project.name.lower() + '.sh'
        script_path = os.path.join(self.project.target_dir, script_name)
        print('建立打包脚本：' + script_path)
        shell_script = render_template('apis/v2/service/' + script_name,
                                       target_dir=self.project.target_dir,
                                       source_dir=self.project.source_dir)

        # 不存在打包脚本,则重新创建
        if not os.path.exists(script_path):
            with open(script_path, 'w') as f:
                f.write(shell_script)

        return script_path

    def create_package_dir(self):
        '''
        在target_dir下创建空目录的更新包及LOG目录
        '''

        target_dir = self.project.target_dir
        package_dir = os.path.join(target_dir, self.name)
        app_dir = os.path.join(package_dir, 'APP')
        db_dir = os.path.join(package_dir, 'DB')
        sql_dir = os.path.join(db_dir, 'SQL')
        pck_dir = os.path.join(db_dir, 'PCK')
        rollback_dir = os.path.join(db_dir, 'ROLLBACK')

        # 如果target_dir下存在更新包，则删除重建
        if os.path.exists(package_dir):
            shutil.rmtree(package_dir)
        os.mkdir(package_dir)

        os.mkdir(app_dir)
        os.mkdir(db_dir)
        os.mkdir(sql_dir)
        os.mkdir(pck_dir)
        os.mkdir(rollback_dir)

    # def package_merge(self):
    #     '''
    #     合并更新包里面的应用版本到SVN
    #     '''
    #     merge_blineno = self.merge_blineno
    #     merge_msg = '开始合并基线....\n'
    #     print('开始合并基线....')
    #     for blineno in merge_blineno.split(','):
    #         baseline = Baseline.query.get_or_404(blineno)
    #         app = baseline.app
    #         # 基线版本按照版本号从小到大合并
    #         version_list = []
    #         if baseline.versionno:
    #             version_list = sorted(baseline.versionno.split(','))
    #         source_dir = app.source_dir
    #         workspace = app.jenkins_job_dir
    #         if version_list:
    #             for version in version_list:
    #                 # 更新SVN中的Jenkins中的源码目录
    #                 workcopy = svn.local.LocalClient(workspace)
    #                 try:
    #                     workcopy.update()
    #                 except SvnException:
    #                     merge_msg = 'SVN 工作目录更新异常'
    #                 # 合并,一个一个的版本合并提交，出现异常回滚
    #                 message = f'Merged revision {version} from {source_dir}\n'
    #                 current_app.logger.info(message)

    #                 merge_msg += message
    #                 try:
    #                     merge_result = workcopy.run_command(
    #                         'merge',
    #                         [app.source_dir, workspace, '-c', version])
    #                     if len(merge_result
    #                            ) > 2 and 'conflicts' in merge_result[3]:
    #                         merge_msg += '合并' + version + '出现冲突\n'
    #                         current_app.logger.error(merge_msg)
    #                         workcopy.run_command('revert', ['-R', workspace])
    #                     else:
    #                         # 提交
    #                         workcopy.commit(message)
    #                         merge_msg += '合并成功.\n'
    #                 except Exception:
    #                     merge_msg += '合并出现错误，请检查\n'
    #                     current_app.logger.error(merge_msg)
    #                     workcopy.run_command('revert', ['-R', workspace])
    #         else:
    #             merge_msg = '没有代码需要合并\n'
    #     # 更新包状态变成已合并
    #     self.status_id = 209
    #     db.session.add(self)
    #     db.session.commit()
    #     return merge_msg

    def package_merge(self):
        '''
        合并更新包里面的应用版本到SVN
        '''
        merge_blineno = self.merge_blineno
        merge_msg = '开始合并基线....\n'
        print('开始合并基线....')
        for blineno in merge_blineno.split(','):
            baseline = Baseline.query.get(blineno)
            app = baseline.app
            # 基线版本按照版本号从小到大合并
            version_list = []
            if baseline.versionno:
                version_list = sorted(baseline.versionno.split(','))
            source_dir = app.source_dir
            workspace = app.jenkins_job_dir
            if version_list:
                for version in version_list:
                    version_merge(workspace, source_dir, version,
                                  str(g.current_user.id))
        # 更新包状态变成已合并
        self.status_id = 209
        db.session.add(self)
        db.session.commit()
        return merge_msg

    def package_deploy(self):
        '''
        部署更新包,更新包中的merge_blineno代表的基线将会被更新
        '''
        package_count = self.package_count
        # 更新包中的基线状态修改为 '206 预UAT提测'
        baselines = self.baselines
        for baseline in baselines:
            baseline.status_id = 206
            db.session.add(baseline)
            db.session.commit()
        deploy_msg = '开始部署更新包: ' + self.name
        print(deploy_msg)
        merge_blineno = self.merge_blineno.split(',')
        print(merge_blineno)
        for nu in merge_blineno:
            merge_baseline = Baseline.query.filter_by(id=nu).one()
            print('更新合并基线：' + nu)
            try:
                update_dir = os.path.join(
                    merge_baseline.app.project.target_dir,
                    str(merge_baseline.id))
                dir_remake(update_dir)
                if merge_baseline.sqlno or merge_baseline.pckno:
                    deploy_msg += merge_baseline.update_db(flag=1,
                                                           num=package_count)
                    print('deploy_msg: ' + deploy_msg)
                if merge_baseline.versionno:
                    deploy_msg += merge_baseline.update_app(flag=1,
                                                            num=package_count)
                    print('deploy_msg: ' + deploy_msg)
            except Exception as e:
                print(e)
                return '更新出现问题，请联系管理员'
        # 将状态改为: 已部署210
        self.status_id = 210
        db.session.add(self)
        db.session.commit()
        return deploy_msg

    def package_release(self):
        '''
        更新包发布
        '''
        # 重建更新包
        self.create_package_dir()
        # 更新包中的基线状态修改为 '213 已打包'
        baselines = self.baselines
        for baseline in baselines:
            baseline.status_id = 213
            db.session.add(baseline)
            db.session.commit()

        # 删除合并基线
        # merge_blineno = self.merge_blineno
        # for nu in merge_blineno.split(','):
        #     merge_baseline = Baseline.query.get(nu)
        #     db.session.delete(merge_baseline)
        #     db.session.commit()

        target_dir = self.project.target_dir  # /update/WINGLUNG
        package_dir = os.path.join(
            target_dir, self.name)  # /update/WINGLUNG/WingLung_20200426_02
        app_dir = os.path.join(
            package_dir, 'APP')  # /update/WINGLUNG/WingLung_20200426_02/APP
        # /update/WINGLUNG/WingLung_20200426_02/DB
        db_dir = os.path.join(package_dir, 'DB')
        # /update/WINGLUNG/WingLung_20200426_02/DB/ROLLBACK
        rollback_dir = os.path.join(db_dir, 'ROLLBACK')
        sql_dir = os.path.join(db_dir, 'SQL')
        pck_dir = os.path.join(db_dir, 'PCK')

        merge_blineno = self.merge_blineno
        logs = []  # DB 日志文件
        for no in merge_blineno.split(','):
            # /update/WINGLUNG/12/APP
            source_app_dir = os.path.join(target_dir, no, 'APP')
            # /update/WINGLUNG/12/DB
            source_db_dir = os.path.join(target_dir, no, 'DB')
            # /update/WINGLUNG/12/LOG
            log_dir = os.path.join(target_dir, no, 'LOG')
            source_sql_dir = os.path.join(source_db_dir, 'SQL')
            source_pck_dir = os.path.join(source_db_dir, 'PCK')
            source_rollback_dir = os.path.join(source_db_dir, 'ROLLBACK')
            logs += glob.glob(log_dir + '/*ALL.log')

            # 移动MD5和jar文件到更新包目录中
            if os.path.exists(source_app_dir):
                app_md5_list = os.listdir(source_app_dir)
                for file in app_md5_list:
                    shutil.move(os.path.join(source_app_dir, file), app_dir)

            # 移动数据库文件到更新包目录中
            if os.path.exists(source_db_dir):
                sql_file_list = os.listdir(source_sql_dir)
                pck_file_list = os.listdir(source_pck_dir)
                rollback_file_list = os.listdir(source_rollback_dir)
                all_sql_list = glob.glob(source_db_dir + '/*ALL.sql')
                for all_sql in all_sql_list:
                    shutil.copy(all_sql, db_dir)
                for sql_file in sql_file_list:
                    shutil.copy(os.path.join(source_sql_dir, sql_file),
                                sql_dir)
                for pck_file in pck_file_list:
                    shutil.copy(os.path.join(source_pck_dir, pck_file),
                                pck_dir)
                for rollback_file in rollback_file_list:
                    shutil.copy(
                        os.path.join(source_rollback_dir, rollback_file),
                        rollback_dir)

        script_path = self.render_package_script()
        returncode, output = execute_cmd.execute_cmd('sh ' + script_path +
                                                     ' ' + self.name)

        # 将状态改为: 已交付211
        self.status_id = 211
        db.session.add(self)
        db.session.commit()

        package_path = ''
        package_zip = glob.glob(target_dir + '/' + self.name + '*zip')
        package_7z = glob.glob(target_dir + '/' + self.name + '*7z')
        if package_zip:
            package_path = package_zip[0]
        elif package_7z:
            package_path = package_7z[0]

        # 更新包接受者
        recipients = []
        users = self.project.users
        for user in users:
            if user.is_active and user.role.id in (1, 3, 5):
                recipients.append(user.email)
        # 邮件主题
        mailtheme = self.project.name + '今日发包'

        # 邮件的附件为更新包及日志
        attachments = [package_path] + logs

        send_email(recipients, mailtheme, 'apis/v2/mail/vcs/package.html',
                   attachments)

        return '已发布更新包: ' + self.name + '\n\n' + output.decode('utf-8')

    def package_download(self):
        '''
        更新包下载
        '''
        project_name = self.project.name
        if project_name == 'WingLung':
            package_name = self.name + '.7z'
        else:
            package_name = self.name + '.zip'
        package_dir = os.path.join(self.project.source_dir, '05-packages')
        print('更新包下载: ' + os.path.join(package_dir, package_name))
        return send_from_directory(package_dir,
                                   package_name,
                                   as_attachment=True)

    def package_after_post(self):
        """Hook to make custom work after post method
        1. 修改更新包里的基线的package_id
        2. 根据更新包中的合并基线，将其按照app分组合并,并提交合并成的基线
        返回分组后的基线id
        """

        # 如果是更新包修改发布则删除merge_blineno中的基线
        if self.merge_blineno:
            for no in self.merge_blineno.split(','):
                baseline = Baseline.query.filter_by(id=no).one()
                db.session.delete(baseline)
                db.session.commit()

        # 将基线按app分组 {<App 1>: [<Baseline 1>,  <Baseline 2>],<App 2>: [<Baseline 3>]}
        app_dict = {}
        merge_list = []
        for bid in self.blineno.split(','):
            baseline = Baseline.query.filter_by(id=int(bid)).one()
            baseline.package_id = self.id
            db.session.add(baseline)
            db.session.commit()
            app = baseline.app
            if app not in app_dict.keys():
                app_dict.update({app: [baseline]})
            else:
                app_dict[app].append(baseline)

        # 将相同的app合并成一条基线
        for app_key, baseline_list in app_dict.items():
            versionnos = ''
            sqlnos = ''
            pcknos = ''
            rollbacknos = ''
            for baseline in baseline_list:
                if baseline.sqlno:
                    sqlnos = '{},{}'.format(sqlnos, baseline.sqlno)
                if baseline.versionno:
                    versionnos = '{},{}'.format(versionnos, baseline.versionno)
                if baseline.pckno:
                    pcknos = '{},{}'.format(pcknos, baseline.pckno)
                if baseline.rollbackno:
                    rollbacknos = '{},{}'.format(rollbacknos,
                                                 baseline.rollbackno)

            # 将多条基线合并到同一条
            subsystem_id = app_key.subsystem_id
            project_id = app_key.project_id
            merge_app = App.query.filter_by(project_id=project_id,
                                            subsystem_id=subsystem_id,
                                            env_id=self.env_id).one()
            merge_baseline = Baseline(sqlno=sqlnos.strip(','),
                                      versionno=versionnos.strip(','),
                                      pckno=pcknos.strip(','),
                                      rollbackno=rollbacknos.strip(','),
                                      created=self.rlsdate,
                                      app_id=merge_app.id,
                                      content='合并发布',
                                      developer_id=g.current_user.id,
                                      updateno=1,
                                      status_id=203,
                                      package_id=self.id)
            db.session.add(merge_baseline)
            db.session.commit()
            merge_list.append(merge_baseline)
        merge_blineno = ','.join(str(bline.id) for bline in merge_list)
        return merge_blineno
