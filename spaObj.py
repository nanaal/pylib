#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conf.Gconf import *
from conf.SPAconf import *
from shellObj import shellObj
from subshlObj import subshlObj
from rcvObj import rcvObj

import os,sys
sys.path.append(pexpect_lib_path)
import pexpect

class spaObj(object):
      def __init__(self):
          self.sshObj = shellObj()

      def install_sll_spa(self):
          ret = self.sshObj.shell_scp(src_usr, src_ip, src_spa_path,src_password,
                                dest_usr,dest_ip,dest_spa_path,dest_password) 
          if not ret == 0:
             print('ERROR:scp spa package to test lab failed')
             return 1
  
          conn_handle = self.sshObj.shell_ssh(dest_usr, dest_ip, dest_password)
          if conn_handle == None:
             print('ERROR:ssh to test lab failed')
             return 1
          
          file_path = spa_install_dir + "/.READY_TO_INSTALL_" + spa_name
          ret = self.sshObj.shell_remote_command(conn_handle, 'touch %s' % (file_path))
          if not ret == 0:
             print('ERROR:touch file %s failed' % (file_path))
             return 1

          subshl_obj = subshlObj()
          subshl_obj.set_connect_handle(conn_handle)
          (tmp_handle, need_close_handle, ret) = subshl_obj.subshl()
          if not ret == 0:
             print("ERROR:subshl failed")
             return 1
        
          ret = subshl_obj.install_config_spa(tmp_handle, spa_name)
          if not ret == 0:
             print("ERROR:subshl>install:config,spa=%s failed" % (spa_name))
             return 1

          ret = subshl_obj.install_proc_spa(tmp_handle, spa_name)
          if not ret == 0:
             print("ERROR:subshl>install:proc,spa=%s failed" % (spa_name))
             return 1
        
          ret = subshl_obj.rst_spa(tmp_handle, spa_name)
          if not ret == 0:
             print("ERROR:subshl>rst:spa=%s failed" % (spa_name))
             return 1

          rcv_obj = rcvObj()
          if not rcv_obj.rcv_menu(tmp_handle) == 0:
             print("ERROR:subshl>rcv:menu failed")
             return 1
          ret = rcv_obj.form_operation_map.get('6.2.3')(form_6_2_3,'I',tmp_handle)
          if not ret == 0:
             print("ERROR:configure rcv form 6.2.3 failed")
          ret = rcv_obj.form_operation_map.get('10.1.2')(form_10_1_2,'I',tmp_handle)
          if not ret == 0:
             print("ERROR:configure rcv form 10.1.2 failed")
          rcv_obj.exit_menu(tmp_handle)
          subshl_obj.init_proc(tmp_handle,'SMI')
          subshl_obj.quit(tmp_handle)
          conn_handle.close()
          return 0

      def install_sll_spa_with_config(self,form_list):
          ret = self.sshObj.shell_scp(src_usr, src_ip, src_spa_path,src_password,
                                dest_usr,dest_ip,dest_spa_path,dest_password)
          if not ret == 0:
             print('ERROR:scp spa package to test lab failed')
             return 1

          conn_handle = self.sshObj.shell_ssh(dest_usr, dest_ip, dest_password)
          if conn_handle == None:
             print('ERROR:ssh to test lab failed')
             return 1

          file_path = spa_install_dir + "/.READY_TO_INSTALL_" + spa_name
          ret = self.sshObj.shell_remote_command(conn_handle, 'touch %s' % (file_path))
          if not ret == 0:
             print('ERROR:touch file %s failed' % (file_path))
             return 1

          subshl_obj = subshlObj()
          subshl_obj.set_connect_handle(conn_handle)
          (tmp_handle, need_close_handle, ret) = subshl_obj.subshl()
          if not ret == 0:
             print("ERROR:subshl failed")
             return 1

          ret = subshl_obj.install_config_spa(tmp_handle, spa_name)
          if not ret == 0:
             print("ERROR:subshl>install:config,spa=%s failed" % (spa_name))
             return 1
  
          rcv_obj = rcvObj()
          if not rcv_obj.rcv_menu(tmp_handle) == 0:
             print("ERROR:subshl>rcv:menu failed")
             return 1

          for form_value in form_list:
              ret = rcv_obj.form_operation_map.get('1.6')(form_value,'I',tmp_handle)
              if not ret == 0:
                 print("ERROR:configure rcv form 1.6 failed")
          rcv_obj.exit_menu(tmp_handle)

          ret = subshl_obj.install_proc_spa(tmp_handle, spa_name)
          if not ret == 0:
             print("ERROR:subshl>install:proc,spa=%s failed" % (spa_name))
             return 1

          ret = subshl_obj.rst_spa(tmp_handle, spa_name)
          if not ret == 0:
             print("ERROR:subshl>rst:spa=%s failed" % (spa_name))
             return 1

          if not rcv_obj.rcv_menu(tmp_handle) == 0:
             print("ERROR:subshl>rcv:menu failed")
             return 1
          ret = rcv_obj.form_operation_map.get('6.2.3')(form_6_2_3,'I',tmp_handle)
          if not ret == 0:
             print("ERROR:configure rcv form 6.2.3 failed")
          ret = rcv_obj.form_operation_map.get('10.1.2')(form_10_1_2,'I',tmp_handle)
          if not ret == 0:
             print("ERROR:configure rcv form 10.1.2 failed")
          rcv_obj.exit_menu(tmp_handle)
          subshl_obj.init_proc(tmp_handle,'SMI')
          subshl_obj.quit(tmp_handle)
          conn_handle.close()
          return 0
    
      def provision_with_simulator(self, data_file, simulator_path, conn, timeout=20):
          if conn == None:
             return (1,'')
          cmd = '%s -f %s' %(simulator_path, data_file)
          conn.sendline(cmd)
          ret = conn.expect(['SPA not in proper state', pexpect.TIMEOUT, pexpect.EOF],timeout)  
          ret_str = '%s%s' %(conn.before, conn.after)
          if ret == 0:
             ret = 2
          if ret == 1 and (ret_str.find('value Success') > 0 or ret_str.find('ErrorString:Success')>0):
             ret = 0
          if ret == 1 and (ret_str.find('DUPLICATE FORM') > 0):
             ret = 0
          print(ret_str)
          conn.sendline('\nquit')
          conn.expect([pexpect.EOF, pexpect.TIMEOUT])
          return (ret, ret_str)
