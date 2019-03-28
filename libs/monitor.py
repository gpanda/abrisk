# -*- coding: utf8 -*-
""" monitor library code """

from __future__ import print_function
from __future__ import absolute_import

__author__ = 'gpanda'

import argparse
import logging
import multiprocessing
import re
import subprocess
import sys
import time

from collections import OrderedDict
from datetime import datetime

from .common import print_table_row, is_sec_id, valid_deal_time
from .driver import get_quote

"""
# TRIGGER MAP
# Type  Name    Unit
# 1     Price   Chinese Yuan
# 2     P/B     1.000
# 3     Volume  0.1B Chinese Yuan
# 4     NAV     Chinese Yuan

# Rule sets example
#   0   1           2       3       4           5
# Long term thresholds
#   ID  SName       Type    Func    Threshold   Misc
150019  银华锐进    1       <=      .621
150019  银华锐进    2       <=      1.03
150224  证券B级     2       <=      1.03
150224  证券B级     2       >=      1.12
150224  证券B级     4       <=      .26

# Short term thresholds
150019  银华锐进    1       <=      .690
150019  银华锐进    1       >=      .700
150019  银华锐进    2       >=      1.15
150019  银华锐进    2       <=      1.10

150019  银华锐进    3       >=      0.3         AM
150019  银华锐进    3       >=      0.5         PM

"""

NOTIFY = "notify '⚠️  💰ABRISK💰' \"{}\""

LOG_FORMAT = "%(asctime)-15s %(threadName)s %(message)s"
# logging.basicConfig(format=LOG_FORMAT)
LOG = logging.getLogger("abrisk.monitor")
HANDLER = logging.StreamHandler(sys.stdout)
HANDLER.setFormatter(logging.Formatter(LOG_FORMAT))
LOG.addHandler(HANDLER)
LOG.setLevel(logging.INFO)

SEPARATOR = r'\s*(?:\s|,)\s*'
OUTPUT_PATTERN = {
    'cmd': {
        'header':
            "|{SId:^8}|{SName:^8}| {Type:^10}|{Func:^8}|{Threshold:^8}"
            "|{Misc:^4}|",
        'row':
            "|{SId:^8}|{SName:^8}| {Type:^10}|{Func:^8}|{Threshold:^8}"
            "|{Misc:^4}|",
    }
}

HEADER_LABELS = {
    'SId': '证券代码',
    'SName': '证券名称',
    'Type': '触发类型',
    'Func': '触发函数',
    'Threshold': '触发阈值',
    'Misc': '其它约束',
}

def price(s):
    return s.price

def pbr(s):
    return s.pbr

def volume(s):
    return s.volume

def nav(s):
    return s.nav

TYPE_MAP = {
    1: (price, '价格(元)'),
    2: (pbr, ' 市净率 '),
    3: (volume, '交易量(亿)'),
    4: (nav, '净值(元)'),
}

def check_trigger(i):
    # check trigger type validity
    if i < 1 or i > len(TYPE_MAP):
        raise Exception('Invalid trigger type!')

def le(s, i, e):
    return TYPE_MAP[i][0](s) <= e

def ge(s, i, e):
    return TYPE_MAP[i][0](s) >= e

def lt(s, i, e):
    return TYPE_MAP[i][0](s) < e

def gt(s, i, e):
    return TYPE_MAP[i][0](s) > e

FUNC_MAP = {
    '<=': (le, '<=', '小于或等于'),
    '>=': (ge, '>=', '大于或等于'),
    '<': (lt, '<', '小于'),
    '>': (gt, '>', '大于'),
}

def am(s):
    return 'AM' == datetime.strptime(s.time, '%H:%M:%S').strftime('%p')

def pm(s):
    return 'PM' == datetime.strptime(s.time, '%H:%M:%S').strftime('%p')

MISC_FUNC_MAP = {
    'am': (am, '上午'),
    'pm': (pm, '下午'),
}

def trigger(r, s):
    check_trigger(r[2])
    return ( len(r) < 6 or MISC_FUNC_MAP[r[5].lower()][0](s) ) and \
            FUNC_MAP[r[3]][0](s, r[2], r[4])


TRIGGER_MESSAGE_PATTERN = \
    "提醒:{stime}: {sid} {sname} {ttype} {tfunc} {threshold} {misc}: {value}"


"""
Config options utilities

"""

