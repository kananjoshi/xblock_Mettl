# uncompyle6 version 3.5.0
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.5 (default, Aug  7 2019, 00:51:29) 
# [GCC 4.8.5 20150623 (Red Hat 4.8.5-39)]
# Embedded file name: /edx/app/edxapp/venvs/edxapp/lib/python2.7/site-packages/mettl/command_line.py
# Compiled at: 2017-10-05 12:19:06
import mettl

def WriteJson(pub_key, pri_key):
    import os, json
    FILE_PATH = mettl.__file__.rsplit('/', 1)[0]
    FILE_NAME = os.path.join(FILE_PATH, 'mettl_auth_keys.json')
    FILE_DATA = {'PUBLIC_KEY': pub_key, 
       'PRIVATE_KEY': pri_key}
    with open(FILE_NAME, 'w+') as (outfile):
        json.dump(FILE_DATA, outfile)
        print ('Authentication keys are being saved in {0} !').format(FILE_NAME)


def PromptKey():
    pub_key, pri_key = ('blank123456', 'blank123456')
    pub_key_flag = True
    while pub_key_flag:
        try:
            pub_key = str(raw_input('Please enter your Public Key : '))
            if len(pub_key) == 36:
                pub_key_flag = False
            else:
                print 'The key must be 36 character long !'
        except Exception as e:
            print e
            pub_key_flag = False

    pri_key_flag = True
    while pri_key_flag:
        try:
            pri_key = str(raw_input('Please enter your Private Key : '))
            if len(pri_key) == 36:
                pri_key_flag = False
            else:
                print 'The key must be 36 character long !'
        except Exception as e:
            print e
            pri_key_flag = False

    return (
     pub_key, pri_key)


def main():
    pub_key, pri_key = PromptKey()
    WriteJson(pub_key, pri_key)