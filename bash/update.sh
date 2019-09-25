#/bin/bash
APP_DIR="/wls/webapps/CPIC_Webapps_20190815/8002"
DOMAIN_DIR='/wls/bea/Oracle/Middleware/user_projects/tb_domains/tb_8882_domain'
APP_NAME=webapps
APP_PORT=8882
APP_ALIAS=INS
server=AdminServer
APP_CACHE=application_sinosoftWorkingDir
LOGFILE=/wls/logs/server${APP_PORT}.log

timeout=600
BACKUP_DIR="$APP_DIR/BACKUP"
JAR_DIR="$APP_DIR/JAR"
MD5_DIR="$APP_DIR/MD5"

[ ! -e $BACKUP_DIR ] && mkdir $BACKUP_DIR
[ ! -e $JAR_DIR ] && mkdir $JAR_DIR
[ ! -e $MD5_DIR ] && mkdir $MD5_DIR

function checkPackage(){
   if [ $(ls ${APP_DIR}/*jar|wc -l) -gt 1 ];then
      echo "Tere more than one jar package,please check!!!";
      rm -rf ${APP_DIR}/*jar
      exit -2;
   else
     packageName=$(basename $(ls ${APP_DIR}/*jar));
     packageAlias=$(echo $packageName|awk -F'_' '{print $1}');
     if  [[ $packageAlias != $APP_ALIAS ]];then
        echo "***Jar Package format error,please check!!![INS_8002_20171010_02.jar]"
        exit -2 
     fi
     echo "=================================================================="
     echo "Start update $packageName...."
     echo "Stop application $APP_PORT";
     stop
   fi    
}



function stop(){
    /usr/sbin/lsof -i:${APP_PORT} | awk '{ print $2 }' | while read line
      do 
        if [ $line != PID ];then
          echo "kill -9 $line"
   	      kill -9 $line
          break;
        fi
      done
    update 
}

function update(){
    #packageName=INS_8002_20160304_01.jar
   packageName=$(basename $(ls ${APP_DIR}/*jar));  
   packageDate=$(echo $packageName|awk -F'[_.]' '{print $3}')
   packageNo=$(echo $packageName|awk -F'[_.]' '{print $4}')
   if [ ! -f "${BACKUP_DIR}/${APP_NAME}_${packageDate}_${packageNo}_bak" ];then
      echo cp -fr "${APP_DIR}/${APP_NAME}"  "${BACKUP_DIR}/${APP_NAME}_${packageDate}_${packageNo}"
      cp -fr "${APP_DIR}/${APP_NAME}" "${BACKUP_DIR}/${APP_NAME}_${packageDate}_${packageNo}_bak"
   fi
   echo unzip -o   ${APP_DIR}/$packageName  -d ${APP_DIR}
   unzip -o   ${APP_DIR}/$packageName  -d ${APP_DIR}
   if [ $? = 0 ];then 
      echo  Start app $PORT...
      start $packageName
   else
      echo "Inflating error,please check!!!"
      exit -2
   fi 
    
}


function start(){
   echo rm -rf $DOMAIN_DIR/$APP_CACHE
   rm -rf $DOMAIN_DIR/$APP_CACHE
   rm -rf $DOMAIN_DIR/servers/${server}/cache
   rm -rf $DOMAIN_DIR/servers/${server}/data
   rm -rf $DOMAIN_DIR/servers/${server}/tmp
   mv ${APP_DIR}/$1  ${JAR_DIR}
   (cd ${APP_DIR};md5sum -c ${APP_DIR}/*md5)
   mv ${APP_DIR}/*md5  ${MD5_DIR}
   echo "<The startup log is being written to the ${LOGFILE},  Please wait several minute.......>"
   nohup ${DOMAIN_DIR}/startWebLogic.sh >$LOGFILE 2>&1 &
   checkRun $LOGFILE
   if [ $? = 0 ];then
      echo "$1 is installed successful"
   fi
}


function checkRun {
    for((i=0;i<$timeout;i++));do
       sleep 1
       STATUS=$(grep -E "RUNNING mode|FORCE_SHUTTING_DOWN"  ${1})
       if [[ $STATUS =~ "RUNNING mode" ]];then
          echo -e "    <$(echo $1|awk -F[/.] '{print $(NF-1)}') server start Successful."
          break
       elif [[ $STATUS =~ "FORCE_SHUTTING_DOWN" ]];then
          echo "Start a mistake,please check ${1}"
          exit -1
       fi
       if [[ $i -eq 600 ]];then
          echo  "Timeout,please check ${1}"
          exit -1
       fi
    done
}

checkPackage
