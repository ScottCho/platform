###
 # @Author: your name
 # @Date: 2020-04-26 11:04:49
 # @LastEditTime: 2020-04-26 11:04:49
 # @LastEditors: your name
 # @Description: In User Settings Edit
 # @FilePath: /platform/app/templates/apis/v2/service/package_deploy.sh
 ###
# /bin/bash

#　模板参数：　
# jenkins_job_dir = /root/.jenkins/workspace/Winglung_Core　　
# port = 8002
# alias = INS
# deploy_host = 192.168.0.12
# deploy_dir = /wls/webapps/8002
# package_dir    merge： /update/WINGLUNG/APP_12    single： /update/WINGLUNG/APP_SIT

cd {{ jenkins_job_dir }}
find {{ jenkins_job_dir }} -maxdepth 1 -name *jar -print0|xargs -0 rm -rf


APP_LIST=$(ls {{ jenkins_job_dir }}/*_${baseline_id}.txt)

if [[ ! -f $APP_LIST ]];then
    echo {{ jenkins_job_dir }} is not exists ${baseline_id} java txt file,please check!!!
    exit 2
fi
echo $APP_LIST


# Release jar
#PACKAGE_JAR=ACTUARY_8003_20180127_01.jar
#BASE_APP_LIST=ACTUARY_20180127_01.txt
BASE_APP_LIST=$(basename $APP_LIST)
APP_NAME=$(echo $BASE_APP_LIST|awk -F'[_.]' '{print $1}')
APP_DATE=$(echo $BASE_APP_LIST|awk -F'[_.]' '{print $2}')
APP_NU=$(echo $BASE_APP_LIST|awk -F'[_.]' '{print $3}')
PACKAGE_JAR={{ alias }}_{{ port }}_${APP_DATE}_${APP_NU}.jar
PACKAGE_MD5={{ alias }}_{{ port }}_${APP_DATE}_${APP_NU}.md5
cat ${APP_LIST}|xargs md5sum >${PACKAGE_MD5}
jar -cvfM  ${PACKAGE_JAR} @$APP_LIST
if [[ $? -ne 0 ]];then
    echo jar $PACKAGE_JAR fail!!
    exit 2
fi

echo "{{ jenkins_job_dir }}"/"${PACKAGE_JAR}" "{{ deploy_host }}:{{ deploy_dir }}"
#scp  "{{ jenkins_job_dir }}"/"${PACKAGE_JAR}" "{{ deploy_host }}:{{ deploy_dir }}"
#scp  "{{ jenkins_job_dir }}"/"${PACKAGE_MD5}"  "{{ deploy_host }}:{{ deploy_dir }}"

if [[ ! -d {{ package_dir }} ]];then
    mkdir {{ package_dir }}
fi 


mv "{{ jenkins_job_dir }}"/"${PACKAGE_JAR}"  "{{ package_dir }}"
mv "{{ jenkins_job_dir }}"/"${PACKAGE_MD5}" "{{ package_dir }}"

echo ssh {{ deploy_host }} "sh {{ deploy_dir }}/update.sh"
#ssh {{ deploy_host }} "sh {{ deploy_dir }}/update.sh"

rm -rf $APP_LIST

exit