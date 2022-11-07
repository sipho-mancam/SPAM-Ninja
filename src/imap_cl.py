from imaplib import IMAP4, IMAP4_SSL
import imaplib
import json
import pathlib
import os
import getpass


def read_creds()->dict:
    p = pathlib.Path(__file__+'../../../').resolve().as_posix()+'/creds/creds.json';

    if os.path.isfile(p): 
        with open(p, 'r') as f:
            creds = json.load(f)
            return creds
    else:

        try:
            p = pathlib.Path(__file__+'../../../').resolve().as_posix() + '/creds'
            os.mkdir(p)

            creds = {}

            creds['useremail'] = input('Input Email: ')
            creds['password'] = getpass.getpass("Enter Password: ")
            creds['host'] = input('Enter Host name (e.g imap.gmail.com): ')

            with open(p+'/creds.json', 'w') as f:
                json.dump(creds, f)

        except FileExistsError as fe:
            p = pathlib.Path(__file__+'../../../').resolve().as_posix() + '/creds'

            creds = {}

            creds['useremail'] = input('Input Email: ')
            
            creds['password'] = getpass.getpass("Enter Password: ")
            creds['host'] = input('Enter Host name (e.g imap.gmail.com): ')

            with open(p+'/creds.json', 'w') as f:
                json.dump(creds, f)
            
        finally:
            with open(p+'/creds.json', 'w') as f:
                json.dump(creds, f)
            return creds


def user_login(host:str, user_email:str, user_password:str)->tuple:
    logged_in = False
    imap = None
    try:
        imap = IMAP4_SSL(host)
        print(f"Connected ...")
        r = imap.noop()
         
        if len(r)>=2:
            print('Server Response Test Passed')
        
        res = imap.login(user_email, user_password)
        print("Logged In")
        logged_in = True
    except imaplib.IMAP4.error as ie:
        print(str(ie.args[0], 'utf-8'))
        print("Logging in Failed")
    except Exception as e:
        logged_in = False
        print(e.args)
        print("Logging in Failed")
    finally:
        return logged_in, imap


def decode_message(message_str:bytes)->dict:
    """ This will recieve RFC message and returns a dictionary structured message"""

    result = {}
    message_string = str(message_str, 'utf-8')

    l = message_string.split('\r\n')
    counter = 0;

    result['Message'] = l[-2]
    for i in l:
        item = i.split(':')

        if len(item)>2:
            result[item[0]] = ':'.join(item[1:])
        elif len(item) <= 1:
            counter += 1
            if item[0] != result['Message'] and len(item[0])>0:
                result['{}'.format(counter)] = item[0].strip()
        else: 
            result[item[0]] = item[1].strip()
    
    return result


def read_inbox(mailbox='INBOX', imap:imaplib.IMAP4 = None, search_flag='NEW', data_type='(RFC822)')->list[tuple]:
    """This will read all the new messages in the server and then return a tuple of (index, message[dict])"""
    res = []
    if imap is None:
        raise ValueError("Please pass in the imap client")
        # return []
    else:
        imap.select(mailbox, False)
        # read the mail from the Imap    \
        typ, data = imap.search(None, search_flag) # get all the new messages in the inbox to check for spam
        # The search will return us message indices that we'll use to manipulate messages from the server
        # print(data) --> Comment this line to see how the data result from the search looks
        for ind in data[0].split():
            # print(ind)
            typ, message = imap.fetch(ind, data_type)
            res.append((ind, decode_message(message[0][1])))
    return res
        



