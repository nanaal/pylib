import sys,time,re,traceback

import pexpect,pexpect.pxssh

# Functions that easy for you to print out some messages 
def log_warn(message_):
    print ''
    print '-'*30 + ' WARNING ' + '-'*30
    print message_
    print '-'*30 + ' WARNING ' + '-'*30
    print ''

def log_error(message_):
    print ''
    print '+'*30 + ' ERROR ' + '+'*30
    print message_
    print '+'*30 + ' ERROR ' + '+'*30
    print ''

def log_info(message_):
    print ''
    print '='*30 + ' INFO ' + '='*30
    print message_
    print '='*30 + ' INFO ' + '='*30
    print ''


class CommonFunc(pexpect.pxssh.pxssh):
    def __init__(self,labname,usr='',pwd='',port=''):
        super(CommonFunc,self).__init__(timeout=30, maxread=2000, searchwindowsize=None, logfile=None, cwd=None, env=None)
        self.labname_ = labname
        self.usr_ = usr
        self.pwd_ = pwd
        self.port_ = port
        self.log_file('all')

    # Determine what kind of logs to show on the screen. For debug or something.
    # All: print out the commands sent by user, and results delivered by lab
    # Read: Only results
    # Send: Only commands sent by user
    # None: Nothing to display
    def log_file(self, rcd = 'read'):
        logtype = ['all', 'read', 'send','none']
        ind = logtype.index(rcd)
        self.logfile = None
        self.logfile_read = None
        self.logfile_send = None
        if ind == 0:
            self.logfile = sys.stdout
        elif ind == 1:
            self.logfile_read = sys.stdout
        elif ind == 2:
            self.logfile_send = sys.stdout
        elif ind == 3:
            pass
        else:
            log_warn('Cannot recognize input parameter, set to default (read)')
            self.logfile_read = sys.stdout

    # To expect the command prompt
    # Second parametre is timeout, 30s by default if not specified
    def prompt(self,timeout=-1):
        if timeout == -1:
            timeout = self.timeout
        ind = self.expect([self.PROMPT,pexpect.TIMEOUT], timeout=timeout)
        if ind == 0:
            return True
        elif ind == 1:
            promptE = pexpect.TIMEOUT('Timeout exceeded.'+'\n'+str(self))
            raise promptE
        else:
            return False

    # Send commands to lab and expect the prompt
    # A combination of "sendline -> prompt"
    def sendppt(self,command_='',timeout=-1):
        try:
            self.sendline(command_)
            self.prompt(timeout)
        except Exception as e:
            log_error(traceback.format_exc())
            return False
        return True

    # log onto a lab, configured in global.py
    def ssh_lab(self):
        try:
            if self.usr_:
                self.login(self.labname_,self.usr_,self.pwd_[0],
                           port=self.port_,original_prompt='[#$>]')
            else:
                self.force_password = False
                self.login(self.labname_,'root',original_prompt='[#$>]')
            self.sendline('stty -echo')
            self.prompt()
        except Exception as e:
            log_error(traceback.format_exc())
            return False
        return True
    
    # Switch user to root
    def su_root(self):
        try:
            self.sendline('su -')
            self.waitnoecho()
            self.sendline(self.pwd_[1])
            self.set_unique_prompt()
            self.sendline()
            self.prompt()
            self.sendline('stty -echo')
            self.prompt()
        except Exception as e:
            log_error(traceback.format_exc())
            return False
        return True

    # It might be a good habit to logout when all finish.
    def ssh_logout(self):
        self.expect('.*')
        self.sendline('whoami')
        index1 = self.expect(['root','ainet',pexpect.TIMEOUT])
        if index1 == 0:
            self.sendline('exit')
            self.prompt()
        self.logout()
        if not self.isalive():
            return True
        return False
    
    # scp from local to lab
    # scp_putfile(local_filepath,destination_filepath)
    # Example: "self.scp_putfile("/u/user/imperial.py","/u/ainet/"
    def scp_putfile(self, filename, des_dir):
        try:
            self.scp_child = pexpect.spawn('scp -P %s %s %s@%s:%s'
                              %(self.port_,filename,self.usr_,
                              self.labname_, des_dir))
            index1 = self.scp_child.expect(['yes/no','(?i)password'])
            if index1 == 0:
                self.scp_child.sendline('yes')
                self.scp_child.expect('(?i)password')
            self.scp_child.sendline(self.pwd_[0])
            index2 = self.scp_child.expect(['100%','(?i)permission denied','(?i)password',
                                            '(?i)error',pexpect.TIMEOUT],timeout=3600)
            if index2 == 0:
                 log_info(' File %s has been copied to %s successfully '%(filename,self.labname_))
            elif index2 == 1:
                log_error(' No permission or error login/pwd, please check')
                return False
            elif index2 == 2:
                log_error(' Error login/pwd, please check')
                return False
            elif index2 == 3:
                log_error(' Error: scp file %s transfer error'%filename)
                return False
            elif index2 == 4:
                log_error(' Error: scp file %s timeout'%filename)
                return False
            time.sleep(3)
        except Exception, e:
            log_error(traceback.format_exc())
            return False
        finally:
            if not self.scp_child.terminate():
                return False
        return True
    
    # Go into rcv
    # If user want to insert an item in 1.6:
    # self.rcv_in("1.6","I")
    def rcv_in(self, path_, action_):
        try:
            self.sendline('subshl')
            self.expect('<')
            self.sendline('rcv:menu')
            self.expect('->')
            self.sendline(path_)
            self.expect('Enter Database Operation')
            self.sendline(action_)
            self.expect('ALCATEL-LUCENT NETWORK ELEMENT')
        except Exception, e:
            log_error(traceback.format_exc())
            return False
        return True

    # Reverse action
    def rcv_out(self):
        try:
            self.sendline('<')
            self.expect('->')
            self.sendline('!')
            self.expect('<')
            self.sendline('quit')
            self.prompt()
        except Exception, e:
            log_error(traceback.format_exc())
            return False
        return True
    
    # Literal meaning.
    # Example: self.install_spa("/u/ainet/svc-jappdemo-1.full.tar","jappdemo1",[3,4])
    # install_spa(filepath,spaname,<SPMAN SPA NODE FORM>, <Sync all to all nodes>)
    def installConfig_spa(self, filepath, spaname):
        try:
            self.sendline('tar -xvf %s -C /etc/SU'%filepath)

            index1 = self.expect(['(?i)error',self.PROMPT])
            if index1 == 0:
                log_error(' Error: Failed to untar spa file!')
                return False

            self.sendline('subshl')
            self.expect('<')
            self.sendline('install:config,spa=%s'%spaname)
            index2 = self.expect(['FAILED',
                      'CONFIG SPA INSTALLATION COMPLETE'],timeout=120)
            if index2 == 0:
                log_error(' Error: Failed to install spa config!')
                return False
            
            self.sendline('quit')
            self.prompt()
        except Exception, e:
            log_error(traceback.format_exc())
            return False
        return True

    def installProc_spa(self,spaname,node_id=[],sync_=True):
        try:
            if node_id:
                if not self.rcv_in('1.6', 'I'):
                    return False
                for node_ in node_id:
                    self.sendline(spaname)
                    self.sendline(str(node_))
                    self.sendline('N')
                    self.sendline()
                    self.sendline()
                    self.expect('Enter Insert')
                    self.sendline('I')
                    self.expect('Enter name of the SPA')
                if not self.rcv_out():
                    return False

            if sync_:
                self.sendline('PlatformSync /sn/sps/%s/bin/ all'%spaname)
                self.prompt()

            self.sendline('subshl')
            self.expect('<')
            self.sendline('install:proc,spa=%s'%spaname)
            index3 = self.expect(['FAILED','COMPLETE'],timeout=120)
            if index3 == 0:
                log_error(' Error: Failed to install spa proc!')
                return False
        except Exception, e:
            log_error(traceback.format_exc())
            return False
        return True

    def rst_spa(self,spaname):
        try:
            self.sendline('rst:spa=%s'%spaname)
            index4 = self.expect(['FAILED','COMPLETED SUCCESSFULLY'],timeout=120)
            if index4 == 0:
                log_error(' Error: Failed to start spa!')
                return False

            self.sendline('quit')
            self.prompt()
        except Exception, e:
            log_error(traceback.format_exc())
            return False
        return True

    def install_spa(self, filepath, spaname,node_id=[],sync_=True):
        if self.installConfig_spa(filepath,spaname) and \
           self.installProc_spa(spaname,node_id,sync_) and \
           self.rst_spa(spaname):
               return True
        else:
            return False

    # Uninstall spa, needs to specified the name
    def delete_spa(self, spaname):
        try:
            self.sendline('subshl')
            self.expect('<')
            self.sendline('rmv:spa=%s'%spaname)
            self.expect('Y OR N')
            self.sendline('Y')
            index1 = self.expect(['FAILED','COMPLETED SUCCESSFULLY'],timeout=120)
            if index1 == 0:
                log_error(' Error: Failed to remove spa!')
                return False

            self.sendline('delete:proc,spa=%s'%spaname)
            self.expect('Y OR N')
            self.sendline('Y')
            index2 = self.expect(['FAILED','COMPLETED SUCCESSFULLY'],timeout=120)
            if index2 == 0:
                log_error(' Error: Failed to delete spa proc!')
                return False

            self.sendline('delete:config,spa=%s'%spaname)
            self.expect('Y OR N')
            self.sendline('Y')
            index3 = self.expect(['FAILED','SPA DELETION COMPLETE'],timeout=120)
            if index3 == 0:
                log_error(' Error: Failed to delete spa config!')
                return False

            self.sendline('quit')
            self.prompt()
        except Exception as e:
            log_error(traceback.format_exc())
            return False
        return True
    
    # init a process, can also specify the machine.
    def init_proc(self,proc_name,machine_name=''):
        try:
            if machine_name:
                machine_name = 'MACHINE=' + machine_name

            log_info('Now init %s via init:proc=%s,level=1,ucl,%s'
                      %(proc_name,proc_name,machine_name))
            self.sendline('subshl')
            self.expect('<')
            self.sendline('init:proc=%s,level=1,ucl,%s'%(proc_name,machine_name))
            index1 = self.expect(['DOES NOT EXIST','SUCCESSFULLY ACKNOWLEDGED'])
            if index1 == 0:
                log_error('ERROR! proc %s does not exist! '%proc_name +
                          'Please log in lab and check proc %s'%proc_name)
                return False
            elif index1 == 1:
                log_info('init %s SUCCESSFULLY ACKNOWLEDGED'%proc_name)

            time.sleep(20)
            self.expect('<')
            self.sendline('op:init,proc=%s,%s'%(proc_name,machine_name))
            self.expect('STEADY')
            log_info('%s initialized SUCCESSFULLY,%s'%(proc_name,machine_name))
            self.sendline('quit')
            self.prompt()
        except Exception as e:
            log_error(traceback.format_exc())
            return False
        return True

    # Check if the file exist. Return True or False
    def file_exist(self,filename):
        try:
            self.sendline('ls %s'%filename)
            index = self.expect(['No such file',
                                 '(?m)^%s\r$'%filename],timeout=120)
            print self.after
            self.prompt()
            if index == 0:
                log_error('%s: No such file!'%filename)
                return False
            self.sendline()
            self.prompt()
        except Exception as e:
            log_error(traceback.format_exc())
            return False
        return True

    # Check if the corefile exists for a specified process. Return True or False
    def is_core_exist(self, procname):
        try:
            self.sendline('stty -echo')
            self.prompt()
            self.sendline('ls /sncore/%s'%procname)
            print 'ls /sncore/%s'%procname
            index = self.expect(['cannot access',self.PROMPT,'core','debug'])
            self.sendline('stty echo')
            self.prompt()
            if index == 0 or index == 1:
                log_info('No coredump')
            elif index == 2 or index == 3:
                log_error('Coredump exists!')
                return False
        except Exception as e:
            log_error(traceback.format_exc())
            return False
        return True

    # set:runlvl=100. Can accept machine name.
    def start_proc(self, machine_name=''):
        try:
            if machine_name:
                machine_name = 'MACHINE=' + machine_name
            self.sendline('subshl')
            self.expect('<')
            self.sendline('set:runlvl=100,%s'%machine_name)
            self.expect('SET RUNLVL=100 (%s )?COMPLETED'%machine_name)
            log_info('set:runlvl=100 %s finished.'%machine_name)
            self.sendline('quit')
            self.prompt()
        except Exception as e:
            log_error(traceback.format_exc())
            return False
        return True
    
    # inh and init a process. Can accept machine name.
    def stop_proc(self,procname,machine_name=''):
        try:
            if machine_name:
                machine_name = 'MACHINE=' + machine_name
            log_info('Now stop %s via inh:restart and init:proc=%s,\
                      level=1,ucl,%s'.replace('  ','')
                        %(procname,procname,machine_name))
            self.sendline('subshl')
            self.expect('<')
            self.sendline('inh:restart,proc=%s,%s'
                                %(procname,machine_name))
            index1 = self.expect(['INH RESTART PROC=%s (%s )?COMPLETED'
                                       %(procname,machine_name),'FAILED'])
            if index1 == 0:
                log_info('inh:restart,proc=%s,%s successful'
                         %(procname,machine_name))
            elif index1 == 1:
                log_error('inh:restart,proc=%s,%s failed!'
                          %(procname,machine_name))
                return False
            time.sleep(1)

            self.sendline('init:proc=%s,level=1,ucl,%s'
                                %(procname,machine_name))
            index2 = self.expect(['DOES NOT EXIST','SUCCESSFULLY ACKNOWLEDGED'])
            if index2 == 0:
                log_error('ERROR! proc %s does not exist!'%procname)
                return False
            elif index2 == 1:
                log_info('init %s SUCCESSFULLY ACKNOWLEDGED %s'%(procname,machine_name))
            self.sendline('quit')
            self.prompt()
        except Exception as e:
            log_error(traceback.format_exc())
            return False
        return True

    # Check the owner of a file. or directory.
    # Example: self.check_owner("/tmp/what","ainet:ainet")
    def check_owner(self,filename,owner):
        try:
            self.sendline('[[ -d %s ]]'%filename)
            self.prompt()
            self.sendline('echo result$?')
            index1 = self.expect(['result0','result1'])
            self.prompt()
            if index1 == 0:
                ownership = "ls -ltrd %s | awk '{print $3 \":\" $4}'"%filename
            elif index1 == 1:
                ownership = "ls -ltr %s | awk '{print $3 \":\" $4}'"%filename
            self.sendline(ownership)
            index2 = self.expect([owner,'No such file or directory',pexpect.TIMEOUT])
            print self.after
            self.prompt()
            if index2 == 0:
                pass
                #log_info('%s owner is correct!'%filename)
            elif index2 == 1:
                log_error('%s does not exist! Please check!'%filename)
                return False
            elif index2 == 2:
                log_error('TIMEOUT! %s owner is wrong!'%filename)
                return False
            self.sendline()
            self.prompt()
        except Exception as e:
            log_error(traceback.format_exc())
            return False
        return True

    # Check file or directory permission.
    # Example: self.check_permission("/tmp/what","755")
    def check_permission(self,filename,permission):
        try:
            self.sendline('[[ -d %s ]]'%filename)
            self.prompt()
            self.sendline('echo result$?')
            index1 = self.expect(['result0','result1'])
            self.prompt()
            perm_dict = {'0':'---','1':'--x','2':'-w-','4':'r--','5':'r-x','6':'rw-','7':'rwx'}
            perm_raw=''
            for i in permission:
                perm_raw += perm_dict[i]
            if index1 == 0:
                permfile = "ls -ltrd %s | awk '{print $1}'"%filename
            elif index1 == 1:
                permfile = "ls -ltr %s | awk '{print $1}'"%filename
            self.sendline(permfile)
            index2 = self.expect([perm_raw,'No such file or directory',pexpect.TIMEOUT])
            print self.after
            self.prompt()
            if index2 == 0:
                pass
                #log_info('%s permission is correct!'%filename)
            elif index2 == 1:
                log_error('%s does not exist! Please check!'%filename)
                return False
            elif index2 == 2:
                log_error('TIMEOUT! %s owner is wrong!'%filename)
                return False
            self.sendline()
            self.prompt()
        except Exception as e:
            log_error(traceback.format_exc())
            return False
        return True

    def chk_rtn(self):
        self.sendline('echo $?')
        rtn = self.expect(['0','\d'])
        self.prompt()
        if rtn == 0:
            return True
        else:
            return False

    def run_case(self,caseSet):
        casePattern = re.compile(r'[a-zA-Z]{2}\d{4}')
        for i in caseSet:
            if casePattern.findall(i):
                caseFunc = 'self.' + i + '()'
                exec 'ret = %s'%caseFunc
                self.JenkinsReport(ret,i)

    def JenkinsReport(self,ret,caseNum):
        print
        if ret:
            print '__AUTOTEST__:COMMON_COMMON_%s@1:Pass'%caseNum
        else:
            print '__AUTOTEST__:COMMON_COMMON_%s@1:Fail'%caseNum
        print

