#!/bin/bash
# this script is created by zhaoyong
rm -rf {{ target_dir }}*zip

cd {{ target_dir }}${1}/DB
count=1
for sql in $(find .   -maxdepth 1 -type f  -name '*ALL.sql');do
   basesql=$(basename ${sql})
   new="${count}-${basesql}"
   sed  -i "s#{{ target_dir }}[0-9]\+/LOG#C:/DB#g" ${basesql}
   sed  -i "s#{{ target_dir }}[0-9]\+/DB*#C:/DB#g" ${basesql}
   sed -i '$d' ${basesql}
   mv ${sql} ${new}
   let count++
done

cd {{ target_dir }}${1}/APP
for jar in $(find .   -maxdepth 1 -type f  -name '*.jar');do
   basejar=$(basename ${jar})
   set -x 
   alias=${basejar%%_*}
   [[ $alias == CAS ]] && unzip  $basejar -d sso
   [[ $alias == INS ]] && unzip  $basejar -d core
   [[ $alias == RES ]] && unzip  $basejar -d actsys
   [[ $alias == REP ]] && unzip  $basejar -d stats
   [[ $alias == PRI ]] && unzip  $basejar -d print
   [[ $alias == DMS ]] && unzip  $basejar -d dms
   rm -rf $jar
   set +x
done

cd {{ target_dir }}
zip -r  "$1".zip $1
cp "$1".zip {{ source_dir }}05-packages
cd {{ source_dir }}05-packages
/usr/bin/svn add "$1".zip
/usr/bin/svn ci -m "'add package' $1" "$1".zip
