from __future__ import print_function

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import pprint
import base64
import re
from bs4 import BeautifulSoup


SCOPES = ["https://mail.google.com/"]


class GMailAPI:

    def __init__(self, scopes, fp, **kwargs)->None:
        self.SCOPES = scopes
        self.creds = None
        self.creds_file_path = fp;
        self.threads = None;
        self.new_message= None;
        self.classifier = None;
        self.service_obj = None;

    def set_classifier(self, cl)->None:
        self.classifier = cl;
    
    def get_classifier(self):
        return self.classifier
    
    def login(self):
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('spam-ninja-creds.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        self.creds = creds

        if creds: return True
        else: return False
    
    def read_threads(self):
        if self.login():
            try:
                # create gmail api client
                service = build('gmail', 'v1', credentials=self.creds)
                self.service_obj = service
                # pylint: disable=maybe-no-member
                # pylint: disable:R1710
                threads = service.users().threads().list(userId='me').execute().get('threads', [])
                thread = service.users().threads().get(userId='me', id=threads[0]['id']).execute()
                # pprint.pprint(thread['messages'][0]['payload']['parts'][1]['body']['data'])
                self.threads = threads
                msg_list = service.users().messages().list(userId='me').execute()
                msg = service.users().messages().get(userId='me', id=msg_list['messages'][0]['id']).execute()
                pprint.pprint(msg['payload'])

                self.flag_spam(msg_list['messages'][0])
                # self.get_message(msg)
            except HttpError as error:
                print(F'An error occurred: {error}')
        else:
            raise HttpError('An error occurred: {error}')
        
    def flag_spam(self, message):
        try:
            labels = {
                'addLabelIds':['SPAM'],
                'removeLabelIds':['INBOx'],
            }
            self.service_obj.users().messages().modify(userId='me', id=message['id'], body=labels).execute()
            return True
        except HttpError as e:
            return False

    def modify_labels(self, add_labels=[], remove_label=[], thread={'id':''}):
        try:
            labels = {
                'addLabelIds':add_labels,
                'removeLabelIds':remove_label,
            }
            self.service_obj.users().threads().modify(userId='me', id=thread['id'], body=labels).execute()
        except HttpError as he:
            print(he)
            return False
        
    def create_label(label_name):
        pass

    #############################################################
    # Helper Methods to decode and parse message to normal text.#
    #############################################################

    def get_message(self, msg_obj)->str:
        payload = msg_obj['payload']
        res = ''
        # check mime type, if it's a single message we extract body, otherwise extract the parts
        if re.match(r'multipart',payload['mimeType'].lower()) is not None:
            # is multipart, let's combine the parts.
            for data in payload['parts']:
                text = self.decode_message(data['body']['data'])
                print(text)
                if type(text) is not bool:
                    print(self.is_html(text))


    def process_message(self, message_obj)->str:
        message_data = message_obj

    def decode_message(self, message:str)->str:     
        try:
            if message.endswith(r'='):
                dec = base64.b64decode(message)
            else:
                message += '==';
                dec = base64.b64decode(message)
                # dec.decode('utf-32')
            return str(dec)
        except Exception as e:
            print(e)
            return False
    
    def is_html(self, message:str)->bool:
        res = re.match(r'<.*?>', message)
        if res is not None:
            return True
        else:
            return False
    
    def extract_data_4rm_html(self, message:str)->str:
        soup = BeautifulSoup(message)

        text = soup.text

        text.replace('\n', '')

        print(text)

        return text

    def run(self):
        # self.read_threads()
        """
        1. Read the threads, and get all the messages inside threads and the clean them up
        2. Run the messages in a thread collectively through the classifier(to build ...)TODO,
        3. Flag the Thread either as SPAM or None SPAM,
        4. Repeat for all the thraeds.
        """
        self.read_threads()
        for thread in self.threads:
            self.clean_thread(thread)
            res = self.classifer.is_spam(thread)
            if res:
                self.flag_spam(thread)
            # mark the thread as marked.
            




gApi = GMailAPI(SCOPES, 'spam-ninja-creds.json')



if __name__ == '__main__':
    gApi.run()
    