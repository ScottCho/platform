#!/bin/bash
# this script is created by zhaoyong
rm -rf {{ target_dir }}*7z
cd {{ target_dir }}$1
mv APP CLASS
mv DB EXECUTE_CODE
cd {{ target_dir }}${1}/EXECUTE_CODE
for sql in $(find .   -maxdepth 1 -type f  -name '*ALL.sql');do
    basesql=$(basename ${sql})
    new="$(echo $basesql|awk -F '[_.]' '{print $2}')_$(echo $basesql|awk -F '[_.]' '{print $4}')_$(echo $basesql|awk -F '[_.]' '{print $1}'|tr 'A-Z' 'a-z')_$(echo $basesql|awk -F '[_.]' '{print $3}').$(echo $basesql|awk -F '[_.]' '{print $5}')"
    sed  -i "s#{{ target_dir }}[0-9]\+/DB#/prog_update/${1}#g" ${basesql}
    sed -i '1d' ${basesql}
    sed -i '$d' ${basesql}
    mv ${sql} ${new}
done

cd {{ target_dir }}${1}/EXECUTE_CODE/ROLLBACK
for sql in $(find .   -maxdepth 1 -type f  -name '*ALL_ROLLBACK_01.sql');do
    basesql=$(basename ${sql})
    sed -i "s#{{ target_dir }}DB#/prog_update/${1}#g" ${basesql}
done

cd {{ target_dir }}${1}
tar -cvf "$1".tar *
md5sum "$1".tar >"$1".md5
7za  -psinosoft a "$1".7z  "$1".tar "$1".md5
cp "$1".7z {{ source_dir }}05-packages
mv "$1".7z {{ target_dir }}
cd {{ source_dir }}05-packages
/usr/bin/svn add "$1".7z
/usr/bin/svn ci -m "'add package' $1" "$1".7z
