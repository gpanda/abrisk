#!/usr/bin/env python
# -*- coding: utf8 -*-
from __future__ import print_function

__author__ = 'gpanda'

"""References:

[1] easy thread-safe queque, http://pymotw.com/2/Queue/
    now changed to queue in py3

"""

import argparse
import collections
import fileinput
import logging
import os
import pprint
import re
import sys
import threading
import time

import queue

from libs import driver
from libs.common import Fund, LOG, is_sec_id, AbriskError

config = {}



def _initialize_input_parser():
    parser = argparse.ArgumentParser(
        description="Show me interesting funds."
    )

    parser.add_argument(
        '--fin',
        nargs="*",
        metavar="FILE",
        help="One or more security list files as input."
    )

    parser.add_argument(
        '--workers',
        default=5,
        nargs="?",
        metavar="COUNT",
        help="Working thread count."
    )

    parser.add_argument(
        '--head', '-H',
        default=0,
        nargs="?",
        metavar="COUNT",
        help="How many items in the top rank to show."
    )

    parser.add_argument(
        '--tail', '-T',
        default=0,
        nargs="?",
        metavar="COUNT",
        help="How many items in the bottom rank to show."
    )

    parser.add_argument(
        '--funds', '-f',
        nargs="*",
        metavar="FUND INDEX",
        help="One or more specified funds."
    )

    parser.add_argument(
        '-v', '--verbose',
        action="store_true",
        help="Show debug messages."
    )

    return parser

def _parse_input_0(opts):

    global config
    global LOG

    # retrieve fund list files
    files = opts['fin']
    if files:
        if not isinstance(files, list):
            files = [files]
        config['fin'] = files

    workers = int(opts['workers'])
    if  workers > 0:
        config['workers'] = workers


    head = int(opts['head'])
    if head > 0:
        config['head'] = head

    tail = int(opts['tail'])
    if tail > 0:
        config['tail'] = tail

    funds = opts['funds']
    if funds:
        if not isinstance(funds, list):
            funds = [funds]
        config['funds'] = funds

    if opts['verbose']:
        config['debug'] = True
        LOG.setLevel(logging.DEBUG)

    return config


def _parse_input_1(cfg):
    """
    TODO: comments
    """
    # pprint.pprint(config)
    fund_pool = collections.OrderedDict()

    files = cfg['fin'] if 'fin' in cfg else None
    if files:
        for fname in files:
            if os.path.isfile(fname):
                fund_pool[fname] = collections.OrderedDict()
            else:
                files.remove(fname)

        with fileinput.input(files=files) as f:
            for line in f:
                if line.startswith("#"):
                    continue
                fields = line.split(',')
                sid = fields[0].strip()
                if is_sec_id(sid):
                    fund_pool[fileinput.filename()][sid] = [].extend(fields[1:])

    funds = config['funds'] if 'funds' in config else None
    if funds:
        category = 'Quick_show'
        fund_pool[category] = collections.OrderedDict()
        for fund in funds:
            if is_sec_id(fund):
                fund_pool[category][fund] = []

    return fund_pool


