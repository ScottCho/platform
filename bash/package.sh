#!/bin/bash
# this script is created by  zy 20170616

JKS_DIR=$(pwd)
PORT=8006
REMOTE_HOST="weblogic@192.168.0.43"
REMOTE_PORT=22
DEPLOY_DIR="/home/weblogic/webapps/picc8006"
PACKAGE_DIR="/update/PICCHK/APP-SIT"
ALIAS="PRI"

# delete last genereted jar and md5 file
find ${JKS_DIR} -maxdepth 1 -name *jar -print0|xargs -0 rm -rf
find ${JKS_DIR} -maxdepth 1 -name *md5 -print0|xargs -0 rm -rf


#APP_LIST=ACCOUNT_20180127_01.txt
APP_LIST=$(ls $JKS_DIR/*_*.txt)
if [[ ! -f $APP_LIST ]];then
    echo $JKS_DIR is not exists java txt file,please check!!!
    exit -1
else
	echo Packing $APP_LIST.... 
fi


# Release jar
#PACKAGE_JAR=ACTUARY_8003_20180127_01.jar
#BASE_APP_LIST=ACTUARY_20180127_01.txt
BASE_APP_LIST=$(basename $APP_LIST)
APP_NAME=$(echo $BASE_APP_LIST|awk -F'[_.]' '{print $1}')
APP_DATE=$(echo $BASE_APP_LIST|awk -F'[_.]' '{print $2}')
APP_NU=$(echo $BASE_APP_LIST|awk -F'[_.]' '{print $3}')
PACKAGE_JAR=${ALIAS}_${PORT}_${APP_DATE}_${APP_NU}.jar
PACKAGE_MD5=${ALIAS}_${PORT}_${APP_DATE}_${APP_NU}.md5
cat ${APP_LIST}|xargs md5sum >${PACKAGE_MD5}
jar -cvfM  ${PACKAGE_JAR} @$APP_LIST
if [[ $? -ne 0 ]];then
    echo jar $PACKAGE_JAR fail!!
    exit -2
fi

#Remote deployment
echo scp -P $REMOTE_PORT "${JKS_DIR}"/"${PACKAGE_JAR}" "${REMOTE_HOST}:${DEPLOY_DIR}"
scp -P $REMOTE_PORT "${JKS_DIR}"/"${PACKAGE_JAR}" "${REMOTE_HOST}:${DEPLOY_DIR}"
echo scp -P $REMOTE_PORT "${JKS_DIR}"/"${PACKAGE_MD5}"  "${REMOTE_HOST}:${DEPLOY_DIR}"
scp  -P $REMOTE_PORT "${JKS_DIR}"/"${PACKAGE_MD5}"  "${REMOTE_HOST}:${DEPLOY_DIR}"
echo mv "${JKS_DIR}"/"${PACKAGE_JAR}"  "${PACKAGE_DIR}"
mv "${JKS_DIR}"/"${PACKAGE_JAR}"  "${PACKAGE_DIR}"
echo mv "${JKS_DIR}"/"${PACKAGE_MD5}" "${PACKAGE_DIR}"
mv "${JKS_DIR}"/"${PACKAGE_MD5}" "${PACKAGE_DIR}"
echo ssh -p ${REMOTE_PORT} ${REMOTE_HOST} "sh ${DEPLOY_DIR}/update.sh"
ssh -p ${REMOTE_PORT} ${REMOTE_HOST}  $"sh ${DEPLOY_DIR}/update.sh"
exit