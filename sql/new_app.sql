--新建一个应用 
INSERT INTO `platform`.`apps` 
( `host`, `username`, `password`, `env_id`, `log_dir`, `project_id`, `source_dir`, `subsystem_id`, `jenkins_job_dir` )
VALUES
( '192.168.0.23', 'weblogic', 'weblogic', 2, '/wls/logs', 3, 'https://vss1/svn/root/WingLungFiles/UAT/SOURCECODE/application/modules_uat
', 2, '/root/.jenkins/jobs/CPICHK_ACCOUNT_SECURITY' );