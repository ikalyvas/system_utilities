#!/usr/bin/env python

import re
import sys
import itertools
import gzip
import os
from subprocess import Popen, STDOUT, PIPE

crit = re.compile(r'(?<=crit) (CLA-\d|AS\d+-\d|SAB\d+-\d|IB\d+-\d)')
err = re.compile(r'(?<=err) (CLA-\d|AS\d+-\d|SAB\d+-\d|IB\d+-\d)')
warn = re.compile(r'(?<=warn) (CLA-\d|AS\d+-\d)|SAB\d+-\d|IB\d+-\d')
info = re.compile(r'(?<=info) (CLA-\d|AS\d+-\d|SAB\d+-\d|IB\d+-\d)')
notice = re.compile(r'(?<=notice) (CLA-\d|AS\d+-\d|SAB\d+-\d|IB\d+-\d)')
debug = re.compile(r'(?<=debug) (CLA-\d|AS\d+-\d|SAB\d+-\d|IB\d+-\d)')
other_err = re.compile(r'(?<=err) (\w.+)')

#:it adjusts the scrolling page into your screen :#
#rows,colums = os.popen('stty size','r').read().split()

#:color db :#
red = '\033[91m'
white = '\033[97m'
yellow = '\033[93m'
cyan = '\033[94m'
green = '\033[92m'
pink = '\033[95m'


def write(_line, color=None):

    sys.stdout.write(color + _line + '' + '\n')
    sys.stdout.flush()


#: decide what is the file to monitor :#
def tail_lines(pipe):

    line = pipe.stdout.readline()
    if line == '':
        sys.exit(4)
    elif info.search(line):
        write(line, white)
    elif err.search(line):
        write(line, red)
    elif warn.search(line):
        write(line, yellow)
    elif notice.search(line):
        write(line, cyan)
    elif debug.search(line):
        write(line, green)
    elif other_err.search(line):
        write(line, red)
    elif crit.search(line):
        write(line, pink)
    else:
        pass


def print_lines():

    for next_lines in itertools.islice(f, 41):
        if next_lines:
            for line in next_lines.splitlines():
                if info.search(line):
                    print white + line + ''
                elif err.search(line):
                    print red + line + ''
                elif warn.search(line):
                    print yellow + line + ''
                elif notice.search(line):
                    print cyan + line + ''
                elif debug.search(line):
                    print green + line + ''
                elif other_err.search(line):
                    print red + line + ''
                elif crit.search(line):
                    print pink + line + ''
                else:
                    pass
        else:
            break


syslog = sys.argv[1]

try:
    if syslog == 'master-syslog':
        answer = raw_input(
            'For tail -f press y.\nOtherwise it will open master-syslog from the beginning:')
        if answer == 'y' or answer == 'Y':
            p = Popen('tail -f ' + syslog, shell=True,
                      stdout=PIPE, stderr=STDOUT)
            while True:
                try:
                    tail_lines(p)
                except KeyboardInterrupt:
                    sys.exit(2)
        else:
            f = open(syslog)
    else:
        if syslog.endswith('gz'):
            f = gzip.open(syslog, 'rb')
        else:
            f = open(syslog)

    while True:
        try:
            raw_input()
            print_lines()
        except KeyboardInterrupt:
            sys.exit(4)

except IOError:
    print 'File %s does not exist' % syslog
    sys.exit(3)
