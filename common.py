# -*- encoding: utf8 -*-
from __future__ import print_function

__author__ = 'gpanda'

import datetime
import re

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

def valid_deal_time():
    d = datetime.datetime.now()
    deal_start = datetime.time(hour=9, minute=30, second=0)
    deal_end = datetime.time(hour=15, minute=0, second=0)
    if d.time() < deal_start or d.time() >= deal_end:
        return False
    w = d.isoweekday()
    if w < 1 or w > 5:
        return False
    return True

