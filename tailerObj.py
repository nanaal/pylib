#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import time

from conf.Gconf import *
sys.path.append(pexpect_lib_path)
import pexpect

class tailerObj(object):
    def __init__(self, tmp_log_file_path):
        self.__log_file_path = tmp_log_file_path
        self.__callback = None

    def tail(self, tail_number, tailed_file_path, conn_handle,vnfc_map):
        if conn_handle == None:
            return 1
        count = 0
        conn_handle.sendline('tailer %s' % (tailed_file_path))
        while count < tail_number:
            #conn_handle.sendline('tailer %s' % (tailed_file_path))
            tmp_log = open(self.__log_file_path,'w')
            conn_handle.logfile = tmp_log
            conn_handle.expect([pexpect.EOF,pexpect.TIMEOUT])
            #conn_handle.sendcontrol('c')
            #print conn_handle.before
            conn_handle.logfile = None
            tmp_log.close()
            count = count + 1
            if not self.__callback == None:
                self.__callback(self.__log_file_path,vnfc_map)
            time.sleep(5)
        conn_handle.sendcontrol('c')
        return 0

    def register_callback(self, func):
        self.__callback = func
