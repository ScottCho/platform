def trans_java(subsystem,source_dir,file):
    if subsystem == 'B2B_ADM':
        file = file.replace(source_dir+'/',''). \
            replace('src/main/java/ins','WEB-INF/classes/ins'). \
            replace('src/main/resources/i18n','WEB-INF/classes/i18n'). \
            replace('.java','.class'). \
            replace('src/main/webapp/','')

    elif subsystem == 'B2B_WEB':
        file = file.replace(source_dir+'/',''). \
            replace('src/main/java/ins','WEB-INF/classes/ins'). \
            replace('src/main/resources/i18n','WEB-INF/classes/i18n'). \
            replace('.java','.class'). \
            replace('src/main/webapp/','')

    elif subsystem == 'sso':
        file = file.replace(source_dir+'/', '')

    elif subsystem == 'core':
        file = file.replace('.java', '.class'). \
            replace(source_dir+'/',''). \
            replace('component/com','webapps/WEB-INF/classes/com'). \
            replace('component/resources','webapps/WEB-INF/classes/resources'). \
            replace('component', 'webapps/WEB-INF/classes')

    elif subsystem == 'reserver':
        file = file.replace('.java', '.class'). \
            replace(source_dir+'/',''). \
            replace('src/com', 'reserve/WEB-INF/classes/com'). \
            replace('src/resources','reserve/WEB-INF/classes/resources')

    elif subsystem == 'account':
        file = file.replace('.java', '.class'). \
        replace(source_dir+'/',''). \
        replace('src/com', 'account/WEB-INF/classes/com'). \
        replace('src/resources','account/WEB-INF/classes/resources')
        
    elif subsystem == 'report':
        file = file.replace('.java', '.class'). \
        replace(source_dir+'/',''). \
        replace('src/com', 'Report/WEB-INF/classes/com'). \
        replace('src/resources', 'Report/WEB-INF/classes/resources'). \
        replace('src/org', 'Report/WEB-INF/classes/org')
       
    elif subsystem == 'print':
        file = file.replace(source_dir+'/', ''). \
        replace('.java', '.class'). \
        replace('modules/component/com','webapps/WEB-INF/classes/com'). \
        replace('component/resources','webapps/WEB-INF/classes/resources'). \
        replace('webapps/print/template/jasperreport/PICC/jsresources','webapps/WEB-INF/classes/jsresources'). \
        replace('component', 'webapps/WEB-INF/classes')
        
    elif subsystem == 'dms':
        file = file.replace(source_dir+'/',''). \
            replace('.java', '.class'). \
            replace('src/main/java/com', 'document/WEB-INF/classes/com'). \
            replace('src/main/resources/messages','document/WEB-INF/classes/messages'). \
            replace('src/main/resources', 'document/WEB-INF/classes'). \
            replace('src/main/', ''). \
            replace('webapp', 'document')
                
    elif subsystem == 'circreport':
        file = file.replace(source_dir+'/',''). \
            replace('.java', '.class'). \
            replace('src/java','circreport/WEB-INF/classes'). \
            replace('src/resources','circreport/WEB-INF/classes')
    
    return file