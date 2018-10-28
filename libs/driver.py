#!/usr/bin/env python
# -*- coding: utf8 -*-

from __future__ import print_function

__author__ = 'gpanda'

import re
import requests
import sys

import codecs
import locale

from common import print_table_row, LOG

#print(locale.getpreferredencoding())
#sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)

reload(sys)
sys.setdefaultencoding('utf8')


import HTMLParser
htmlparser = HTMLParser.HTMLParser()

UTF8_ENCODING = "UTF-8"

SCHEME = 'http://'
URL_HTML_SUFFIX = '.html'

MARKET_SH = 0
MARKET_SZ = 1
MARKET_XX = 64

EASTMONEYFUND_HOST = 'fund.eastmoney.com'
EASTMONEYFUND_RESOURCE_PREFIX = '/'
EASTMONEYFUND_QUOTE_PREFIX = SCHEME + EASTMONEYFUND_HOST \
    + EASTMONEYFUND_RESOURCE_PREFIX

NAV_FETCH_INTERVAL = 60
NAV_FETCH_TIMES = -1

# <div id="statuspzgz" class="fundpz"><span class="red bold">2.3142</span><
#NAV_REGEX = \
#    u"<div\s+id=\"statuspzgz\"\s+class=\"fundpz\">" \
#    u"<span\s+class=\"\w+\s+bold\">(\d+\.\d+)</span><"
#id="gz_gsz">0.7903</span>
NAV_REGEX = u"id=\"gz_gsz\">(\d+\.\d+)</span>"
NAV_TIME = \
    u""

# print(NAV_REGEX)

# http://hq.sinajs.cn/list=sz150001
HQSINA_HOST = 'hq.sinajs.cn'
HQSINA_RESOURCE_PREFIX = '/list='
HQSINA_QUOTE_SH = 'sh'
HQSINA_QUOTE_SZ = 'sz'
HQSINA_QUOTE_PREFIX = SCHEME + HQSINA_HOST + HQSINA_RESOURCE_PREFIX
HQSINA_QUOTE_SH_PREFIX = HQSINA_QUOTE_PREFIX + HQSINA_QUOTE_SH
HQSINA_QUOTE_SZ_PREFIX = HQSINA_QUOTE_PREFIX + HQSINA_QUOTE_SZ
HQSINA_QUOTE_PATTERN_REGEX = u"var\s+hq_str_.+=\"(.*)\";"
HQSINA_QUOTE_SEP = u","

# http request header patterns
HTTP_HEADER_CONTENT_TYPE_CHARSET_REGEX=r"charset=(\w+)"

# http request timeout
HTTP_REQUEST_TIMEOUT = 8
# =============================================================================

def get_page_content(page):
    """."""
    content = None

    # signal.signal(signal.SIGALRM, handler)
    #timeout = 60
    # signal.alarm(timeout)

    try:
        resp = requests.get(page, timeout=HTTP_REQUEST_TIMEOUT)
        encoding = resp.encoding
        ct_hdr = resp.headers['Content-Type']
        if ct_hdr:
            m = re.search(HTTP_HEADER_CONTENT_TYPE_CHARSET_REGEX, ct_hdr)
            if m:
                encoding = m.group(1)
        content = resp.content
        if content:
            content = content.decode(encoding)
            content = content.encode(UTF8_ENCODING)
    except IOError:
        # print("Give up get request ({page}) after {timeout} seconds.".\
        #     format({'page': page, 'timeout': timeout}))
        # print("Error occurred during request of ({page}) ". \
        #      format({'page': page}))
        LOG.info("Error occurred during request of %s", page)
        raise

    # signal.alarm(0)          # Disable the alarm

    return content

def search_regex(regex, page):
    """."""
    results = None

    content = get_page_content(page)
    if content:
        content = content.decode(UTF8_ENCODING)
        results = re.findall(regex, content, re.U)
    return results

def get_nav_url(qid):
    """."""
    return EASTMONEYFUND_QUOTE_PREFIX + str(qid) + URL_HTML_SUFFIX

def get_market(qid):
    """."""
    if qid / 100000 == 1:
        return MARKET_SZ
    else:
        return MARKET_SH

def get_nav(qid):
    """."""
    url = get_nav_url(qid)
    results = search_regex(NAV_REGEX, url)
    if results:
        return results[0]

def get_quote_url(qid, market):
    """."""
    if int(market) == MARKET_SH:
        return HQSINA_QUOTE_PREFIX + HQSINA_QUOTE_SH + str(qid)
    if int(market) == MARKET_SZ:
        return HQSINA_QUOTE_PREFIX + HQSINA_QUOTE_SZ + str(qid)

