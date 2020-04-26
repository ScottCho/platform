#!/bin/bash
# this script is created by 
rm -rf /update/WINGLUNG/*7z
cd /update/WINGLUNG/$1
mv APP CLASS
mv DB EXECUTE_CODE
cd /update/WINGLUNG/${1}/EXECUTE_CODE
for sql in $(find .   -maxdepth 1 -type f  -name '*ALL.sql');do
    basesql=$(basename ${sql})
    new="$(echo $basesql|awk -F '[_.]' '{print $2}')_$(echo $basesql|awk -F '[_.]' '{print $4}')_$(echo $basesql|awk -F '[_.]' '{print $1}'|tr 'A-Z' 'a-z')_$(echo $basesql|awk -F '[_.]' '{print $3}').$(echo $basesql|awk -F '[_.]' '{print $5}')"
    sed -i "s#/update/WINGLUNG/DB#/prog_update/${1}#g" ${basesql}
    sed -i '1d' ${basesql}
    sed -i '$d' ${basesql}
    mv ${sql} ${new}
done

cd /update/WINGLUNG/${1}/EXECUTE_CODE/ROLLBACK
for sql in $(find .   -maxdepth 1 -type f  -name '*ALL_ROLLBACK_01.sql');do
    basesql=$(basename ${sql})
    sed -i "s#/update/WINGLUNG/DB#/prog_update/${1}#g" ${basesql}
done

cd /update/WINGLUNG/${1}
tar -cvf "$1".tar *
md5sum "$1".tar >"$1".md5
7za  -psinosoft a "$1".7z  "$1".tar "$1".md5
cp "$1".7z /SVN/Update/WINGLUNG/05-packages
mv "$1".7z /update/WINGLUNG/
cd /SVN/Update/WINGLUNG/05-packages
/usr/bin/svn add "$1".7z
/usr/bin/svn ci -m "'add package' $1" "$1".7z
