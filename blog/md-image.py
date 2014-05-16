# -*- coding: utf-8 -*-
import datetime
import os
import shutil

#  递归创建文件夹
def mkdirs(path):
    path=path.strip()
    path=path.rstrip("\\")
    isExists=os.path.exists(path)

    if not isExists:
        os.makedirs(path)
        print path + u' 创建成功'
        return True
    else:
        print path + u' 目录已存在'
        return False

date_str = datetime.datetime.now().strftime('%Y-%m')
date_arr = date_str.split('-')
dest_dir = os.getcwd() + '/image/'+'/'.join(date_arr)

# 目标文件价可能不存在需要创建
if not os.path.exists(dest_dir):
    print '目标文件价不存在，正在创建'
    mkdirs(dest_dir)

# 开始复制文件
list_dirs = os.walk(os.getcwd() + '/src_image/')
for root, dirs, files in list_dirs:
    for f in files:
        shutil.copyfile(os.path.join(root,f),os.path.join(dest_dir,f))
        print 'file',f,' is copied'


print '文件文件复制完成。'
