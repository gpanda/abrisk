#!/usr/bin/env python
# -*- coding: utf8 -*-
from __future__ import print_function

__author__ = 'gpanda'

"""References:

[1] easy thread-safe queque, http://pymotw.com/2/Queue/

"""

import argparse
import collections
import fileinput
import logging
import os
import pprint
import re
import string
import sys
import threading
import time

import Queue

from libs.common import is_sec_id
import driver

LOG_FORMAT = "%(asctime)-15s %(threadName)s %(message)s"
logging.basicConfig(format=LOG_FORMAT)
LOG = logging.getLogger("abrisk")
LOG.addHandler(logging.StreamHandler(sys.stdout))
LOG.setLevel(logging.INFO)

config = {}

class Fund(object):
    """Fund data structure

    pbr = price / book value (nav), an important index to sort funds

    """

    def __init__(self, secId, name=None, time=None, price=float(0),
                 volume=float(0), nav=float(1)):
        """Initialize Fund object

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


def _initialize_input_parser():
    parser = argparse.ArgumentParser(
        description="Show me interesting funds."
    )

    parser.add_argument(
        '--fin',
        default="default.0",
        nargs="*",
        metavar="FILE",
        help="Security list input file."
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

    files = cfg['fin']
    for yaf in files:
        if os.path.exists(yaf):
            filename = os.path.basename(yaf)
            # print("{filename}".format(filename=filename))
            fund_pool[filename] = collections.OrderedDict()
            for line in fileinput.input(yaf):
                if line.startswith("#"):
                    continue
                fields = line.split(',')
                sec_id = string.strip(fields[0])
                if is_sec_id(sec_id):
                    fund_pool[filename][sec_id] = [].extend(fields[1:])

    funds = config['funds']
    if funds[0]:
        category = 'Quick_show'
        fund_pool[category] = collections.OrderedDict()
        for fund in funds:
            if is_sec_id(fund):
                fund_pool[category][fund] = []

    return fund_pool


def work_flow(input_queue, output_queue):
    """
    TODO: comments
    """

    local = threading.local()
    local.thread_name = threading.current_thread().getName()

    LOG.debug("*** Enters work_flow() >>>")
    # print("*** Thread-{0}:{1} *** Enters work_flow >>>"
    #       .format(local.thread_name, time.time()))

    def retrieve_data(sec_id):
        """
        TODO: comments
        """
        LOG.debug("Retrieving data for %s", sec_id)
        # print("Thread-{0}: Retrieving data for {1}"
        #       .format(local.thread_name, sec_id))
        fund_raw_data = driver.getpbr(sec_id)
        if not fund_raw_data:
            return None
        fund = Fund(sec_id,
                    name=fund_raw_data[2],
                    time=fund_raw_data[0],
                    price=fund_raw_data[4],
                    volume=fund_raw_data[5],
                    nav=fund_raw_data[3],
                    )
        # driver.show(fund_raw_data)
        return fund


    for category, queue in  input_queue.items():
        try:
            LOG.debug("Switching to category %s", category)
            # print("Thread-{0}: Switching to category {1}"
            #      .format(local.thread_name, category))
            while not queue.empty():
                sec_id = queue.get(False)
                fund = retrieve_data(sec_id)
                if fund:
                    output_queue[category].put(fund)
            LOG.debug("Leaving category %s", category)
            # print("Thread-{0}: Leaving category {1}"
            #       .format(local.thread_name, category))
        except Queue.Empty as exp:
            print(exp)
    LOG.debug("*** Exits from work_flow() <<<")
    # print("*** Thread-{0} *** Exits from work_flow <<<"
    #      .format(local.thread_name))


def sync(fund_pool):
    """Central controller of fund data synchronization.

    ** Preparing working queue (FIFO) and workers for funds of interest.
    ** Preparing data queue (Heap) for storing and sorting collected data.
    ** Retrieving fund data, refining and sorting them.

    """
    fund_input_queues = {}
    fund_output_queues = {}
    for category, pool in fund_pool.items():
        fund_input_queues[category] = Queue.Queue(len(pool))
        for sec_id in sorted(pool.keys()):
            fund_input_queues[category].put(sec_id)
        fund_output_queues[category] = Queue.PriorityQueue(len(pool))

    workers = {}
    worker_number = config['workers']
    for i in range(worker_number):
        workers[i] = threading.Thread(
            target=work_flow,
            name=str(i),
            args=[fund_input_queues, fund_output_queues],
        )
        workers[i].start()

    for worker in workers.values():
        worker.join()

    LOG.debug("All jobs have been done.")

    return fund_output_queues


def report_fund_list(fund_output_queues):

    for category, priority_queue in fund_output_queues.items():
        LOG.info("Category-%s", category)
        # print("Category-{0}".format(category))
        driver.setup_output(0, LOG)
        driver.print_header()
        while not priority_queue.empty():
            fund = priority_queue.get()
            driver.print_row((fund.time, fund.secId, fund.name,
                              fund.nav, fund.price, fund.volume,
                              fund.pbr))


def show_fund_pool(fund_pool):
    for category, pool in fund_pool.items():
        LOG.debug("Category %s", category)
        # print("Category {category}".format(category=category))
        for sec_id, extras in pool.items():
            LOG.debug("%s, %s", sec_id, extras)
            # print("{0}, {1}".format(sec_id, extras))


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
    fund_list = sync(fund_pool)
    end = time.time()
    report_fund_list(fund_list)
    LOG.info("Time usage: %s seconds; Workers: %s",
             end - begin, config['workers'])
    # print("Time usage: {0} seconds; Workers: {1}"
    #       .format(end - begin, config['workers']))


if __name__ == '__main__':
    main()
