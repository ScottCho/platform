import os, time
import requests
from datetime import datetime
from flask_login import login_required,current_user
from flask import render_template,request,flash,url_for,redirect, current_app
import svn.remote,svn.local

from app.version import version_bp
from app.version.forms import BaselineForm,SelectAppForm, \
    PackageForm,MergeBaselineForm
from .. import db
from app.models.service import Subsystem, App, Env
from app.models.auth import Project, User, Permission
from app.models.version import Baseline, Blstatus,Package
from app.utils.jenkins import get_jenkins_job
from ..localemail import send_email
from app.utils import fnmatch_file
from app.decorators import admin_required, permission_required
from app.utils.redirect_back import redirect_back


#根据选择的项目判断是否允许更新
@version_bp.route('/select/app',methods=('GET', 'POST'))
@login_required
def select_app():
    form = SelectAppForm()
    form.project.choices = [(0,'请选择')]+[(g.id,g.name) for g in Project.query.all()]
    form.subsystem.choices = [(0,'请选择')]+[(g.id,g.zh_name) for g in Subsystem.query.all()]
    form.env.choices = [(0,'请选择')]+[(g.id,g.name) for g in Env.query.all()]
    if form.validate_on_submit():
        project_id = form.project.data
        subsystem_id = form.subsystem.data
        env_id = form.env.data
        project = Project.query.get_or_404(project_id)
        if project.switch is False:
            flash('正在测试不允许更新','danger')
            return redirect(url_for('index'))
        return redirect(url_for('version.update_baseline',project_id=project_id,
            subsystem_id=subsystem_id,env_id=env_id))
    return render_template('version/select_app.html',form=form)

#发布SIT基线
@version_bp.route('/update/baseline/<int:project_id>/<int:subsystem_id>/<int:env_id>',methods=('GET', 'POST'))
@login_required
def update_baseline(project_id,subsystem_id,env_id):
    project = Project.query.get_or_404(project_id)
    project_name = project.name
    form = BaselineForm()
    if form.validate_on_submit():
        app = App.query.filter_by(project_id=project_id,env_id=env_id,subsystem_id=subsystem_id).first()
        app_id=app.id
        versionno = form.versionno.data
        sqlno = form.sqlno.data
        pckno = form.pckno.data
        rollbackno= form.rollbackno.data
        mantisno = form.mantisno.data
        content = form.content.data
        mark = form.mark.data
        updateno = 1
        status = 'SIT提测'
        job_name = os.path.basename(app.jenkins_job_dir)
        job = get_jenkins_job(job_name)
        jenkins_last_build = job.get_last_build().is_good()
        jenkins_build_number = job.get_next_build_number() 

        #将基线写入到数据库
        baseline = Baseline(versionno=versionno, 
            sqlno=sqlno,
            pckno=pckno,
            rollbackno=rollbackno,
            mantisno=mantisno,
            content=content,
            mark=mark,
            developer=current_user.username,
            jenkins_build_number=jenkins_build_number,
            jenkins_last_build=jenkins_last_build,
            updateno = updateno,
            status=status,
            app_id=app_id)
        db.session.add(baseline)
        db.session.commit()

        msg=''
        #构建Jenkins的Job
        if versionno:
            msg+=baseline.build_app_job()

        #更新数据库
        if sqlno or pckno:
            msg+=baseline.build_db_job()

        # 基线邮件主题
        mailtheme = project_name + '-' + app.env.name + '-' + \
            baseline.created.strftime("%Y%m%d") + '-' + str(baseline.id)
        
        #收件人       
        recipients = []
        users = project.users
        for user in users:
            if user.is_active:
                recipients.append(user.email)

        #附件
        log_dir = os.path.join(str(project.target_dir),
                'LOG' + '_' + str(baseline.id))
        attachments = fnmatch_file.find_specific_files(
            log_dir, '*log')

        #发送邮件
        send_email(recipients, mailtheme,
               'mail/version/baseline.html', attachments, baseline=baseline
                )
        flash('更新完毕，请查收邮件','warning')
        return render_template('version/update_result.html', msg=msg)
    return render_template('version/update_baseline.html',form=form,project_name=project_name)