def initialize_input_parser():
    """CLI parser"""

    parser = argparse.ArgumentParser(
        description="To monitor and alert for your interesting securities."
    )

    parser.add_argument(
        '--fin', '-i',
        type=open,
        nargs="*",
        metavar="FILE",
        help="a input file contains a rule list."
    )

    parser.add_argument(
        '--workers', '-w',
        type=int,
        default=multiprocessing.cpu_count(),
        nargs="?",
        metavar="COUNT",
        help="Working thread count."
    )

    parser.add_argument(
        '--interval', '-t',
        type=int,
        default=60,
        nargs="?",
        metavar="SECONDS",
        help="Monitor sleep interval."
    )

    parser.add_argument(
        '--rules', '-s',
        type=str,
        nargs="*",
        metavar="RULE",
        help="rule list specified in command line."
    )

    parser.add_argument(
        '--verbose', '-v',
        action="store_true",
        help="Show debug messages."
    )

    return parser


def parse_input_0(opts):
    """ Build configuration object. """

    config = {}

    # retrieve security list files
    files = opts['fin']
    if not isinstance(files, list):
        files = [files]

    config['fin'] = files

    workers = int(opts['workers'])
    if  workers > 0:
        config['workers'] = workers

    interval = int(opts['interval'])
    if  interval > 0:
        config['interval'] = interval

    rules = opts['rules']
    if not isinstance(rules, list):
        rules = [rules]

    config['rules'] = rules

    if opts['verbose']:
        config['debug'] = True
        LOG.setLevel(logging.DEBUG)

    return config


def parse_input_1(cfg):
    """ Build subject matters(security pools). """
    # pprint.pprint(config)
    rule_sets = OrderedDict()

    files = cfg['fin']
    for f in files:
        if f is None:
            break
        with f as f:
            rule_sets[f.name] = OrderedDict()
            for line in f:
                # print(string.strip(line))
                if line.startswith("#"):
                    continue
                cols = re.split(SEPARATOR, line)
                if not cols[-1].strip():
                    cols = cols[:-1]
                if len(cols) < 5:
                    continue
                for c in cols:
                    c = c.strip()
                cols[2] = int(cols[2])
                cols[4] = float(cols[4])
                sid = cols[0]
                if is_sec_id(sid):
                    rules = rule_sets[f.name]
                    if sid not in rules:
                        rules[sid] = set()
                    rules[sid].add(tuple(cols))

    cli_rules = cfg['rules']
    if cli_rules[0]:
        category = 'Quick_show'
        rule_sets[category] = OrderedDict()
        for s in cli_rules:
            cols = re.split(SEPARATOR, s)
            if len(cols) < 5:
                continue
            for c in cols:
                c = c.strip()
            cols[2] = int(cols[2])
            cols[4] = float(cols[4])
            sid = cols[0]
            if is_sec_id(sid):
                rules = rule_sets[category]
                if sid not in rules:
                    rules[sid] = set()
                rules[sid].add(tuple(cols))

    return rule_sets


# Output utilities

def print_header():
    """ Print table header. """
    pattern = OUTPUT_PATTERN['cmd']['header']
    print_table_row(pattern, HEADER_LABELS, sys.stdout)


def print_row(r):
    """ Print table row. """
    pattern = OUTPUT_PATTERN['cmd']['row']
    row_values = {
        'SId': r[0],
        'SName': r[1],
        'Type': TYPE_MAP[r[2]][1],
        'Func': FUNC_MAP[r[3]][1],
        'Threshold': r[4],
        'Misc': "" if len(r) < 6 else r[5],
    }
    print_table_row(pattern, row_values, sys.stdout)


def print_monitor_rules(rule_sets):
    # pprint.pprint(rule_sets)
    for category, rules in list(rule_sets.items()):
        print("Category: " + category)
        print_header()
        for rule in list(rules.values()):
            for sub_rule in rule:
                print_row(sub_rule)

def get_msg(r, s):
    return TRIGGER_MESSAGE_PATTERN.format(
        stime=s.time,
        sid=s.sid,
        sname=s.name,
        ttype=TYPE_MAP[r[2]][1],
        tfunc=FUNC_MAP[r[3]][1],
        threshold=r[4],
        misc="" if len(r) < 6 else r[5],
        value=TYPE_MAP[r[2]][0](s),
    )


def send_msg(msg):
    """."""
    real_cmd = NOTIFY.format(msg)
    subprocess.call(real_cmd, shell=True)

def test(r):
    s = get_quote('150019', 'MARKET_SZ')
    if le(s, 1, .96):
        msg = "{} {} pb:{:.3f}".format(s.name, s.time, s.pbr)
        real_cmd = NOTIFY.format(msg)
        subprocess.call(real_cmd, shell=True)

def loop():
    i = sys.argv[1]
    while True:
        if not valid_deal_time():
            msg = "Monitor is shut down. Bye!"
            real_cmd = NOTIFY.format(msg)
            subprocess.call(real_cmd, shell=True)
            break;

        test(i)
        time.sleep(60)

