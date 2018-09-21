# -*- encoding: utf8 -*-
""" common library """

from __future__ import print_function
from __future__ import division

from past.builtins import cmp
from builtins import object

__author__ = 'gpanda'

import datetime
import re
import time

SEC_ID_PATTERN_STRING = "^\d{6}$"
SEC_ID_PATTERN = re.compile(SEC_ID_PATTERN_STRING)

class Security(object):
    """Security data structure
    """

    def __init__(self, secId, name=None, time=None, price=float(0),
                 volume=float(0), nav=float(1)):
        """Initialize Security object

        :param secId: security id
        :param name: name
        :param time: data timestamp
        :param price: security price
        :param volume: exchange volume (unit: 0.1 billion)
        :param nav: security (fund) net asset value or book value

        """
        self.secId = secId
        self.name = name
        self.time = time
        self.price = price
        self.volume = volume
        self.nav = nav
        self.pbr = self.price / self.nav

    def __cmp__(self, other):
        return cmp(self.pbr, other.pbr)


def is_sec_id(chars):
    return SEC_ID_PATTERN.match(chars)

def valid_deal_time(interval=0):
   now = datetime.datetime.now()
   deal_start = now.replace(hour=9, minute=30, second=0)
   deal_end = now.replace(hour=15, minute=0, second=0) + \
       datetime.timedelta(seconds=interval)
   if now < deal_start or now >= deal_end:
       return False
   w = now.isoweekday()
   if w < 1 or w > 5:
       return False
   return True

def noon_break(interval=0):
    now = datetime.datetime.now()
    break_start = now.replace(hour=11, minute=30, second=0) + \
        datetime.timedelta(seconds=interval)
    break_end = now.replace(hour=13, minute=0, second=0)
    if now < break_start or now >= break_end:
        return False
    print("Noon break...")
    delta = break_end - datetime.datetime.now()
    print("for " + str(delta.total_seconds()) + "seconds.")
    time.sleep(delta.total_seconds())
    return True


def print_table_row_log(pattern, row_values):
    row = pattern.format(**row_values)
    if LOG:
        LOG.critical(row)
    return

def print_table_row(pattern, row_values, fout):
    row = pattern.format(**row_values)
    print(row, file=fout)
    return


def nodup_generator(g):
    # this is better than set(g)
    s = set()
    for i in g:
        if i not in s:
            yield i
            s.add(i)
