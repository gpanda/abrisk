#!/usr/bin/env python
# -*- encoding: utf8 -*-
from __future__ import print_function

__author__ = 'gpanda'

import itertools
import logging
import os
import pprint
import sys
import threading
import time
import datetime

import Queue

from concurrent.futures import ThreadPoolExecutor
from multiprocessing.pool import ThreadPool

from libs.common import valid_deal_time, noon_break, nodup_generator, Security
from libs.monitor import *
from libs.driver import getpbr, setup_output


stop_event = threading.Event()
stop_event.clear()

def start_monitor(cfg, rule_sets):

    def fetch_security(sid):
        raw_s = getpbr(sid)
        if not raw_s:
            return None
        s = Security(sid, name=raw_s[2], time=raw_s[0], price=raw_s[4],
            volume=raw_s[5], nav=raw_s[3])
        return s

    def test_against_rules(s):
        try:
            for category, rules in rule_sets.items():
                sid = s.sid
                if sid in rules:
                    sub_rules = rules[sid]
                    if LOG.isEnabledFor(logging.DEBUG):
                        LOG.debug("select rules for {} in category {}"
                            .format(sid, category))
                        LOG.debug(sub_rules)
                    for r in sub_rules:
                        if trigger(r, s):
                           msg = get_msg(r, s)
                           send_msg(msg)
        except Exception as e:
            LOG.error(e)
            return e


    if LOG.isEnabledFor(logging.INFO):
        print_monitor_rules(rule_sets)

    max_workers = cfg['workers']
    with ThreadPoolExecutor(max_workers=max_workers) as exec1:
        sids = set(sid for category, rules in rule_sets.items()
                       for sid in rules.keys())
        interval = cfg['interval']
        while True:
            if noon_break(interval):
                print("Resume!")
            loop_start = time.time()
            out1 = exec1.map(fetch_security, sids)
            with ThreadPoolExecutor(max_workers=max_workers) as exec2:
                out2 = exec2.map(test_against_rules, out1)
                for result in out2:
                    if isinstance(result, Exception):
                        LOG.error(result)
            if not valid_deal_time(interval):
                print("Not in trading hours, exit.")
                break
            loop_end = time.time()
            time.sleep(interval + loop_start - loop_end)


def main():
    parser = initialize_input_parser()
    opts = vars(parser.parse_args(sys.argv[1:]))
    cfg = parse_input_0(opts)
    rule_sets = parse_input_1(cfg)
    start_monitor(cfg, rule_sets)

if __name__ == '__main__':
    if not valid_deal_time():
        # sys.exit(1)
        None
    main()