def get_quote(qid, market):
    """."""
    url = get_quote_url(qid, market)
    quote_raw = search_regex(HQSINA_QUOTE_PATTERN_REGEX, url)
    if not quote_raw:
        return
    quote_raw = quote_raw[0]
    quote = re.split(HQSINA_QUOTE_SEP, quote_raw, flags=re.U)
    return quote

def getpbr(qid):
    """."""
    # get dynamic Net Asset Value (update interval: 5 minutes)
    _nav = get_nav(qid)
    if _nav:
        _nav = float(_nav)
    else:
        return

    # get current quote information, such as price
    market = MARKET_XX
    qid = int(qid)
    market = get_market(qid)
    if market == MARKET_XX:
        return

    quote = get_quote(qid, market)
    if not quote:
        return
    _datlen = len(quote)
    if _datlen <= 1:
        return
    _name = quote[0]
    _time = quote[31]
    _price = float(quote[3])
    _volume = float(quote[9]) / 10 ** 8

    # calculate dynmaic Price/Book ratio
    _pbr = _price / _nav

    return (_time, qid, _name, _nav, _price, _volume, _pbr)

# =============================================================================
# OUT_FORMAT
CSV_FORMAT = 'csv'
CMD_FORMAT = 'cmd'

# OUTPUT_PATTERN
OUTPUT_PATTERN = {
    'csv': {
        'header':
            u"{Time:^8},{QId:^8},{QName:^10},{NAV:>10},{Price:^6},{Volume:^6},{PBRatio:<9},",
        'row':
            u"|{Time:^8},{QId:^8},{QName:^6},{NAV:>10},{Price:^6},{Volume:^6.3},{PBRatio:<9.2%},"
    },
    'cmd': {
        'header':
            u"|{Time:^8}|{QId:^8}|{QName:^10}|{NAV:>10}|{Price:^6}|{Volume:^6}|{PBRatio:<9}|",
        'row':
            u"|{Time:^8}|{QId:^8}|{QName:^6}|{NAV:>10}|{Price:^6}|{Volume:^6.3}|{PBRatio:<9.2%}|"
    }
}

# current setup
CURRENT_OUTPUT_FORMAT = None
CURRENT_FOUT = None

def print_header():
    if not CURRENT_OUTPUT_FORMAT:
        return

    pattern = OUTPUT_PATTERN[CURRENT_OUTPUT_FORMAT]['header']
    row_values = {
        'Time': u"Time",
        'QId': u"Quote ID",
        'QName': u"Quote Name",
        'NAV': u"Book Value",
        'Price': u"Price",
        'Volume': u"Volume",
        'PBRatio': u"P/B Ratio",
    }

    print_table_row(pattern, row_values, CURRENT_FOUT)
    return

def print_row(quote):
    if not CURRENT_OUTPUT_FORMAT:
        return

    pattern = OUTPUT_PATTERN[CURRENT_OUTPUT_FORMAT]['row']
    row_values = {
        'Time': quote[0],
        'QId': quote[1],
        'QName': quote[2],
        'NAV': quote[3],
        'Price': quote[4],
        'Volume': quote[5],
        'PBRatio': quote[6],
    }

    print_table_row(pattern, row_values, CURRENT_FOUT)

# =============================================================================
def show(t):
    if t:
        global CURRENT_FOUT
        global CURRENT_OUTPUT_FORMAT
        CURRENT_FOUT = sys.stdout
        CURRENT_OUTPUT_FORMAT = CMD_FORMAT
        print_header()
        print_row(t)

def cli():
    global CURRENT_FOUT
    global CURRENT_OUTPUT_FORMAT
    CURRENT_FOUT = sys.stdout
    CURRENT_OUTPUT_FORMAT = CMD_FORMAT

def csv():
    global CURRENT_FOUT
    global CURRENT_OUTPUT_FORMAT
    CURRENT_FOUT = None
    CURRENT_OUTPUT_FORMAT = CSV_FORMAT

OUTPUT_MAP = {
    0: cli,
    1: csv,
}

def setup_output(mode, logger):
    global LOG
    LOG = logger
    OUTPUT_MAP[mode]()


def test_encoding():

    content = None
    cs = None
    url = HQSINA_QUOTE_SZ_PREFIX + "150019"
    resp = requests.get(url)
    ct_hdr = resp.headers['Content-Type'];
    if ct_hdr:
        m = re.search(HTTP_HEADER_CONTENT_TYPE_CHARSET_REGEX, ct_hdr)
        if m:
            cs = m.group(1)
    content = resp.content
    if content:
        if cs:
            content = content.decode(cs)
        else:
            content = content.decode(resp.encoding)
        content = content.encode(UTF8_ENCODING)
    #print(u"%s" % content)
    print("url = %s, resp.encoding = %s, resp hdr charset = %s\ncontent=%s" % 
          (url, resp.encoding, cs, content))


def test():
    test_encoding()

if __name__ == '__main__':
    test()

