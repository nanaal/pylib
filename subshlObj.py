#!/usr/bin/python
# -*- coding: utf-8 -*-

from conf.Gconf import *
import time
import sys
sys.path.append(pexpect_lib_path)

import pexpect


class subshlObj(object):
      def __init__(self):
          self.connect_handle = None

      #if you would like to execute this function
      #on remote host, please set connect handle 
      #before you execute any other commands
      def set_connect_handle(self, conn_handle):
          self.connect_handle = conn_handle

      def subshl(self):
          tmp_handle = self.connect_handle
          need_close_handle = False
          if tmp_handle == None:
             tmp_handle = pexpect.spawn('/cs/sn/cep/subshl')
             need_close_handle = True
          else:
             tmp_handle.sendline('/cs/sn/cep/subshl')
          index1 = tmp_handle.expect(['All rights reserved.*<', pexpect.TIMEOUT])
          print('%s%s' % (tmp_handle.before,tmp_handle.after))
          if not index1 == 0:
             if need_close_handle == True:
                tmp_handle.close()
             return (None, False, 1)
          return (tmp_handle, need_close_handle, 0)

      def quit(self, conn_handle):
          if conn_handle == None:
             return 1
          conn_handle.sendline('quit')
          index1 = conn_handle.expect(['>',pexpect.EOF,pexpect.TIMEOUT,
                                      'CONTINUE Y OR N'])
          print("%s%s" % (conn_handle.before, conn_handle.after))
          if index1 == 3:
             conn_handle.sendline('Y')
          return 0

      def spa_exist(self, conn_handle, spa_name):
          if conn_handle == None:
             return 2
          conn_handle.sendline('op:status,spa=%s' % (spa_name))
          index1 = conn_handle.expect_exact(['NOT FOUND', 'SPA STATE', pexpect.EOF, pexpect.TIMEOUT])
          print('%s%s' % (conn_handle.before,conn_handle.after))
          if index1 == 1:
             return 0
          else:
             return 1

      def install_config_spa(self, conn_handle, spa_name):
          if conn_handle == None:
             return 1
          index1 = self.spa_exist(conn_handle, spa_name)
          if index1 == 0:
             self.abt_spa(conn_handle, spa_name)
             self.delete_config_spa(conn_handle, spa_name)
             time.sleep(3)
          conn_handle.sendline('install:config,spa=%s' % (spa_name))
          index1 = conn_handle.expect(['SPA FILE INSTALLATION:.+SUCCEEDED', 'SPA FILE INSTALLATION:.+FAILED', pexpect.EOF, pexpect.TIMEOUT])
          print('%s%s' % (conn_handle.before,conn_handle.after))
          if not index1 == 0:
             return 1
          else:
             return 0
          
      def install_proc_spa(self, conn_handle, spa_name):
          if conn_handle == None:
             return 1
          conn_handle.sendline('install:proc,spa=%s' % (spa_name))
          index1 = conn_handle.expect(['SPA PROCESS INSTALLATION:.+SUCCEEDED', 'SPA PROCESS INSTALLATION:.+FAILED', pexpect.EOF, pexpect.TIMEOUT])
          print('%s%s' % (conn_handle.before,conn_handle.after))
          if not index1 == 0:
             return 1
          else:
             return 0

      def rst_spa(self, conn_handle, spa_name):
          if conn_handle == None:
             return 1
          conn_handle.sendline('rst:spa=%s' % (spa_name))
          index1 = conn_handle.expect(['RST SPA.+COMPLETED SUCCESSFULLY', 'RST SPA.+FAILED', pexpect.EOF, pexpect.TIMEOUT])
          print('%s%s' % (conn_handle.before,conn_handle.after))
          if not index1 == 0:
             return 1
          else:
             return 0

      def abt_spa(self, conn_handle, spa_name):
          if conn_handle == None:
             return 1
          conn_handle.sendline('abt:spa=%s' % (spa_name))
          index1 = conn_handle.expect_exact(['CONTINUE Y OR N', pexpect.EOF, pexpect.TIMEOUT])
          print('%s%s' % (conn_handle.before,conn_handle.after))
          if not index1 == 0:
             return 1
          conn_handle.sendline('Y')
          index1 = conn_handle.expect(['ABT SPA.+COMPLETED SUCCESSFULLY', 'ABT SPA.+FAILED', pexpect.EOF, pexpect.TIMEOUT])
          print('%s%s' % (conn_handle.before,conn_handle.after))
          if not index1 == 0:
             return 1
          else:
             return 0

      def delete_config_spa(self, conn_handle, spa_name):
          if conn_handle == None:
             return 1
          conn_handle.sendline('delete:config,spa=%s' % (spa_name))
          index1 = conn_handle.expect_exact(['CONTINUE Y OR N', pexpect.EOF, pexpect.TIMEOUT])
          print('%s%s' % (conn_handle.before,conn_handle.after))
          if not index1 == 0:
             return 1
          conn_handle.sendline('Y')
          index1 = conn_handle.expect(['SPA FILE DELETION:.+SUCCEEDED', 'SPA FILE DELETION:.+FAILED', pexpect.EOF, pexpect.TIMEOUT])
          print('%s%s' % (conn_handle.before,conn_handle.after))
          if not index1 == 0:
             return 0
          else:
             return 1
      
      def init_proc(self, conn_handle, proc_name):
          if conn_handle == None:
             return 1
          conn_handle.sendline('init:proc=%s, level=1,ucl' % (proc_name))
          index1 = conn_handle.expect(['INIT PROC.+REQUEST SUCCESSFULLY ACKNOWLEDGED',pexpect.EOF,pexpect.TIMEOUT])
          print("%s%s" %(conn_handle.before,conn_handle.after))
          if not index1 == 0:
             return 1
          else:
             return 0
      
      def op_uuid(self, conn_handle):
          if conn_handle == None:
             return 1
          conn_handle.sendline('op:vm,uuid')
          conn_handle.waitnoecho()
          index1 = conn_handle.expect(['COMPLETED','FAILED', pexpect.EOF,pexpect.TIMEOUT])
          print("%s%s" % (conn_handle.before,conn_handle.after))
          if not index1 == 0:
             return 1
          else:
             return 0

      def trace_proc(self,conn_handle,proc_name, mode_value):
          if conn_handle == None:
             return 1
          conn_handle.sendline('trace:proc=%s,mode=%s,ucl' % (proc_name,mode_value))
          while True:
             index1 = conn_handle.expect_exact(['<','CONTINUE Y OR N?',pexpect.EOF,pexpect.TIMEOUT])
             if index1 == 1:
                conn_handle.sendline('Y')
             elif index1 == 0:
                return 0
             else:
                return 1

      def cep(self,conn_handle,cmd_str,expect_str):
          if conn_handle == None:
             return 1
          conn_handle.sendline(cmd_str)
          index1 = conn_handle.expect([expect_str,pexpect.EOF,pexpect.TIMEOUT])
          if index1 == 0:
             return 0
          else:
             return 1 
