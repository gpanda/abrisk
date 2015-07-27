#!/usr/bin/python
# -*- encoding: utf8 -*-

from __future__ import print_function

__author__ = 'gpanda'

"""References:

[1] thread-safe queque, http://pymotw.com/2/Queue/

"""

import argparse
import collections
import fileinput
import os
import pprint
import re
import string
import sys
import threading
import time

import Queue

import driver

SEC_ID_PATTERN_STRING = "^\d{6}$"
SEC_ID_PATTERN = re.compile(SEC_ID_PATTERN_STRING)

config = {}

def is_sec_id(chars):
    return SEC_ID_PATTERN.match(chars)



class Fund(object):
    """Fund data structure

    pbr = price / book value (nav), an important index to sort funds

    """

    def __init__(self, secId, name=None, time=None, price=float(0), nav=float(1)):
        """Initialize Fund object

        :param secId: security id
        :param name: name
        :param time: data timestamp
        :param price: security price
        :param nav: security (fund) net asset value or book value

        """
        self.secId = secId
        self.name = name
        self.time = time
        self.price = price
        self.nav = nav
        self.pbr = self.price / self.nav

    def __cmp__(self, other):
        return cmp(self.pbr, other.pbr)


def _initialize_input_parser():
    parser = argparse.ArgumentParser(
        description="Show me interesting funds."
    )

    parser.add_argument('--fin',
                        default="default.0",
                        nargs="*",
                        metavar="FILE",
                        help="Configure security list input file.")

    parser.add_argument('--workers',
                        default=5,
                        nargs="?",
                        metavar="COUNT",
                        help="Configure working thread count.")
    return parser

def _parse_input_0(opts):

    global config

    # retrieve fund list files
    files = opts['fin']
    if not isinstance(files, list):
        files = [files]

    config['fin'] = files

    workers = int(opts['workers'])
    if  workers > 0:
        config['workers'] = workers

    return config

def _parse_input_1(config):
    # pprint.pprint(config)
    fund_pool = collections.OrderedDict()
    files = config['fin']
    for file in files:
        if os.path.exists(file):
            filename = os.path.basename(file)
            # print("{filename}".format(filename=filename))
            fund_pool[filename] = collections.OrderedDict()
            for line in fileinput.input(file):
                if line.startswith("#"):
                    continue
                fields = line.split(',')
                sec_id = string.strip(fields[0])
                if is_sec_id(sec_id):
                    fund_pool[filename][sec_id] = [].extend(fields[1:])

    return fund_pool

def work_flow(input_queue, output_queue):

    local = threading.local()
    local.thread_name = threading.current_thread().getName()

    print("*** Thread-{0}:{1} *** Enters work_flow >>>"
          .format(local.thread_name, time.time()))

    def retrieve_data(sec_id):
        print("Thread-{0}: Retrieving data for {1}"
              .format(local.thread_name, sec_id))
        fund_raw_data = driver.getpbr(sec_id)
        if not fund_raw_data:
            return None
        fund = Fund(sec_id,
                    name=fund_raw_data[2],
                    time=fund_raw_data[0],
                    price=fund_raw_data[4],
                    nav=fund_raw_data[3]
                    )
        # driver.show(fund_raw_data)
        return fund


    for category, queue in  input_queue.items():
        try:
            print("Thread-{0}: Switching to category {1}"
                  .format(local.thread_name, category))
            while not queue.empty():
                sec_id = queue.get(False)
                fund = retrieve_data(sec_id)
                if fund:
                    output_queue[category].put(fund)
            print("Thread-{0}: Leaving category {1}"
                  .format(local.thread_name, category))
        except Queue.Empty as e:
            print(e)
    print("*** Thread-{0} *** Exits from work_flow <<<"
          .format(local.thread_name))


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
    print("All jobs have been done.")
    for category, priority_queue in fund_output_queues.items():
        print("Category-{0}".format(category))
        driver.setup_output(0)
        driver.print_header()
        while not priority_queue.empty():
            fund = priority_queue.get()
            driver.print_row((fund.time, fund.secId, fund.name,
                              fund.nav, fund.price, fund.pbr))


def sort(fund_pool):
    pass

def main():
    parser = _initialize_input_parser()
    opts = vars(parser.parse_args(sys.argv[1:]))
    config = _parse_input_0(opts)
    fund_pool = _parse_input_1(config)
    # show_fund_pool(fund_pool)
    begin = time.time()
    ordered = sync(fund_pool)
    end = time.time()
    print("Time usage: {0} seconds; Workers: {1}"
          .format(end - begin, config['workers']))
    sorted_fund_pool = sort(fund_pool)


def show_fund_pool(fund_pool):
    for category, pool in fund_pool.items():
        print("Category {category}".format(category=category))
        for sec_id, extras in pool.items():
            print("{0}, {1}".format(sec_id, extras))


if __name__ == '__main__':
    main()
