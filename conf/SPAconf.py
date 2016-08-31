#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#info of src host
#

import os


src_usr = 'nanaal'
src_ip = '127.0.0.1'
src_password = 'xxx'
#please modify spa path as following
src_spa_path = os.environ.get('COMMON_DIR) + '/lib/smispa.full.tar'


#
#info of dest host
#
dest_usr = 'xxx'
dest_ip = '135.0.0.1'
dest_password = 'xxx'
dest_spa_path = '/etc/SU'
dest_root_usr = 'root'
dest_root_password = 'xxx'

#
#info of spa
#
spa_install_dir = '/etc/SU'
spa_name = 'smispa'

#
#rcv form 10.1.2
#
form_10_1_2 = {'LOGICAL NAME':'smi_conf',
               'PROTOCOL':'SMI',
               'SERVICE HOST':'xxx.x.xxx.xxx',
               'SERVICE HOST 2':'',
               'SERVICE HOST 3':'',
               'SERVICE HOST 4':'',
               'SERVICE HOST 5':'',
               'SERVICE HOST 6':'',
               'eSM ID':'1',
               'PORT NUMBER':'8001',
               'IN OR OUT':'IN',
               'ALLOW DENY':'A'}

#
#rcv form 6.2.3
#
form_6_2_3 = {'PRIMARY CORBA HOST IP':'135.0.0.1',
              'SECONDARY CORBA HOST IP':'135.0.0.2',
              'CORBA PORT':'26435'}

#
#rcv form 1.6
form_1_6 = {'SPA NAME' : 'smispa',
            'NODE ID': '3',
            'START SERVER': 'Y',
            'NUMBER OF STANDARD CLIENTS' : '1',
            'NUMBER OF SPECIALIZED CLIENTS': '0'}
