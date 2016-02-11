#!/usr/bin/python

import urllib2
import sys
import re
from time import sleep
import smtplib
import ldap
from getpass import getuser as username
from email.mime.text import MIMEText


class Message(Exception):


    def __init__(self,*args):
        super(Message,self).__init__(*args)
        self.send_mail(*args)


    def send_mail(self,*args):
       
        """
        Function that will send out a descriptive message
        to me whether the iso succeded,or failed.
        """
        outgoing_message = args[0]
        if self.__class__ == SuccessIso:
            outgoing_message += '\n'+send_description()

      
        sender = find_sender(username())
        receivers = [sender] + [find_sender(people) for people in optional_people if optional_people]
        msg = MIMEText(outgoing_message)

        msg['Subject'] = 'ISO trigger...' 
        msg['From'] = sender
        msg['To'] = ','.join(receivers)
        s=smtplib.SMTP('localhost')
        s.sendmail(sender,[sender,','.join(receivers)],msg.as_string())
        s.quit()
        sys.exit()





class FatalError(Message):
    pass

class DownloadError(Message):
    pass

class ParsingError(Message):
    pass

class RevisionError(Message):
    pass

class NotCompletedError(Message):
    pass

class SuccessIso(Message):
    pass


def init_globals():


    global commited
    global url
    global timer
    global countdown 
    global branch
    global optional_people

    branch = str(sys.argv[1])
    commited = str(sys.argv[2])
    try:
        optional_people = sys.argv[3:]
    except IndexError:
        pass
    url='http://hugin.dev.cic.org-rdnet.net/scit/html/projects/ISO_'+branch+'_delivery_AB4/index.html'
    timer = 900 #15minutes
    countdown = 7200 #2hours

def validate():
    if len(sys.argv)<3:
        print 'Tool accepts 2 mandatory arguments'
        print 'The branch and the revision'
        sys.exit(2)

def find_sender(user):


    """
        Utility to find the mail address of the sender

    """



    l = ldap.open("ed-p-gl.emea.org-net.net")
    l.protocol_version=ldap.VERSION3
    baseDN = "o=org"
    searchScope = ldap.SCOPE_SUBTREE
    retrieveAttributes=None
    searchFilter= "uid="+str(user.strip())
    x= l.search(baseDN,searchScope,searchFilter,retrieveAttributes)
    res = l.result(x,0)
    l.unbind_s()
    return res[1][0][1].get('mail')[0]


def get_page(urlname):

    i=0    #number of retries until give up getting the page of scit
    while (i != 20): 
        try:
            resp = urllib2.urlopen(urlname).readlines()
        except urllib2.HTTPError as e:
            print e
            sleep(60)#wait 1 minute and retry again
            i+=1
        else:
            return resp

    raise DownloadError('Waited for 20 minutes until got no response from %s..\
                         \n\nUnable to download it for further parsing' % url)



def get_latest_triggered(resp):


    for line in resp:
        if 'Latest triggered revision' not in line:
            continue
        else:
            try:
                revision = re.search('Latest triggered revision.+/(\d{6})',\
                                      line).group(1)
            except:
                raise ParsingError('Found Latest triggered revision\
                                    but could not retrieve it...')
            else:
                return revision  

    raise ParsingError('Could not find at all \
                        Latest triggered revision')



def verify_triggered_equals_commited(triggered):

    """returns True if the revision 
       from which the latest ISO has been triggered
       is the same as the commited one"""

    return True if triggered == commited else False


def check_ISO_progress(url_response):
    
    """this function should run in a loop until the ISO ends.."""

    for line in url_response:
        if 'running' in line and 'abortbuild' not in line:
            print 'ISO has been started with  %s running...' % commited
            print 'Timer started for 15m' 
            sleep(timer) #sleep and wake up to check if it has completed
            print 'Woke up.Lets loop again'
            break    
        elif 'Latest completed revision' in line and 'success' in line and commited in line:
            raise SuccessIso('ISO has been successfully completed.')

        elif 'Latest completed revision' in line and 'failed' in line and commited in line:
            raise FatalError('ISO has failed!!\nSomeone to check manually!')


def get_page_and_triggered():


    """1)Fetch the url from scit
       2)Parse it to find the latest triggered revision
       3)Check if the current triggered is the same as 
         the recently commited
       4)Return the url page and the result of 3)"""

    
    page = get_page(url)

    latest_triggered_revision = get_latest_triggered(page)
 
    verified = verify_triggered_equals_commited(latest_triggered_revision)

    return verified,page




def wait_until_completion(page):

    """Loop that runs maximum up to 2h.
       During this timeframe the script sleeps
       for 15m and wakes up to check if the ISO
       has been completed"""


    global countdown
    while (countdown != 0):   

        check_ISO_progress(page)
        page = get_page(url)
        countdown -= timer #start gradually reducing by 15m the whole duration 2h...

    check_ISO_progress(page) #do one last check just in case...
    raise NotCompletedError('ISO has not completed in the usual timeframe...')



def send_description():

    """Finds the ISO name on success"""


    hugin = 'http://hugin.dev.cic.org-rdnet.net'
    for line in urllib2.urlopen(url):
        if 'Latest completed revision' in line and 'success' in line and commited in line:   
            success_link = re.search('href=("\/scit\/html\/ISO.+)>success',line).group(1).strip('"')
            success_link = hugin + success_link
            success_link = success_link.replace('.html','_log')
            success_link = success_link+'/'+re.search('AB4_(.+)_log',success_link).group(1)+'_3:ISO_delivery_'+branch+'_AB4_s1'

            for line in urllib2.urlopen(success_link):
                if 'Sending command: scp -v -t' in line:
                    iso_name = re.search('scp -v -t (.+)',line).group(1)
                    return iso_name
 


def fail_and_exit():


    """i believe its self documented"""

    raise FatalError('ISO should have been triggered with %s.Unknown fatal error' % commited)


def main():


    validate()

    init_globals()

    sleep(timer) # give some time for the command to be scheduled...

    is_triggered , page = get_page_and_triggered()


    if is_triggered:
        wait_until_completion(page)
    else:
        fail_and_exit()



if __name__ == '__main__':

    main()
