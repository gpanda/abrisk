#!/usr/bin/env python
# -*- encoding: utf8 -*-
from __future__ import print_function

__author__ = 'gpanda'

import itertools
import logging
import os
import pprint
import sys
import subprocess
import threading
import time
import datetime

import Queue

from concurrent.futures import ThreadPoolExecutor
from multiprocessing.pool import ThreadPool

from libs.common import valid_deal_time, nodup_generator, Security
from libs.monitor import *
from driver import getpbr, setup_output


CMD = "notify '⚠️  💰ABRISK💰' \"{}\""
stop_event = threading.Event()
stop_event.clear()

def test(r):
    if le(s, 6, .96):
        msg = "{} {} pb:{:.3f}".format(s[1], s[2], s[6])
        real_cmd = CMD.format(msg)
        subprocess.call(real_cmd, shell=True)

def loop():
    i = sys.argv[1]
    while True:
        if not valid_deal_time():
            msg = "Monitor is shut down. Bye!"
            real_cmd = CMD.format(msg)
            subprocess.call(real_cmd, shell=True)
            break;

        test(i)
        time.sleep(60)


def trigger(msg):
    real_cmd = CMD.format(msg)
    subprocess.call(real_cmd, shell=True)


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
                sid = s.secId
                if sid in rules:
                    sub_rules = rules[sid]
                    if LOG.isEnabledFor(logging.DEBUG):
                        LOG.debug("select rules for {} in category {}"
                            .format(sid, category))
                        LOG.debug(sub_rules)
                    for r in sub_rules:
                        if TRIGGER_FUNC_MAP[r[3]][0](s, r[2], r[4]):
                            msg = TRIGGER_MESSAGE_PATTERN.format(
                                stime=s.time,
                                sid=sid,
                                sname=s.name,
                                trigger=TRIGGER_MAP[r[2]][1],
                                tfunc=TRIGGER_FUNC_MAP[r[3]][1],
                                threshold=r[4],
                                value=TRIGGER_MAP[r[2]][0](s),
                            )
                            trigger(msg)
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
        terminated = False
        while not terminated:
            loop_start = time.time()
            out1 = exec1.map(fetch_security, sids)
            with ThreadPoolExecutor(max_workers=max_workers) as exec2:
                out2 = exec2.map(test_against_rules, out1)
                for result in out2:
                    if isinstance(result, Exception):
                        LOG.error(result)
                if not valid_deal_time():
                    terminated = True
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
