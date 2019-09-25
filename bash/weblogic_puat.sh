#/bin/bash

#set domain info
domainHome="/u01/oracle/welllinkuat/user_projects/domains/welllinkuat"
adminURL=http://192.168.0.31:7101

#Server Name
srv_adm=Admin
srv_sso=WLS_SSO
srv_ins=WLS_CORE
srv_act=WLS_ACTSYS
srv_rep=WLS_STATS
srv_pri=WLS_PRINT
srv_dms=WLS_DMS
arv_adm=AdminServer

#Server PID
sso_pid=$(ps -ef |grep "Dweblogic.Name=$srv_sso"|grep -v grep|awk '{print $2}')
ins_pid=$(ps -ef |grep "Dweblogic.Name=$srv_ins"|grep -v grep|awk '{print $2}')
act_pid=$(ps -ef |grep "Dweblogic.Name=$srv_act"|grep -v grep|awk '{print $2}')
rep_pid=$(ps -ef |grep "Dweblogic.Name=$srv_rep"|grep -v grep|awk '{print $2}')
pri_pid=$(ps -ef |grep "Dweblogic.Name=$srv_pri"|grep -v grep|awk '{print $2}')
dms_pid=$(ps -ef |grep "Dweblogic.Name=$srv_dms"|grep -v grep|awk '{print $2}')
adm_pid=$(ps -ef |grep "Dweblogic.Name=$srv_adm"|grep -v grep|awk '{print $2}')

#set server log
runLogDir=/home/weblogic/logs
[ ! -e $runLogDir ]  && mkdir $runLogDir
ssoLog=${runLogDir}/${srv_sso}.log
insLog=${runLogDir}/${srv_ins}.log
actLog=${runLogDir}/${srv_act}.log
repLog=${runLogDir}/${srv_rep}.log
priLog=${runLogDir}/${srv_pri}.log
dmsLog=${runLogDir}/${srv_dms}.log
adminLog=${runLogDir}/${srv_adm}.log

#set application cache
insCache=${domainHome}"/application_sinosoftWorkingDir"
actCache=${domainHome}"/reserve_sinosoftWorkingDir"
repCache=${domainHome}"/jspdir"
priCache=${domainHome}"/PrintFlat_sinosoftWorkingDir"
dmsCache=${domainHome}"/document_sinosoftWorkingDir"

#set start timeout
timeout=600

#set time format 
time=$(date +"%Y%m%d-%H%M%S")

function start(){
  case "$1" in
    sso)
       startSSO
       ;;
   core)
      startINS 
       ;;
   reserve)
     startACT
      ;;
   report)
     startREP
      ;;
   print)
     startPRI
      ;;
   dms)
     startDMS
      ;;
   all)
     startSSO
     startINS
     startACT
     startREP
     startPRI
     startDMS
      ;;
   *)
     echo $"Usage: $0 {start} {sso|ins|act|rep|pri|dms|all}"
     exit 2
  esac           
    
}

function startSSO(){
  stop core
  rm -rf ${domainHome}/servers/${srv_sso}/{cache,data,tmp}
  nohup ${domainHome}/bin/startManagedWebLogic.sh ${srv_sso}  ${adminURL} >${ssoLog} 2>&1 &
  echo ""
  echo "   <$time> <The startup log is being written to the ${ssoLog},  Please wait several minute.......>"
  echo ""
  sleep 5
  checkRun $ssoLog
}

function startINS(){
  stop core
  [ -e ${insCache} ] && rm -rf ${insCache}
  rm -rf ${domainHome}/servers/${srv_ins}/{cache,data,tmp}
  export USER_MEM_ARGS="-Xms1536m -Xmx1536m -XX:MaxPermSize=512m"
  nohup ${domainHome}/bin/startManagedWebLogic.sh ${srv_ins}  ${adminURL} >${insLog} 2>&1 &
  echo ""
  echo "   <$time> <The startup log is being written to the ${insLog},  Please wait several minute.......>"
  echo ""
  sleep 5
  checkRun $insLog
}

function startACT(){
  stop reserve
  [ -e ${actCache} ] && rm -rf ${actCache}
  rm -rf ${domainHome}/servers/${srv_act}/{cache,data,tmp}
  export USER_MEM_ARGS="-Xms1024m -Xmx1024m -XX:MaxPermSize=512m"
  nohup ${domainHome}/bin/startManagedWebLogic.sh ${srv_act}  ${adminURL} >${actLog} 2>&1 &
  echo ""
  echo "   <$time> <The startup log is being written to the ${actLog},  Please wait several minute.......>"
  echo ""
  sleep 5
  checkRun $actLog
}