# 管理基线
@version_bp.route('/manage/baseline',methods=('GET', 'POST'))
@login_required
def manage_baseline():
    page = request.args.get('page', 1, type=int)
    per_page=current_app.config['FLASKY_BASELINES_PER_PAGE']
    filter_rule = request.args.get('filter', 'me')
    if filter_rule == 'all':
        filtered_baselines = Baseline.query
    elif filter_rule == 'SIT':
        filtered_baselines = Baseline.query.filter_by(status='SIT提测')
    elif filter_rule == 'PUAT':
        filtered_baselines = Baseline.query.filter_by(status='预UAT提测')
    elif filter_rule == 'fail':
        filtered_baselines = Baseline.query.filter(Baseline.status.in_(['SIT不通过','预UAT失败','UAT不通过','生产不通过']))
    elif filter_rule == 'unrelease':
        filtered_baselines = Baseline.query.filter(~Baseline.status.in_(['已发布UAT','UAT通过','UAT不通过','作废']))
    elif filter_rule == 'release':
        filtered_baselines = Baseline.query.filter(Baseline.status.in_(['已发布UAT','UAT提测','UAT通过','已上生产']))
    else:
        filtered_baselines = Baseline.query.filter_by(developer=current_user.username)
    pagination = filtered_baselines.order_by(Baseline.id.desc()).paginate(
        page, per_page,
        error_out=False)
    baselines = pagination.items
    return render_template('version/manage_baseline.html', baselines=baselines,
                           pagination=pagination)   

'''
修改基线状态
'''

