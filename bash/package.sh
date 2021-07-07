PORT=8002
REMOTE_HOST="weblogic@192.168.0.31"
DEPLOY_DIR="/wls/webapps/8002"
PACKAGE_DIR="/update/WLINK/APP-SIT"
ALIAS="INS"

# delete jar file in $WORKSPACE 
cd $WORKSPACE
find ${WORKSPACE} -maxdepth 1 -name *jar -print0|xargs -0 rm -rf


APP_LIST=$(ls $WORKSPACE/*_${baseline_id}.txt)

if [[ ! -f $APP_LIST ]];then
    echo $WORKSPACE is not exists java txt file,please check!!!
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
PACKAGE_JAR=${ALIAS}_${PORT}_${APP_DATE}_${APP_NU}.jar
PACKAGE_MD5=${ALIAS}_${PORT}_${APP_DATE}_${APP_NU}.md5
cat ${APP_LIST}|xargs md5sum >${PACKAGE_MD5}
jar -cvfM  ${PACKAGE_JAR} @$APP_LIST
if [[ $? -ne 0 ]];then
    echo jar $PACKAGE_JAR fail!!
    exit 2
fi

echo "${WORKSPACE}"/"${PACKAGE_JAR}" "${REMOTE_HOST}:${DEPLOY_DIR}"
scp  "${WORKSPACE}"/"${PACKAGE_JAR}" "${REMOTE_HOST}:${DEPLOY_DIR}"
scp  "${WORKSPACE}"/"${PACKAGE_MD5}"  "${REMOTE_HOST}:${DEPLOY_DIR}"
mv "${WORKSPACE}"/"${PACKAGE_JAR}"  "${PACKAGE_DIR}"
mv "${WORKSPACE}"/"${PACKAGE_MD5}" "${PACKAGE_DIR}"

echo ssh ${REMOTE_HOST} "sh ${DEPLOY_DIR}/update.sh"
ssh ${REMOTE_HOST} "sh ${DEPLOY_DIR}/update.sh"

rm -rf $APP_LIST

exit