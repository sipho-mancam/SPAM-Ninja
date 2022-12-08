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
        self.threads = []
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
                threads = service.users().threads().list(userId='me', labelIds=['INBOX']).execute().get('threads', [])
                for t in threads:
                    thr = self.service_obj.users().threads().get(userId='me', id=t['id']).execute()
                    self.threads.append(thr)
            except HttpError as error:
                print(F'An error occurred: {error}')
        else:
            raise HttpError('An error occurred: {error}')
        
        
    def flag_spam(self, thread, labels={
                'addLabelIds':['SPAM'],
                'removeLabelIds':['INBOx'],
            }):
        return self.modify_labels(labels.get('addLabelIds'), labels.get('removeLabelIds'), thread.get('id'))

    def modify_labels(self, add_labels=[], remove_label=[], thread={'id':''}):
        try:
            labels = {
                'addLabelIds':add_labels,
                'removeLabelIds':remove_label,
            }
            self.service_obj.users().threads().modify(userId='me', id=thread['id'], body=labels).execute()
        except HttpError as he:
            print(self.create_label())
            for l in add_labels:
                print(self.create_label(label_name=l))

            return self.modify_labels(add_labels, remove_label, thread)
        
    def create_label(self, label_name:str='MARKED'):
        label={
            'id':label_name.upper(),
            'name':label_name,
            'messageListVisibility':'show',
            'labelListVisibility': 'labelShow',
            'type':'user',
            'color':{
                "textColor": "#ffffff",
                "backgroundColor": "#434343"
            }
        }
        try:
            self.service_obj.users().labels().create(userId='me', body=label).execute()
        except HttpError as he:
            # print(he.arg)
            return False

    #############################################################
    # Helper Methods to decode and parse message to normal text.#
    #############################################################

    def  aggregate_thread_messages(self, thread)->str:
        messages = thread['messages'] # a litst of message objects.
        res_data = '' 
        for message in messages:
            try:
                res_data += self.get_message(message)
                res_data = self.clean_string(res_data)

            except ValueError as ve:
                print(ve)
        
        thread_data = {
            'id':thread['id'],
            'text': res_data
        }
        return thread_data

    def clean_string(self, s:str)->str:
        s = s.replace('\n', '')
        s = s.replace('\r\n', '')
        s = s.replace('\r', '')
        s = s.replace('\t', '')
        s = s.replace('\r', '')
        s = s.replace('(  )', '')
        s = re.sub(r'http\S+', '', s)
        return s



    def get_message(self, msg_obj)->str:
        payload = msg_obj['payload']
        res = ''
        # check mime type, if it's a single message we extract body, otherwise extract the parts
        if re.match(r'multipart',payload['mimeType'].lower()) is not None:
            # is multipart, let's combine the parts.
            for data in payload['parts']:
                # pprint.pprint(data)
                text = self.decode_message(data['body'].get('data'))
                # check if it's html based text
                if not isinstance(text, Exception):
                    if self.is_html(text):
                        actual_msg = self.extract_data_4rm_html(text)
                        res += actual_msg
                    else:
                        res += text
                    return res
                else:
                    raise ValueError("Message Could Not be docoded: {e}" );
        else:
            text = self.decode_message(payload['body'].get('data'))
            
            if not isinstance(text, Exception):
                    if self.is_html(text):
                        actual_msg = self.extract_data_4rm_html(text)
                        res += actual_msg
                    else:
                        res += text
                    return res
            else:
                raise ValueError("Message Could Not be docoded: {e}" );

    def decode_message(self, message:str)->str:     
        try:
            dec = base64.urlsafe_b64decode(message)
            dec = dec.decode('utf-8')
            return dec
        except Exception as e:
            print(F'There was an error: {e}')
            return e
    
    def is_html(self, message:str)->bool:
        message = message.strip()
        res = re.match(r'<.*?>', message)
        if res is not None:
            return True    
        else:
            if re.match(r'<![A-Za-z0-9].*?', message) is not None:
                return True 
            return False
    
    def extract_data_4rm_html(self, message:str)->str:
        soup = BeautifulSoup(message, 'lxml')
        text = soup.text
        return text

    def run(self):
        # self.read_threads()
        """
        1. Read the threads, and get all the messages inside threads and the clean them up
        2. Run the messages in a thread collectively through the classifier(to build ...)TODO,
        3. Flag the Thread either as SPAM or None SPAM,
        4. Repeat for all the thraeds.
        """
        self.read_threads() # This will read new threads and store them.
        for thread in self.threads:
            t = self.aggregate_thread_messages(thread) # this method will go through the thread and combine all the messages into a single string
            # res = self.classifer.is_spam(thread)
            print(t['text'], end='')
            res = False
            if res:
                self.flag_spam(t)
            # mark the thread as marked.
            # print(self.modify_labels(['CHECKED'], [], t)) # mark this thread as checked, so that we filter out all threads we've checked
            




gApi = GMailAPI(SCOPES, 'spam-ninja-creds.json')


if __name__ == '__main__':
    gApi.run()
    