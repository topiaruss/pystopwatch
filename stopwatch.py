#!/usr/bin/env python3

import datetime
import getopt
import os
import pickle
import sys

times = {}
STORAGE = '/tmp/stopwatch.pickle'

CMD = 'stopwatch.py -mode <start|stop> -t <timername> -z'
DETAIL = """
Flexible timer for lazy programmers.
Stores times in /tmp pickle. Handy across multi-command scripting.

Russ Ferriday, 2016-11-05, russf@topia.com

Simple to use:

  ./stopwatch.py
  sleep 3
  ./stopwatch.py
  global           3s

Multiple overlapping steps:

  ./stopwatch.py
  sleep 3
  ./stopwatch.py -t lastphase
  sleep 4
  ./stopwatch.py

    global          7s
    lastphase       4s

Multiple sequential steps with global time:

  ./stopwatch.py
  sleep 3
  ./stopwatch.py -t step1
  sleep 4
  ./stopwatch.py -t step1 -m end
  ./stopwatch.py -t step2
  sleep 6
  ./stopwatch.py

    global         13s
    step1           4s
    step2           6s


  -t global // stops all, prints all, clears pickle
  
  -z just clears pickle.
  
"""


def is_running():
    return os.path.isfile(STORAGE)


def clear_storage():
    try:
        os.remove(STORAGE)
        print("removed the file %s" % STORAGE)
    except OSError as e:
        pass


def read_storage():
    return pickle.load(open(STORAGE, 'rb'))


def write_storage(data):
    pickle.dump(data, open(STORAGE, 'wb'))


def init_storage():
    clear_storage()
    write_storage({})


def now():
    return datetime.datetime.now()


def update_storage(key, mode='start'):
    data = read_storage()
    if key is not None:
        entry = data.setdefault(key, {'start': now()})
        if mode == 'end':
            entry.setdefault('end', now())
    write_storage(data)


def display():
    for k, entry in sorted(read_storage().items()):
        entry.setdefault('end', now())
        print("  {!s:<12} : {!s:>12}".format(k, entry['end'] - entry['start']))


def main(argv):
    timer = 'global'
    mode = 'start'
    zero = False

    try:
        opts, args = getopt.getopt(argv, "hm:t:z", ["mode=", "timer=", "zero"])
    except getopt.GetoptError:
        print(CMD)
        sys.exit(1)
    for opt, arg in opts:
        if opt == '-h':
            print(CMD)
            print(DETAIL)
            sys.exit()
        elif opt in ("-t", "--timername"):
            timer = arg
        elif opt in ("-m", "--mode"):
            mode = arg
        elif opt in ("-z", "--zero"):
            zero = True
    print('Timer :', timer)
    print('Mode:', mode)
    print('Zero:', zero)

    if mode not in ['start', 'end']:
        print('bad mode "%s", use start or end' % mode)
        sys.exit(1)

    if zero:
        clear_storage()
        sys.exit(0)

    if is_running():
        if timer == 'global':
            update_storage(None, 'end')
            display()
            clear_storage()
        else:
            update_storage(timer, mode)
    else:
        init_storage()
        update_storage('global', mode)

if __name__ == "__main__":
    main(sys.argv[1:])
