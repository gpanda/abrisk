# -*- coding: utf8 -*-

__author__ = 'gpanda'

import argparse
import logging
import multiprocessing
import re
import string
import sys

from collections import OrderedDict
from common import print_table_row, is_sec_id


LOG_FORMAT = "%(asctime)-15s %(threadName)s %(message)s"
# logging.basicConfig(format=LOG_FORMAT)
LOG = logging.getLogger("abrisk.monitor")
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter(LOG_FORMAT))
LOG.addHandler(handler)
LOG.setLevel(logging.INFO)

SEPARATOR='\s*(?:\s|,)\s*'
OUTPUT_PATTERN = {
    'cmd': {
        'header':
            "|{SId:^8}|{SName:^8}| {Trigger:^10}|{Func:^8}|{Threshold:^8}|",
        'row':
            "|{SId:^8}|{SName:^8}| {Trigger:^10}|{Func:^8}|{Threshold:^8}|",
    }
}

HEADER_LABELS = {
    'SId': '证券代码',
    'SName': '证券名称',
    'Trigger': '触发条件',
    'Func': '触发函数',
    'Threshold': '触发阈值',
}

def price(sec):
    return sec.price

def pbr(sec):
    return sec.pbr

def volume(sec):
    return sec.volume

TRIGGER_MAP = {
    0: (3, '类型数量'),
    1: (price, '价格(元)'),
    2: (pbr, ' 市净率 '),
    3: (volume, '交易量(亿)'),
}
def check_trigger(i):
    if i < 0 or i > TRIGGER_MAP[0][0]:
        raise Exception('Invalid trigger!')

def le(s, i, e):
    check_trigger(i)
    return TRIGGER_MAP[i][0](s) <= e

def ge(s, i, e):
    check_trigger(i)
    return TRIGGER_MAP[i][0](s) >= e

TRIGGER_FUNC_MAP = {
    '<=': (le, '<=', '小于或等于'),
    '>=': (ge, '>=', '大于或等于'),
}

TRIGGER_MESSAGE_PATTERN = \
    "提醒:{stime}: {sid} {sname} {trigger} {tfunc} {threshold}: {value}"


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
        type=file,
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
        metavar="RULE LIST",
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
            break;
        with f as f:
            rule_sets[f.name] = OrderedDict()
            for line in f:
                # print(string.strip(line))
                if line.startswith("#"):
                    continue
                cols = re.split(SEPARATOR, line)
                if len(cols) < 5:
                    continue
                for c in cols:
                    c = string.strip(c)
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
                c = string.strip(c)
            cols[2] = int(cols[2])
            cols[4] = float(cols[4])
            sid = cols[0]
            if is_sec_id(sid):
                rules = rule_sets[category]
                if sid not in rules:
                    rules[sid] = set()
                rules[sid].add(tuple(cols))

    return rule_sets


""" Output utilities """

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
        'Trigger': TRIGGER_MAP[r[2]][1],
        'Func': TRIGGER_FUNC_MAP[r[3]][1],
        'Threshold': r[4],
    }
    print_table_row(pattern, row_values, sys.stdout)

def print_monitor_rules(rule_sets):
    # pprint.pprint(rule_sets)
    for category, rules in rule_sets.items():
        print("Category: " + category)
        print_header()
        for rule in rules.values():
            for sub_rule in rule:
                print_row(sub_rule)

