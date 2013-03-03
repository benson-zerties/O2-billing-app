#!/usr/bin/python
# -*- coding: utf8 -*-

import re

class MyHtmlParser(object):

    base_url = None
    start_sequence = None
    end_sequence = None

    parser_input = u""
    regex = None

    def __init__(self, base_url, start_sequence, end_sequence,
            html_text = None):
        self.base_url = base_url
        self.regex = re.compile(r'(%s.*?%s)' % (start_sequence, end_sequence), re.I | re.U | re.DOTALL)
        if html_text != None:
            self.parser_input = html_text

    def feedParser(self, html_text):
        self.parser_input = html_text

    def getResult(self):
        result = []
        iter_obj = self.regex.finditer(self.parser_input)
        for i in iter_obj:
            result.append(self.base_url + (i.group(1)).decode("utf-8"))

        return result

if __name__ == "__main__":
    result = ""
    fhandler = open("result.html", "r")
    for line in fhandler:
        result += line
    parser = MyHtmlParser(
        u'http://wap.o2online.de/vertrag/rechnung/',
        r';jsessionid=',
        r'format=rechnung.pdf',
        result
    )
    print parser.getResult()
    
