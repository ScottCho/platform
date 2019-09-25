#!/usr/bin/env python
# coding=utf-8
from chardet.universaldetector import UniversalDetector

# 将文件转为UTF-8，传入包含多个文件路径的可迭代对象


def switch_char(filenames):
    detector = UniversalDetector()
    try:
        for filename in filenames:
            detector.reset()
        for line in open(filename, 'rb'):
            detector.feed(line)
            if detector.done:
                break
        detector.close()
        file_encod = detector.result['encoding']
        print(filename+'的文件编码是：' +file_encod)
        if file_encod is None:
            file_encod = 'utf-8'
        elif file_encod == 'ascii':
            pass
        elif file_encod != 'utf-8':
            with open(filename, 'rb') as fr:
                lines = fr.readlines()
            with open(filename, 'w', encoding='utf-8') as fw:
                for lineb in lines:
                    if lineb != None:
                        linestr = lineb.decode(encoding=file_encod)
                        fw.write(linestr)
    except Exception as e:
        print(e)
        return False
    return True
