#!/usr/bin/env python
# -*- coding: utf8 -*-

from __future__ import print_function

__author__ = 'gpanda'

import re
import requests
import sys

import codecs
import locale

from lxml import html

reload(sys)
sys.setdefaultencoding('utf8')

url='http://www.cboe.com/delayedquote/advanced-charts?ticker=VIX'

def get_vix():
    r = requests.get(url)
    root = html.fromstring(r.content)
    vix_price_xpath=\
    '//*[@id="ContentTop_T3A8AEB8A001_Content"]/div[2]/div/div/div/div/div[1]/div/span'
    vix_change_xpath=\
    '//*[@id="ContentTop_T3A8AEB8A001_Content"]/div[2]/div/div/div/div/div[1]/div/div/span[2]'

    vix_price=root.xpath(vix_price_xpath)
    vix_change=root.xpath(vix_change_xpath)

    print(vix_price[0].text.strip() + " " + vix_change[0].text.strip())


if __name__ == '__main__':
    get_vix()
