#!/usr/bin/env python
import sys
import re
import getpass
try:
    import requests
except ImportError:
    print 'requests module is required'
    print 'Install it and try again:sudo pip install requests'
    raise
from collections import OrderedDict, Counter
import random


group = sys.argv[2].upper()
username = sys.argv[1]
password = getpass.getpass("PRONTO Password: ")

server = 'eslpe00%s.emea.org-net.net'
url = "http://%s/org/pronto/pronto.nsf/(OpePRAtMbyID)?OpenView&Group=%s" % (
    server, group)
vpn_url = 'http://%s/org/pronto/pronto.nsf/0/%s?OpenDocument'
finalvpn_url = vpn_url + '&PUNID=%s'


pronto_name = re.compile('">(.+?)&nbsp;')
severe = re.compile('valign=top>(A|B|C) ')
org_pat = 'href="/[nN][oO][kK][iI][aA]/[pP]ronto/pronto.nsf/0/.+?'
person_sever = Counter()
assigned_persons = Counter()
ISUG = ['some_name_from_the_team',
        'some_other_name_from_the_team', 'third_name..']
new_prontos = []
Persons = {}


def get_pronto_server():
    global server
    for i in range(1, 4):
        try:
            r = requests.get(url % i, auth=(username, password), timeout=3)
        except requests.exceptions.Timeout:
            print '%s is unavailable at the moment.Trying next one...' % server % i
        else:
            server = server % i
            print 'Chose %s as pronto server' % server
            break

    return r, server


def get_pronto_ids(r):

    #: Get the request object of the page where all the prontos of Edradour are visible :#
    #: if the server is unavailable wait for 3 secs and then try another one :#
    #: Find all the pronto ids :#

    ids = re.findall(org_pat + ' ', r.content)
    severity = re.findall(
        r'<td valign=top>(A|B|C)(?=\s*&nbsp|\s*<img src="Customer.gif")', r.content)
    cnt = Counter(severity)
    #: name_sever dictionary holds the pronto names as keys and the severity as values :#
    global name_sever
    name_sever = OrderedDict()
    content = re.findall(org_pat + '.+', r.content)
    if not content:
        print 'Could not fetch any prontos '
        return 2
    _splited = content[0].split('OpenDocument')
    _splited.pop(0)
    for i in _splited:
        name_sever[pronto_name.search(i).group(1)] = severe.search(i).group(1)
    if ids:
        print 'Currently %s prontos in %s' % (len(ids), group)
        print
        print 'Critical:%s   Major:%s  Minor:%s' % (cnt['A'], cnt['B'], cnt['C'])
        print
        return ids
    else:
        print 'Found zero prontos assigned in Edradour'
        return 3


def get_pronto_page(pronto_id, server):

    global p_id
    global pronto_title
    global pr_severity
    try:
        p_id = re.search('/0/(.+)\?OpenDocument', pronto_id).group(1)
        if p_id:
            #:After we have the id get login into the specific pronto and parse the Corrections for Responsible Person :#
            r = requests.get(vpn_url % (server, p_id),
                             auth=(username, password))
            if r.reason == 'OK':
                pronto_title = re.search(
                    'name="PRMainTitle" type="hidden" value=.+PR .+?:(.+)>', r.content).group(1).strip('" ')
                pr_severity = re.search(
                    'PRSeverity" type="hidden" value="(A|B|C) - \w+', r.content).group(1).strip()
             # print 'Searching for correction task for %s ' %
             # ('\n'+pronto_title)
                corrections = re.search(
                    'SDInformation.+value=(.+)>', r.content).group(1).split(',')
                return corrections if '""' not in corrections else []
            else:
                print 'Could not get access into pronto page'

    except AttributeError:
        print 'Not found id in pronto list'
        raise


def parse_correction_tasks(correction_list, pronto_id, index, server):

    if correction_list:
        correction_ids = []
        print 'Found %s corrections tasks' % len(correction_list)
        for i in correction_list:
            # : -2 is for \xa characters :#
            correction_ids.append(i[1:i.find('&amp') - 2])
            try:
                r = requests.get(finalvpn_url % (server, correction_ids[
                                 0], pronto_id), auth=(username, password), timeout=5)
            except requests.exceptions.Timeout:
                print 'Could not fetch main pronto page for %s ' % pronto_title
                raise
            resp_pers = re.search('MCResp.+value=(.+)>',
                                  r.content).group(1).strip('"')
            #: in case there are 2 different responsible persons :#
            resp_persons = resp_pers.split(';')
            if 'E' in resp_persons:
                print '%s has correction task but empty responsible person!!!!' % pronto_title
                new_prontos.append(pronto_title)
            else:
                print
                print 'Pronto title: %s' % pronto_title
                print 'Responsible Person(s): %s' % resp_persons
                update_Persons_severity(index, resp_persons)
                check_RFT_task(correction_list, resp_persons)
            print
            print '=' * 50
            # : exit the loop as the correction tasks may be many,usually coordinated by the same person...#:
            break
    else:
        print "Found empty correction tasks for %s\nThis is a newly created pronto\n\n" % pronto_title
        new_prontos.append(pronto_title)


def update_Persons_severity(i, responsible_persons):
    """This function updates the global dictionary where is held as key the
       responsible user for each pronto,and as value the severity of the pronto.
    """
    tmp = [person.strip() for person in responsible_persons]
    responsible_persons = tmp[:]
    for person in set(responsible_persons):
        # if person in ISUG:

        if person not in Persons:
            Persons[person] = Counter()
            Persons[person][name_sever.values()[i]] += 1

        else:
            Persons[person][name_sever.values()[i]] += 1


def check_RFT_task(correction_list, responsible_persons):
    """this function checks for each pronto if there is a Ready for Testing task.
       If there is one,then the responsible person for this task is not excluded from 
       the potential users list,as we assume that he/she has already finished with
       analysis of the specific pronto and he/she can take a new one.
    """
    if 'Ready for Testing' in ''.join(correction_list):
        #:the resp person for this pronto will not be excluded :#
        pass
    else:
        for person in set(responsible_persons):
            assigned_persons[person] += 1


def keep_ISUG_prontos():
    """this function will keep only the new prontos that are related to ISUG only"""

    ISUG_prontos = [
        pronto for pronto in new_prontos if re.search('ISUG', pronto, re.I)]
    return ISUG_prontos


def distribute(pronto_list):

    print 'Found %s ISUG (new) prontos assigned to %s\n' % (len(pronto_list), group)

    if not pronto_list:
        return 4
    for new in pronto_list:
        potential_users = []
        for name in ISUG:
            if name in assigned_persons:
                pass
            else:
                potential_users.append(name)
        edradour_users = [user for user in potential_users if user in ISUG]
        if not edradour_users:
            print 'Edradour user list is exhausted.Loop over them again and choose randomly a person'
            edradour_users = ISUG[:]
        checking = random.choice(edradour_users)
        print '%s :\nProposal: %s' % (new, checking)
        assigned_persons[checking] += 1


def busy_loop(pronto_ids):
    """function that updates the global new_prontos list with the new prontos """

    for index, id in enumerate(pronto_ids):
        correction_tasks = get_pronto_page(id, server)
        parse_correction_tasks(correction_tasks, p_id, index, server)


def main():

    r, server = get_pronto_server()
    prontos = get_pronto_ids(r)
    busy_loop(prontos)
    prontos_to_check = keep_ISUG_prontos()
    distribute(prontos_to_check)


if '__main__' == __name__:

    sys.exit(main())
