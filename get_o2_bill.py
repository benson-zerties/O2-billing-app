#!/usr/bin/python2.7
# -*- coding: utf8 -*-

import M2Crypto
from M2Crypto import SSL, m2urllib2, X509, m2urllib
import cookielib
import sys
import pprint
from time import gmtime, strftime
import os
from my_html_parser import MyHtmlParser
from kwallet_dbus_proxy import *

import argparse

login_data = {
    'msisdnTextField'  : '',
    'passwordTextField': '',
}
O2_BILL_DOWNLOAD_PAGE="http://wap.o2online.de/vertrag/rechnung/aktuelle-rechnung"
O2_LOGOUT="http://wap.o2online.de/ndm/?url=loggedout_touch&logout=1"
O2_LOGIN="https://login.m.o2online.de/login/login?wicket:interface=:198:loginForm::IFormSubmitListener::"
O2_SSL_CERTIFICATE="login.o2online.de"

request_login_data = False

# parse commandline parameters
parser = argparse.ArgumentParser(description='Retrieve O2-Mobile Bill')
parser.add_argument('-s', action="store_true", default=False, dest='request_login_data', help="reset login data")
results = parser.parse_args()

# kwallet object to get login information
try:
    kwallet_obj = KWalletDBusProxy("o2_billing_app")
except (OperationFailedError), e:
    print e
    sys.exit(1)


if results.request_login_data:
    try:
        user = raw_input("Login-Name: ");
        kwallet_obj.storeValue('user', user);
        passwd = raw_input("Login-Password: ");
        kwallet_obj.storeValue('password', passwd);
    except (Exception), e:
        print e
        sys.exit(1)

# get username
try:
    login_data['user'] = str(kwallet_obj.getValue('user'));
except (KeywordNotFoundException),e:
    print "run './get_o2_bill.py -s'"
    print e
    sys.exit(1)
# get password
try:
    login_data['password'] = str(kwallet_obj.getValue('password'));
except (KeywordNotFoundException),e:
    print "run './get_o2_bill.py -s'"
    print e
    sys.exit(1)
   

###########################################################
# open website and download bill                          #
###########################################################
# login data
login_form_data = {
    'cancel'           : 'https://login.m.o2online.de/ndm/?url=o2activehome',
    'msisdnTextField'  : login_data['user'],
    'passwordTextField': login_data['password'],
    'success'          : 'https://login.m.o2online.de/ndm/?url=o2activehome&',
    'id13_hf_0'        : ''
}

login_data_encoded = m2urllib.urlencode(login_form_data)

ctx = SSL.Context()

# TODO: remove next line, because it makes the connection unsecure,
#       so far it's needed, since O2 is too stupid to configure <CN>
#       in their certificate properly
SSL.Connection.postConnectionCheck = None

# If you comment out the next 2 lines, the connection won't be secure
ctx.set_verify(SSL.verify_peer | SSL.verify_fail_if_no_peer_cert, depth=9)
ctx.load_verify_locations(O2_SSL_CERTIFICATE)
c = SSL.Connection(ctx)

cj = cookielib.CookieJar()
opener = m2urllib2.build_opener(ctx, m2urllib2.HTTPCookieProcessor(cj))
m2urllib2.install_opener(opener)

print "processing"
try:
    ctx.load_verify_locations(O2_SSL_CERTIFICATE)
    # login
    resp = opener.open(O2_LOGIN, login_data_encoded)
    ctx.load_verify_locations(O2_SSL_CERTIFICATE)

    # go to billing page
    resp = opener.open('http://wap.o2online.de/vertrag/rechnung/aktuelle-rechnung')
    last_respone = resp.read();

    print "get billing page"

    parser = MyHtmlParser(
        u'http://wap.o2online.de/vertrag/rechnung/',
        r';jsessionid=',
        r'format=rechnung.pdf',
        last_respone
    )
    
    if (parser.getResult() == []):
        print "didn't find pdf files, was login successfull?"
        print "============================================"
        print last_respone
        sys.exit(1)
    
    for i,bill in enumerate(parser.getResult()):
        resp = opener.open(bill);
        pdf_name = ("%s_part_%d.pdf") % (strftime("%Y_%m", gmtime()),i)
        print pdf_name
        f = open(os.path.basename(pdf_name), 'wb')
        f.write(resp.read())
        f.close()

    # log me out
    resp = opener.open(O2_LOGOUT)

    opener.close()

except M2Crypto.SSL.Checker.WrongHost, e:
    print "wrong host"
    print e.message

except (M2Crypto.SSL.SSLError), e:
    print "bad certificate"
    print e.message
    sys.exit(1)

except (m2urllib2.URLError), e:
    print "network probably down"
    print e.message
    sys.exit(1)

except (Exception), e:
    print "other error"
    print e
    sys.exit(1)
