import imap_cl
import time
import os
import pathlib

import pprint

def main():

    creds = imap_cl.read_creds()

    status, imap = imap_cl.user_login(creds['host'],creds['useremail'], creds['password'])

    if status: # successfully logged in.

        while True:
            messages = imap_cl.read_inbox(imap=imap, search_flag='OLD') # poll the inbox every x seconds.
            
            print(f"New messages recieved:  {len(messages)}")
            for message in messages:
                # message is a tuple of (b'index', 'decoded dictionary message')
                ind , m = message
                # perform the flagging here
                pprint.pprint(m['Message'])
                # perform the server flag update here

            time.sleep(30)
    else:
        print("Please check credentials and try again")
        os.remove(pathlib.Path(__file__+'../../../creds/creds.json').resolve().as_posix())
        if imap is not None:
            imap.shutdown()
        main()
        


if __name__ == '__main__':
    main()