@version_bp.route('/edit/blstatus/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_blstatus(id):
    baseline = Baseline.query.get_or_404(id)
    if request.method == 'POST':
        baseline.status = request.form.get('status')
        db.session.add(baseline)
        db.session.commit()
        flash('基线状态已经改变.','warning')
        return redirect_back()
    return render_template('version/edit_blstatus.html', baseline=baseline, status=Blstatus.query.all())

'''
删除基线
'''
@version_bp.route('/delete/baseline/<int:id>')
@login_required
@permission_required(Permission.backend_manage)
def delete_baseline(id):
    baseline = Baseline.query.get_or_404(id)
    db.session.delete(baseline)
    db.session.commit()
    flash('基线已经被删除.','warning')
    return redirect_back()


'''
查看基线内容
'''

@version_bp.route('/baseline/details/<int:id>', methods=['GET', 'POST'])
@login_required
def baseline_details(id):
    baseline = Baseline.query.get_or_404(id)
    return render_template('version/details_baseline.html', baseline=baseline)

'''
基线重更
'''
@version_bp.route('/edit/baseline/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_baseline(id):
    baseline = Baseline.query.get_or_404(id)
    project = baseline.app.project
    project_name = project.name
    form = BaselineForm()
    if form.validate_on_submit():
        app = baseline.app
        app_id=app.id
        versionno = form.versionno.data
        baseline.versionno = versionno
        sqlno = form.sqlno.data
        baseline.sqlno = sqlno
        pckno = form.pckno.data
        baseline.pckno = pckno
        baseline.rollbackno= form.rollbackno.data
        baseline.mantisno = form.mantisno.data
        baseline.content = form.content.data
        baseline.mark = form.mark.data
        baseline.updateno = int(baseline.updateno) + 1
        baseline.status = 'SIT提测'
        job_name = os.path.basename(app.jenkins_job_dir)
        job = get_jenkins_job(job_name)
        jenkins_last_build = job.get_last_build().is_good()
        baseline.jenkins_last_build = jenkins_last_build
        jenkins_build_number = job.get_next_build_number()
        baseline.jenkins_build_number = jenkins_build_number
        db.session.add(baseline)
        db.session.commit()

        msg=''
        #构建Jenkins的Job
        if versionno:
            baseline.build_app_job()
            msg += 'Jenkins构建日志请查： '+job.url+str(jenkins_build_number)+'/console'
        #更新数据库
        if sqlno or pckno:
            msg+=baseline.build_db_job()

        # 基线邮件主题
        mailtheme = project_name + '-' + app.env.name + '-' + \
            baseline.created.strftime("%Y%m%d") + '-' + str(baseline.id)+'第'+str(baseline.updateno)+'次重更'

        #收件人       
        recipients = []
        users = project.users
        for user in users:
            if user.is_active:
                recipients.append(user.email)
        
        #附件
        log_dir = os.path.join(str(project.target_dir),
                               'LOG' + '_' + str(baseline.id))
        attachments = fnmatch_file.find_specific_files(
            log_dir, '*log')
        
        #发送邮件
        send_email(recipients, mailtheme,
               'mail/version/baseline.html', attachments, baseline=baseline
                )
        flash('基线已经重新更，请查收邮件','warning')
        return render_template('version/update_result.html', msg=msg)
    form.versionno.data = baseline.versionno
    form.sqlno.data = baseline.sqlno
    form.pckno.data = baseline.pckno
    form.rollbackno.data = baseline.rollbackno
    form.mantisno.data = baseline.mantisno 
    form.content.data = baseline.content
    form.mark.data = baseline.mark 
    return render_template('version/edit_baseline.html', 
        form=form,status=Blstatus.query.all()
        )

# 录入需要合并的基线，展示不同应用对应的版本号
@version_bp.route('/merge/baseline', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.backend_manage)
def merge_baseline():
    form = MergeBaselineForm()
    form.env.choices = [(0,'请选择')]+[(g.id,g.name) for g in Env.query.all()]
    if form.validate_on_submit():
        baselineno = form.baselineno.data
        env_id = form.env.data
        # 今日发包次数
        packageno = form.packageno.data
        if not packageno:
            packageno = '01'
        # 合并基线（更新包）日期,如果没有写读取当前日期
        bdate = form.date.data
        if bdate:
            bdate = datetime.strptime(bdate, "%Y%m%d")
        else:
            bdate = datetime.now()
        #将基线按app分组 {<App 1>: [<Baseline 1>,  <Baseline 2>],<App 2>: [<Baseline 3>]}
        app_dict={}
        merge_list=[]
        for bid in baselineno.split(','):
            baseline = Baseline.query.filter_by(id=int(bid)).first()
            app = baseline.app
            if app not in app_dict.keys():
                app_dict.update({app:[baseline]})
            else:
                app_dict[app].append(baseline)

        #将相同的app合并成一条基线
        for app_key, baseline_list in app_dict.items():
            versionnos = '' 
            sqlnos = ''
            pcknos = ''
            rollbacknos = ''
            for baseline in baseline_list:
                if baseline.sqlno:
                    sqlnos = '{},{}'.format(sqlnos,baseline.sqlno)
                if baseline.versionno:
                    versionnos = '{},{}'.format(versionnos,baseline.versionno)
                if baseline.pckno:
                    pcknos = '{},{}'.format(pcknos,baseline.pckno)
                if baseline.rollbackno:
                    rollbacknos = '{},{}'.format(rollbacknos,baseline.rollbackno)
               
            # 将多条基线合并到同一条
            subsystem_id = app_key.subsystem_id
            project_id = app_key.project_id
            merge_app = App.query.filter_by(project_id=project_id,subsystem_id=subsystem_id,env_id=env_id).first()
            job_name = os.path.basename(merge_app.jenkins_job_dir)
            job = get_jenkins_job(job_name)
            merge_baseline = Baseline(
                sqlno=sqlnos.strip(','),
                versionno=versionnos.strip(','),
                pckno=pcknos.strip(','),
                rollbackno=rollbacknos.strip(','),
                created=bdate,
                app_id=merge_app.id,
                content='合并基线',
                developer=current_user.username,
                updateno=1,
                status='SIT提测',
                jenkins_last_build = job.get_last_build().is_good(),
                jenkins_build_number = job.get_next_build_number()
            )
            db.session.add(merge_baseline)    
            db.session.commit()
            merge_list.append(merge_baseline)

        # 录入package表
        project = merge_list[0].app.project
        pname = "{}_{}_{}".format(project.name, bdate.strftime("%Y%m%d"),packageno)
        merge_blineno = ','.join(str(bline.id) for bline in merge_list)
        package = Package(name=pname,
                          rlsdate=datetime.now(),
                          blineno=baselineno,
                          project_id=project.id,
                          env_id=env_id,
                          merge_blineno = merge_blineno
                          )
        db.session.add(package)
        db.session.commit()

        #将基线加入package中
        for bid in baselineno.split(','):
            baseline = Baseline.query.filter_by(id=int(bid)).first()
            baseline.package_id = package.id
            db.session.add(baseline)
            db.session.commit()

        flash('本次要合并的内容如下：','warning')   
        return render_template('version/merge_details.html',merge_list=merge_list)
    return render_template('version/merge_baseline.html',form=form) 



'''
发布合并的基线
'''
@version_bp.route('/merge/update/<int:id>')
@login_required
@permission_required(Permission.backend_manage)
def merge_update(id):
    package = Package.query.get_or_404(id)
    project = package.project
    msg="" 
    #合并发布之前重建APP和DB目录
    project.rebuild_relase_directory()
    baselineno = package.merge_blineno.split(',')
    for nu in baselineno:
        merge_baseline = Baseline.query.get_or_404(nu)
        #更新数据库
        if merge_baseline.pckno or merge_baseline.sqlno:
            msg+=merge_baseline.build_db_job(flag=1)
        #构建Jenkins的Job
        if merge_baseline.versionno:
            msg+=merge_baseline.build_app_job(flag=1)
    flash('已合并发布','warning')   
    return render_template('version/update_result.html', msg=msg) 

'''
管理更新包
'''
@version_bp.route('/manage/package/', methods=['GET', 'POST'])
@login_required
def manage_package():
    packages = Package.query.order_by(Package.id.desc()).all()
    return render_template('version/manage_package.html',packages=packages)

'''
删除更新包
'''
@version_bp.route('/delete/package/<int:id>')
@login_required
def delete_package(id):
    package = Package.query.get_or_404(id)
    db.session.delete(package)
    db.session.commit()
    flash('更新已经被删除.','warning')
    return redirect_back()


'''
编辑更新包
'''
@version_bp.route('/edit/package/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.backend_manage)
def edit_package(id):
    form = PackageForm()
    package = Package.query.get_or_404(id)
    project = package.project
    env_id=package.env_id
    original_blineno = package.blineno.split(',')
    if form.validate_on_submit():
        merge_list = []
        msg=""
        name = form.name.data
        blineno = form.blineno.data
        change_blineno = blineno.split(',')
        rlsdate = datetime.now()
        remark = form.remark.data

        #增加的基线状态修改
        add_blineno = set(change_blineno) - set(original_blineno)
        for no in add_blineno:
            baseline = Baseline.query.get_or_404(no)
            baseline.status = 'SIT提测'
            baseline.package_id = package.id
            db.session.add(baseline)
            db.session.commit()

        #删除原始的合并的基线
        for no in original_blineno:
            baseline = Baseline.query.get_or_404(no)
            db.session.delete(baseline)
            db.session.commit()

        #将相同的app合并成一条基线
        #{<App 1>: [<Baseline 1>,  <Baseline 2>],<App 2>: [<Baseline 3>]}
        app_dict={}
        for no in  change_blineno:
            baseline = Baseline.query.get_or_404(no)
            app = baseline.app
            if app not in app_dict.keys():
                app_dict.update({app:[baseline]})
            else:
                app_dict[app].append(baseline)
        for app_key in app_dict.keys():
            versionnos = '' 
            sqlnos = ''
            pcknos = ''
            rollbacknos = ''
            project_name = ''
            baseline_list = app_dict[app_key]
            for baseline in baseline_list:
                bsqlno = baseline.sqlno
                bversionno = baseline.versionno
                bpckno = baseline.pckno
                brollbackno = baseline.rollbackno
                baseline.status = '预UAT提测'
                db.session.add(baseline)
                db.session.commit()
                # 拼接基线
                if bsqlno:
                    sqlnos = (str(bsqlno) + ',' + sqlnos).strip(',')
                if bversionno:
                    versionnos = (str(bversionno) + ',' + versionnos).strip(',')
                if bpckno:
                    pcknos = (str(bpckno) + ',' + pcknos).strip(',')
                if brollbackno:
                    rollbacknos = (str(brollbackno) + ',' + rollbacknos).strip(',')

            # 将多条基线合并到同一条
            subsystem_id = app_key.subsystem_id
            merge_app = App.query.filter_by(project_id=project.id,env_id=env_id,subsystem_id=subsystem_id).first()
            job_name = os.path.basename(app_key.jenkins_job_dir)
            job = get_jenkins_job(job_name)
            merge_baseline = Baseline(sqlno=sqlnos,
                                  versionno=versionnos,
                                  pckno=pcknos,
                                  rollbackno=rollbacknos,
                                  created=datetime.utcnow(),
                                  app_id=merge_app.id,
                                  content='合并发布',
                                  developer=current_user.username,
                                  updateno=1,
                                  status='已发布UAT',
                                  jenkins_last_build = job.get_last_build().is_good(),
                                  jenkins_build_number = job.get_next_build_number()
                                  )
            db.session.add(merge_baseline)    
            db.session.commit()
            merge_list.append(merge_baseline)

        # 录入package表
        merge_blineno = ','.join(str(bline.id) for bline in merge_list)
        package.blineno = blineno
        package.merge_blineno = merge_blineno
        package.remark = remark
        db.session.add(package)
        db.session.commit()
        flash('已重新合并发布','warning')
        return render_template('version/merge_details.html',merge_list=merge_list)
        
    form.name.data = package.name
    form.blineno.data = package.blineno
    form.remark.data = package.remark
    return render_template('version/edit_package.html', form=form)


'''
打包,并且删除合并的基线
'''
@version_bp.route('/release/package/<int:id>')
@login_required
@permission_required(Permission.backend_manage)
def release_package(id):
    package = Package.query.get_or_404(id)
    baselines = package.baselines
    merge_blineno = package.merge_blineno.split(',')
    for baseline in baselines:
        baseline.status = '已发布UAT'
        db.session.add(baseline)
        db.session.commit()
    
    for nu in merge_blineno:
        merge_baseline = Baseline.query.get_or_404(nu)
        db.session.delete(merge_baseline)
        db.session.commit()
    package.release_package()
    flash('已发布更新包','warning')
    return redirect_back()
    

'''
合并版本库的版本
'''
@version_bp.route('/merge/version/<int:id>')
@login_required
@permission_required(Permission.backend_manage)
def merge_version(id):
    package = Package.query.get_or_404(id)
    merge_blineno = package.merge_blineno
    merge_msg = ''
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
            #合并
            source_log = l.run_command('log',[app.source_dir,'-c',version])[3]
            message = '{} \n Merged revision {} from {}'.format(source_log,version,source_dir)
            current_app.logger.info(message)
            merge_msg += message
            try:
                merge_result = l.run_command('merge',
                    [app.source_dir,workspace,'-c',version])
                if len(merge_result) > 2 and 'conflicts' in merge_result[3]:
                    merge_msg = '合并'+version+'出现冲突'
                    current_app.logger.error(merge_msg)
                    l.run_command('revert',['-R',workspace])
                else:
                    #提交
                    l.commit(message)
            except:
                merge_msg = '合并'+version+'出现错误，请检查'
                current_app.logger.error(merge_msg)
                l.run_command('revert',['-R',workspace])
    return(merge_msg)




            
