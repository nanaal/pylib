#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

from conf.Gconf import *
import sys
sys.path.append(pexpect_lib_path)
import pexpect

from shellObj import shellObj

class rcvObj(object):
      def __init__(self):
          self.form_operation_map = {'6.2.3':self.form623,
                                     '10.1.2':self.form1012,
                                     '1.6':self.form16}
          self.form623_items = ['PRIMARY CORBA HOST IP','SECONDARY CORBA HOST IP','CORBA PORT']
          self.form1012_items = ['LOGICAL NAME','PROTOCOL','SERVICE HOST','SERVICE HOST 2',
                                 'SERVICE HOST 3','SERVICE HOST 4','SERVICE HOST 5','SERVICE HOST 6',
                                 'eSM ID','PORT NUMBER','IN OR OUT','ALLOW DENY']
          self.form16_items = ['SPA NAME','NODE ID','START SERVER','NUMBER OF STANDARD CLIENTS',
                              'NUMBER OF SPECIALIZED CLIENTS']

      def rcv_menu(self, conn_handle):
          if conn_handle == None:
             return 1
          conn_handle.sendline('rcv:menu')
          index1 = conn_handle.expect_exact(['Enter view', pexpect.EOF, pexpect.TIMEOUT])
          print("%s%s" % (conn_handle.before, conn_handle.after))
          if not index1 == 0:
             return 1
          return 0

      def exit_menu(self, conn_handle):
          if conn_handle == None:
             return 1
          conn_handle.sendline('!')
          index1 = conn_handle.expect_exact(['<', pexpect.EOF, pexpect.TIMEOUT])
          print('%s%s' % (conn_handle.before,conn_handle.after))
          if not index1 == 0:
             print("ERROR:exit_menu failed")
             return 1
          return 0

      def form(self,form_num_str,value_map,operation_str, conn_handle):
          form_handle = self.form_operation_map.get(form_num_str, None)
          if form_handle == None:
             print("ERROR:form %s functions is not found" % (form_num_str))
             return 1
          return form_handle(value_map,operation_str,conn_handle) 

      def form623(self, value_map, operation_str, conn_handle):
          if conn_handle == None:
             return 1
          conn_handle.sendline('6.2.3')
          index1 = conn_handle.expect(['Enter Database Operation', pexpect.EOF, pexpect.TIMEOUT])
          print('%s%s' % (conn_handle.before, conn_handle.after))
          if not index1 == 0:
             return 1
          try:
             oper_str = operation_str.lower()
             ret = 1
             if oper_str == 'i' or oper_str == 'insert':
                ret = self.__form623_insert(value_map, conn_handle)
             elif oper_str == 'd' or oper_str == 'delete':
                ret = self.__form623_delete(value_map, conn_handle)
             elif oper_str == 'qr' or oper_str == 'queryr':
                ret = self.__form623_query(value_map,conn_handle)
             else:
                print('ERROR:not support operation %s' % (operation_str))
             conn_handle.sendline('<\n<\n<')
             return ret
          except Exception as e:
             print e
             return 1

      def __form623_insert(self, value_map, conn_handle):
          conn_handle.sendline('I')
          for item_id in range(0, len(self.form623_items)):
              index1 = conn_handle.expect_exact([self.form623_items[item_id], 
                                                'DUPLICATE',
                                                pexpect.EOF, pexpect.TIMEOUT])
              print('%s%s' % (conn_handle.before,conn_handle.after))
              if index1 == 1:
                 print("ERROR:DUPLICATE FORM")
                 return 1
              elif not index1 == 0:
                 return 1
              if value_map.has_key(self.form623_items[item_id]):
                 conn_handle.sendline(value_map.get(self.form623_items[item_id]))
              else:
                 conn_handle.sendline('')
          index1 = conn_handle.expect_exact(['Enter Insert, Change, Edit, Validate, or Print', pexpect.EOF, pexpect.TIMEOUT])
          print('%s%s' % (conn_handle.before,conn_handle.after))
          if not index1 == 0:
             return 1
          conn_handle.sendline('I')
          index1 = conn_handle.expect_exact(['FORM INSERTED',pexpect.EOF, pexpect.TIMEOUT])
          print('%s%s' % (conn_handle.before,conn_handle.after))
          if not index1 == 0:
             return 1
          conn_handle.sendline('<')
          index1 = conn_handle.expect_exact(['>',pexpect.EOF, pexpect.TIMEOUT])
          print('%s%s' % (conn_handle.before,conn_handle.after))
          if not index1 == 0:
             return 1
          else:
             return 0
          
      def __form623_delete(self, value_map, conn_handle):
          print("Note:will implement later")
          return 1     

      def __form623_query(self,value_map,conn_handle):
          print("Note:will implement later")
          return 1 
     
      def form1012(self,value_map, operation_str, conn_handle):
          if conn_handle == None:
             return 1
          conn_handle.sendline('10.1.2')
          index1 = conn_handle.expect_exact(['Enter Database Operation', pexpect.EOF, pexpect.TIMEOUT])
          print('%s%s' % (conn_handle.before,conn_handle.after))
          if not index1 == 0:
             return 1
          try:
             oper_str = operation_str.lower()
             ret = 1
             if oper_str == 'i' or oper_str == 'insert':
                ret = self.__form1012_insert(value_map, conn_handle)
             elif oper_str == 'd' or oper_str == 'delete':
                ret = self.__form1012_delete(value_map, conn_handle)
             elif oper_str == 'qr' or oper_str == 'queryr':
                ret = self.__form1012_query(value_map,conn_handle)
             else:
                print("ERROR:not support operation %s" % (operation_str))
             conn_handle.sendline('<\n<\n<')
             return ret
          except Exception as e:
             print e
             return 1 

      def __form1012_insert(self, value_map, conn_handle):
          conn_handle.sendline('I')
          for ite_id in range(0, len(self.form1012_items)):
              item_name = self.form1012_items[ite_id]   
              index1 = conn_handle.expect_exact([item_name,pexpect.EOF,pexpect.TIMEOUT,
                                                 'DUPLICATE FORM'])
              print('%s%s' % (conn_handle.before,conn_handle.after))
              if index1 == 3:
                 print("ERROR:DUPLICATE FORM")
                 return 1
              elif not index1 == 0:
                 return 1
              if value_map.has_key(item_name):
                 conn_handle.sendline(value_map.get(item_name))
              else:
                 conn_handle.sendline('')
          index1 = conn_handle.expect_exact(['Enter Insert, Change, Edit, Validate, screen#, or Print', pexpect.EOF, pexpect.TIMEOUT])
          print('%s%s' % (conn_handle.before,conn_handle.after))
          if not index1 == 0:
             return 1
          conn_handle.sendline('I')
          eSM_id_str = value_map.get('eSM ID', '-1')
          eSM_id = int(eSM_id_str)
          while True:
             index1 = conn_handle.expect_exact(['FORM INSERTED','error',pexpect.EOF, pexpect.TIMEOUT])
             print('%s%s' % (conn_handle.before,conn_handle.after))
             if index1 == 0:
                conn_handle.sendline('<')
                index1 == conn_handle.expect_exact(['>', pexpect.EOF,pexpect.TIMEOUT])
                print('%s%s' % (conn_handle.before,conn_handle.after))
                if index1 == 0:
                   return 0
                else:
                   return 1
             elif index1 == 1:
                conn_handle.sendline('')
                index1 = conn_handle.expect_exact(['ESM_ID is already used',pexpect.EOF,pexpect.TIMEOUT])
                print('%s%s' % (conn_handle.before,conn_handle.after))
                if not index1 == 0:
                   return 1
                conn_handle.sendline('')
                index1 = conn_handle.expect_exact(['Enter Insert, Change, Edit, Validate, screen#, or Print',
                                                   pexpect.EOF,pexpect.TIMEOUT])
                print('%s%s' % (conn_handle.before,conn_handle.after))
                if not index1 == 0:
                   return 1
                eSM_id = eSM_id + 1
                if eSM_id <1 or eSM_id > 99:
                   print("ERROR:invalid value(%d) of eSM_id" % (eSM_id))
                   return 1
                conn_handle.sendline('Change')
                index1 = conn_handle.expect_exact(['Change field',pexpect.EOF,pexpect.TIMEOUT])
                print('%s%s' % (conn_handle.before,conn_handle.after))
                if not index1 ==0:
                   return 1
                conn_handle.sendline('9')
                index1 = conn_handle.expect_exact(['eSM ID',pexpect.EOF,pexpect.TIMEOUT])
                print('%s%s' % (conn_handle.before,conn_handle.after))
                if not index1 == 0:
                   return 1
                conn_handle.sendline(str(eSM_id))
                index1 = conn_handle.expect_exact(['Change field',pexpect.EOF,pexpect.TIMEOUT])
                if not index1 == 0:
                   return 1
                conn_handle.sendline('')
                index1 = conn_handle.expect_exact(['Enter Insert, Change, Edit, Validate, screen#, or Print',
                                                   pexpect.EOF,pexpect.TIMEOUT])
                if not index1 == 0:
                   return 1
                conn_handle.sendline('I')
             else:
                return 1
          
      def __form1012_delete(self, value_map,conn_handle):
          print("Note:delete form 10.1.2 will implement later")
          return 1
 
      def __form1012_query(self,value_map,conn_handle):
          print("Note:query form 10.1.2 will implement later")
          return 1

      def form16(self, value_map, operation_str, conn_handle):
          if conn_handle == None:
             return 1
          conn_handle.sendline('1.6')
          index1 = conn_handle.expect_exact(['Enter Database Operation', pexpect.EOF, pexpect.TIMEOUT])
          print('%s%s' % (conn_handle.before, conn_handle.after))
          if not index1 == 0:
             return 1
          try:
             oper_str = operation_str.lower()
             ret = 1
             if oper_str == 'i' or oper_str == 'insert':
                ret = self.__form16_insert(value_map, conn_handle)
             elif oper_str == 'd' or oper_str == 'delete':
                ret = self.__form16_delete(value_map, conn_handle)
             elif oper_str == 'qr' or oper_str == 'queryr':
                ret = self.__form16_query(value_map,conn_handle)
             else:
                print('ERROR:not support operation %s' % (operation_str))
             conn_handle.sendline('<\n<\n<')
             return ret
          except Exception as e:
             print e
             return 1

      def __form16_insert(self,value_map,conn_handle):
          conn_handle.sendline('I')
          for ite_id in range(0, len(self.form16_items)):
              item_name = self.form16_items[ite_id]
              index1 = conn_handle.expect_exact([item_name,pexpect.EOF,pexpect.TIMEOUT,
                                                 'DUPLICATE FORM'])
              print('%s%s' % (conn_handle.before,conn_handle.after))
              if index1 == 3:
                 print("ERROR:DUPLICATE FORM")
                 return 0
              elif not index1 == 0:
                 return 1
              if value_map.has_key(item_name):
                 conn_handle.sendline(value_map.get(item_name))
              else:
                 conn_handle.sendline('')
          index1 = conn_handle.expect_exact(['Enter Insert, Change, Edit, Validate, or Print:', pexpect.EOF, pexpect.TIMEOUT])
          print('%s%s' % (conn_handle.before,conn_handle.after))
          if not index1 == 0:
             return 1
          conn_handle.sendline('I')
          index1 = conn_handle.expect_exact(['FORM INSERTED',pexpect.EOF, pexpect.TIMEOUT])
          print('%s%s' % (conn_handle.before,conn_handle.after))
          if not index1 == 0:
             return 1
          conn_handle.sendline('<')
          index1 = conn_handle.expect_exact(['>',pexpect.EOF, pexpect.TIMEOUT])
          print('%s%s' % (conn_handle.before,conn_handle.after))
          if not index1 == 0:
             return 1
          else:
             return 0
          

      def __form16_delete(self,value_map,conn_handle):
          print("Note:delete form 1.6 will implement later")
          return 1

      def __form16_query(self,value_map,conn_handle):
          print("Note:query form 1.6 will implement later")
          return 1