function startREP(){
  stop report
  [ -e ${repCache} ] && rm -rf ${repCache}
  rm -rf ${domainHome}/servers/${srv_rep}/{cache,data,tmp}
  export USER_MEM_ARGS="-Xms1024m -Xmx1024m -XX:MaxPermSize=512m"
  nohup ${domainHome}/bin/startManagedWebLogic.sh ${srv_rep}  ${adminURL} >${repLog} 2>&1 &
  echo ""
  echo "   <$time> <The startup log is being written to the ${repLog},  Please wait several minute.......>"
  echo ""
  sleep 5
  checkRun $repLog
}

function startPRI(){
  stop print
  [ -e ${priCache} ] && rm -rf ${priCache}
  rm -rf ${domainHome}/servers/${srv_pri}/{cache,data,tmp}
  export USER_MEM_ARGS="-Xms2048m -Xmx2048m -XX:MaxPermSize=512m"
  nohup ${domainHome}/bin/startManagedWebLogic.sh ${srv_pri}  ${adminURL} >${priLog} 2>&1 &
  echo ""
  echo "   <$time> <The startup log is being written to the ${priLog},  Please wait several minute.......>"
  echo ""
  sleep 5
  checkRun $priLog
}

function startDMS(){
  stop dms
  [ -e ${dmsCache} ] && rm -rf ${dmsCache}
  rm -rf ${domainHome}/servers/${srv_dms}/{cache,data,tmp}
  export USER_MEM_ARGS="-Xms1024m -Xmx1024m -XX:MaxPermSize=512m"
  nohup ${domainHome}/bin/startManagedWebLogic.sh ${srv_dms}  ${adminURL} >${dmsLog} 2>&1 &
  echo ""
  echo "   <$time> <The startup log is being written to the ${dmsLog},  Please wait several minute.......>"
  echo ""
  sleep 5
  checkRun $dmsLog
}


function stop(){
  case "$1" in 
     all)
        for pid in $sso_pid $ins_pid $act_pid $rep_pid $pri_pid $dms_pid;do 
          echo kill -9 ${pid}
          kill -9 ${pid}
        done
      ;;
    sso)
      [[ -n $sso_pid ]] && kill -9 ${sso_pid} || echo "$1 already stopped."
      ;;
    core)
      [[ -n $ins_pid ]] && kill -9 ${ins_pid} || echo "$1 already stopped."
      ;;
    reserve)
      [[ -n $act_pid ]] &&  kill -9 ${act_pid} || echo "$1 already stopped."
      ;;
    report)
      [[ -n $rep_pid ]] && kill -9 ${rep_pid} || echo "$1 already stopped."
      ;;
    print)
      [[ -n $pri_pid ]] && kill -9 ${pri_pid} || echo "$1 already stopped."
      ;;
    dms)
      [[ -n $dms_pid ]] && kill -9 ${dms_pid} || echo "$1 already stopped."
      ;;
    adm)
      [[ -n $adm_pid ]] && kill -9 ${adm_pid} || echo "$1 already stopped."
      ;;
    *)
      echo $"Usage: $0 {stop} {sso|ins|act|rep|pri|dms|all}"
      exit 2
  esac
  if [[ $? -eq 0 ]];then  
    echo "Stop $1 server                [OK]"
  else
    echo "Stop $1 server                [FAILED]"
  fi
}

function checkRun {
    for((i=0;i<$timeout;i++));do
       sleep 1
       STATUS=$(grep -E "RUNNING mode|FORCE_SHUTTING_DOWN"  ${1})
       if [[ $STATUS =~ "RUNNING mode" ]];then
          echo -e "    <$(echo $1|awk -F[/.] '{print $(NF-1)}') server start Successful.>"
          break
       elif [[ $STATUS =~ "FORCE_SHUTTING_DOWN" ]];then
          echo -e "$Start a mistake,please check ${1}"
          exit -1
       fi
       if [[ $i -eq 600 ]];then
          echo -e "Timeout,please check ${1}"
          exit -1
       fi
done

}


# See how we were called.
case "$1" in
  start)
    start $2
    ;;
  stop)
    stop $2
   ;;
  *)
    echo $"Usage: $0 {start|stop} {sso|ins|act|rep|pri|dms|adm|all}"
    exit 2
esac
