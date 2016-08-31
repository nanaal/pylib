#!/usr/bin/env python
# -*- coding:utf-8 -*-

from conf.Gconf import *
import sys
sys.path.append(pexpect_lib_path)

import pexpect
import traceback
import commands

class shellObj(object):
       def __init__(self):
           self.login_str = ['password:',
                             'Last login',
                             'from station_c on ssh',#su root without password
                             'Are you sure you want to continue connecting (yes/no)?',
                             'WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!',
                             'Permission denied',
                             'Password:',
                             pexpect.EOF,
                             pexpect.TIMEOUT,
                             '100%']

       def shell_ssh(self, usr_name, ip, password):
           try:
              cmd_str = "ssh %s@%s" % (usr_name, ip)
              print(cmd_str)
              client = pexpect.spawn(cmd_str)
              while True:
                   index1 = client.expect(self.login_str)
                   print(client.before)
                   #print("index1=%d" %(index1))
                   if index1 == 0 or index1 == 6:
                      client.sendline(password)
                   elif index1 == 1 or index1 == 2:
                      return client
                   elif index1 == 3:
                      client.sendline('yes')
                   elif index1 == 4:
                      client.close()
                      self.shell_local_command('rm ~/.ssh/known_hosts') 
                      client = pexpect.spawn(cmd_str)
                   elif index1 == 5:
                      print("ERROR:Wrong password, please check the password and try again")
                      client.close()
                      return None
                   else:
                      client.close()
                      return None#error
           except Exception as e: 
              print e       
              return None
                 
       def shell_rm(self, ssh_client,parameters, file_or_directory_path):
           if ssh_client == None:
              print("ERROR:invailed connection, parameter ssh_client is None.")
              return 1
           ssh_client.sendline('rm %s %s; echo $?' % (parameters, file_or_directory_path))
           rm_str = ['rm: remove regular file "%s"?' % (file_or_directory_path),
                     'rm: remove regular empty file "%s"?' % (file_or_directory_path),
                     'rm: cannot remove "%s": Is a directory',
                     'rm: remove directory "%s"?' % (file_or_directory_path),
                     pexpect.EOF,
                     pexpect.TIMEOUT,
                     '(yes/no)']
           index1 = ssh_client.expect(rm_str)
           print(ssh_client.before)
           if index1 == 2:
              print("ERROR:If you would like to delete this directory, please make sure parameters's value contains '-r'")
              return 1
           elif index1 == 4 or index1 == 5:
              print("ERROR:unexpect error occured, please check it and try again")
              return 1
           else:
              ssh_client.sendline('yes')
           return 0

       def shell_local_command(self,command_str):
           (status,output) = commands.getstatusoutput(command_str)
           print(output)
           return status
 
       def shell_remote_command(self, ssh_client, command_str,timeout=20):
           if ssh_client == None:
              print("ERROR:invailed connection, parameter ssh_client is None.")
              return 1
           ssh_client.sendline(' %s && echo "shell_remote_command successfully"' % (command_str))
           index1 = ssh_client.expect(['shell_remote_command', pexpect.TIMEOUT, pexpect.EOF],timeout)
           print('%s%s' % (ssh_client.before,ssh_client.after))
           if index1 == 0:
              return 0
           else:
              return 1

       def shell_scp(self, src_usr, src_ip, src_file_ab_path, src_password, dest_usr, dest_ip, dest_ab_path, dest_password):
           cmd_str = "scp %s@%s:%s %s@%s:%s" % (src_usr, src_ip, src_file_ab_path, dest_usr, dest_ip, dest_ab_path)
           print(cmd_str)
           scp_conn = pexpect.spawn(cmd_str)
           while True:
              index1 = scp_conn.expect(self.login_str)
              print('%s%s' % (scp_conn.before,scp_conn.after))
              if index1 == 0 or index1 == 6:
                 if not scp_conn.before.find('%s@%s' %(dest_usr,dest_ip)):
                    scp_conn.sendline(src_password)
                 else:
                    scp_conn.sendline(dest_password)
              elif index1 == 3:
                 scp_conn.sendline('yes')
              elif index1 == 4:
                 scp_conn.close()
                 self.shell_local_command('rm ~/.ssh/known_hosts')
                 scp_conn = pexpect.spawn(cmd_str)
              elif index1 == 9:
                 scp_conn.close()
                 return 0
              else:
                scp_conn.close()
                return 1
      
       def shell_su(self, usr, password, conn_handle): 
           if conn_handle == None:
              return 1 
           conn_handle.sendline('su %s;echo $?' % (usr))
           index1 = conn_handle.expect_exact(['Password',pexpect.EOF,pexpect.TIMEOUT],2)
           if not index1 == 0:
              return 1
           conn_handle.sendline(password)
           index1 = conn_handle.expect_exact(['0','Authentication failure',pexpect.EOF,pexpect.TIMEOUT])
           if index1 == 0:
              return 0
           else:
              return 1