def work_flow(input_queues, output_queues, error_queues):
    """
    TODO: comments
    """

    local = threading.local()
    local.thread_name = threading.current_thread().getName()

    LOG.debug("*** Enters work_flow() >>>")
    # print("*** Thread-{0}:{1} *** Enters work_flow >>>"
    #       .format(local.thread_name, time.time()))

    def retrieve_data(sid):
        """
        TODO: comments
        """
        LOG.debug("Retrieving data for %s", sid)
        # print("Thread-{0}: Retrieving data for {1}"
        #       .format(local.thread_name, sid))
        fund_raw_data = driver.getpbr(sid)
        if not fund_raw_data:
            return None
        fund = Fund(sid,
                    name=fund_raw_data[2],
                    time=fund_raw_data[0],
                    price=fund_raw_data[4],
                    volume=fund_raw_data[5],
                    nav=fund_raw_data[3],
                    )
        # driver.show(fund_raw_data)
        return fund


    for ctg, idq in list(input_queues.items()):
        sid = None
        try:
            LOG.debug("Switching to category %s", ctg)
            # print("Thread-{0}: Switching to category {1}"
            #      .format(local.thread_name, c))
            while not idq.empty():
                sid = idq.get(False)
                fund = retrieve_data(sid)
                if fund:
                    output_queues[ctg].put(fund)
            LOG.debug("Leaving category %s", ctg)
            # print("Thread-{0}: Leaving category {1}"
            #       .format(local.thread_name, ctg))
        except queue.Empty as e:
            LOG.info("Unexpected queue.Empty Exception occurs, %s", e)
        except Exception as e:
            ename = "T:[" + local.thread_name + "]C:[" + ctg \
                    + "]S:[" + sid + "]"
            error_queues[ctg].put(AbriskError(ename, e))
    LOG.debug("*** Exits from work_flow() <<<")
    # print("*** Thread-{0} *** Exits from work_flow <<<"
    #      .format(local.thread_name))


def sync(fund_pool):
    """Central controller of fund data synchronization.

    ** Preparing working queue (FIFO) and workers for funds of interest.
    ** Preparing data queue (Heap) for storing and sorting collected data.
    ** Retrieving fund data, refining and sorting them.

    """
    input_queues = {}
    output_queues = {}
    error_queues = {}
    for category, pool in fund_pool.items():
        input_queues[category] = queue.Queue(len(pool))
        for sid in sorted(pool.keys()):
            input_queues[category].put(sid)
        output_queues[category] = queue.PriorityQueue(len(pool))
        error_queues[category] = queue.Queue(len(pool))

    workers = {}
    worker_number = config['workers']
    for i in range(worker_number):
        workers[i] = threading.Thread(
            target=work_flow,
            name=str(i),
            args=[input_queues, output_queues, error_queues],
        )
        workers[i].start()

    for worker in list(workers.values()):
        worker.join()

    rc = 0
    for c, eq in list(error_queues.items()):
        if not eq.empty():
            rc = 1
            break
    if rc == 0:
        LOG.debug("All jobs have been done without errors.")
    else:
        LOG.debug("All jobs have been done, but there are errors.")
    return output_queues, error_queues, rc


def report_fund_list(out_put_queues):

    for category, priority_queue in list(out_put_queues.items()):
        LOG.debug("Category-%s", category)
        # print("Category-{0}".format(category))
        driver.setup_output(0, LOG)
        driver.print_header()
        while not priority_queue.empty():
            fund = priority_queue.get()
            driver.print_row((fund.time, fund.sid, fund.name,
                              fund.nav, fund.price, fund.volume,
                              fund.pbr))


def show_fund_pool(fund_pool):
    for category, pool in list(fund_pool.items()):
        LOG.debug("Category %s", category)
        # print("Category {category}".format(category=category))
        for sid, extras in list(pool.items()):
            LOG.debug("%s, %s", sid, extras)
            # print("{0}, {1}".format(sid, extras))


def main():
    """
    TODO: no comments
    """
    parser = _initialize_input_parser()
    opts = vars(parser.parse_args(sys.argv[1:]))
    cfg = _parse_input_0(opts)
    fund_pool = _parse_input_1(cfg)
    # show_fund_pool(fund_pool)
    begin = time.time()
    funds, errors, rc = sync(fund_pool)
    if rc != 0:
        for c, eq in list(errors.items()):
            print(c, file=sys.stderr)
            while not eq.empty():
                print(eq.get().name, file=sys.stderr)
        sys.exit(1)
    end = time.time()
    report_fund_list(funds)
    LOG.debug("Time usage: %s seconds; Workers: %s",
             end - begin, config['workers'])
    # print("Time usage: {0} seconds; Workers: {1}"
    #       .format(end - begin, config['workers']))


if __name__ == '__main__':
    main()
