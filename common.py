#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys,os,re

def cur_dir():
    path = sys.path[0]
    if os.path.isdir(path):
        return path
    elif os.path.isfile(path):
        return os.path.dirname(path)
    return ''

def jenkins_rtp_report(ret, feature_id, case_id):
    if ret:
       print('__AUTOTEST__:%s_RTP_%s:Fail' %(feature_id, case_id))
       exit(1)
    else:
       print('__AUTOTEST__:%s_RTP_%s:Pass' %(feature_id,case_id))
       exit(0)

def modify_file(file_path, search_str, target_str):
    try:
       file_obj = open(file_path,'rb')
       lines = file_obj.readlines()
       file_obj.close()
       for indx in range(0,len(lines)):
           lines[indx] = re.sub(search_str, target_str,lines[indx])
       file_obj = open(file_path,'wb')
       file_obj.writelines(lines)
       file_obj.close()
       return 0
    except Exception as e:
       print(e)
       return 1

def find_str(src_str, search_str):
    pat = re.compile(search_str)
    return pat.findall(src_str)
