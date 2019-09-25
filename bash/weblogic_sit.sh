#/bin/bash

#set Domian Home
sso_domain_home=/wls/bea/Oracle/Middleware/user_projects/domains/wlisdm8001
ins_domain_home=/wls/bea/Oracle/Middleware/user_projects/domains/wlisdm8002
act_domain_home=/wls/bea/Oracle/Middleware/user_projects/domains/wlisdm8003
rep_domain_home=/wls/bea/Oracle/Middleware/user_projects/domains/wlisdm8004
pri_domain_home=/wls/bea/Oracle/Middleware/user_projects/domains/wlsdm8005
dms_domain_home=/wls/bea/Oracle/Middleware/user_projects/domains/wlisdm8006


#Server Name
srv_sso=server8001
srv_ins=AdminServer
srv_act=AdminServer
srv_rep=AdminServer
srv_pri=AdminServer
srv_dms=server8001

#Server PID
sso_pid=`netstat -lntp |grep 8001|awk '{ print $NF }' |awk -F '/' '{print $1}'`
ins_pid=`netstat -lntp |grep 8002|awk '{ print $NF }' |awk -F '/' '{print $1}'`
act_pid=`netstat -lntp |grep 8003|awk '{ print $NF }' |awk -F '/' '{print $1}'`
rep_pid=`netstat -lntp |grep 8004|awk '{ print $NF }' |awk -F '/' '{print $1}'`
pri_pid=`netstat -lntp |grep 8005|awk '{ print $NF }' |awk -F '/' '{print $1}'`
dms_pid=`netstat -lntp |grep 8006|awk '{ print $NF }' |awk -F '/' '{print $1}'`


#set application cache
insCache="${ins_domain_home}/application_sinosoftWorkingDir"
actCache="${act_domain_home}/reserve_sinosoftWorkingDir"
repCache="${rep_domain_home}/jspdir"
priCache="${pri_domain_home}/PrintFlat_sinosoftWorkingDir"
dmsCache="${dms_domain_home}/document_sinosoftWorkingDir"

#set server log
ssoLog=${sso_domain_home}/nohup.out
insLog=${ins_domain_home}/nohup.out
actLog=${act_domain_home}/nohup.out
repLog=${rep_domain_home}/nohup.out
priLog=${pri_domain_home}/nohup.out
dmsLog=${dms_domain_home}/nohup.out


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
     echo $"Usage: $0 {start} {sso|core|act|rep|pri|dms|all}"
     exit 2
  esac           
    
}

function startSSO(){
  stop sso
  rm -rf ${sso_domain_home}/servers/${srv_sso}/{cache,data,tmp} 
  #nohup ${sso_domain_home}/startWebLogic.sh >${ssoLog}  2>&1 &
  ${sso_domain_home}/startWebLogic.sh
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
  #nohup ${ins_domain_home}/startWebLogic.sh >${insLog}  2>&1 &
  ${ins_domain_home}/startWebLogic.sh
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
  #nohup ${act_domain_home}/startWebLogic.sh >${actLog}  2>&1 &
  ${act_domain_home}/startWebLogic.sh
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
  #nohup ${rep_domain_home}/startWebLogic.sh >${repLog}  2>&1 &
  ${rep_domain_home}/startWebLogic.sh
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
  #nohup ${pri_domain_home}/startWebLogic.sh >${priLog}  2>&1 &
  ${pri_domain_home}/startWebLogic.sh
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
  #nohup ${dms_domain_home}/startWebLogic.sh >${dmsLog}  2>&1 &
  ${dms_domain_home}/startWebLogic.sh
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
    *)
      echo $"Usage: $0 {stop} {sso|core|reserve|report|print|dms|all}"
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
    echo $"Usage: $0 {start|stop} {sso|core|act|rep|pri|dms|adm|all}"
    exit 2
esac
