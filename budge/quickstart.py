#!/usr/bin/env python3
from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from apiclient.http import MediaFileUpload
from apiclient import errors
import datetime
import os
import pdb
from pprint import pformat as pf

class GFile(dict):
    # represents a File or Directory in GDrive, created
    # by GDrive.list_folder.
    folder_mimeType = 'application/vnd.google-apps.folder'
    fields_str = 'createdTime,id,md5Checksum,mimeType,modifiedTime,name,parents,size,trashed'
    #fields_str = '*'
    DATE_TIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'

    def __init__(self, fields):
        # All fields available as attrs, plus fields 'isFolder'(boolean). created_time and
        # modified_time are datetime's. 'parent' is an id, self.parents[0]
        try:
            for key,val in fields.items():
                setattr(self, key, val)
            if 'size' not in fields:
                setattr(self, 'size', 0)
            self.isFolder = fields['mimeType'] == self.folder_mimeType
            self.createdTime = datetime.datetime.strptime(self.createdTime, self.DATE_TIME_FORMAT)
            self.modifiedTime = datetime.datetime.strptime(self.modifiedTime, self.DATE_TIME_FORMAT)
            self.parent = self.parents[0]
        except Exception as ex:
            print('GFile constructor caught: {}'.format(ex))

    def __repr__(self):
        print('creating string....')
        return '\n'.join(['{}:{}'.format(key,val) for key,val in self.__dict__.items()])

class GDrive(object):

    # If modifying these scopes, delete the file token.pickle.
    scopes = ['https://www.googleapis.com/auth/drive']
    
    def __init__(self):
        creds = None
        # token.pickle stores the user's access and refresh tokens, created
        # when the authorization flow completes for the first time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.scopes)
                creds = flow.run_local_server(port=0)
            # Save creds for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        self.service = build('drive', 'v3', credentials=creds)

    def file_upload(self, src_file_path, gdrive_file_name, parent_folder_id='root'):
        # upload file, creatint it if doesn't exist, else overwriting it.
        file_folder = self.folder_list(parent_folder_id)
        try:
            return self.service.files().update(
                fileId = [gfile.id for gfile in file_folder if not gfile.isFolder and gfile.name == gdrive_file_name][0],
                media_body=MediaFileUpload(src_file_path, mimetype='text/plain'),
                fields='id').execute()['id']
        except Exception as ex:
            print('{}'.format(ex))
            return self.service.files().create(
                body={'name': gdrive_file_name, 'parents':[parent_folder_id]},
                media_body=MediaFileUpload(src_file_path, mimetype='text/plain'),
                fields='id').execute()['id']
        
    def folder_get(self, folder_name, parent_folder_id='root'):
        # Return id of folder, creating it if doesn't exist
        try:
            return [gfile for gfile in self.folder_list(parent_folder_id) if \
                     gfile.isFolder and gfile.name == folder_name][0].id
        except:
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder' }
            if parent_folder_id:
                file_metadata['parents'] = [parent_folder_id]
            return self.service.files().create(body=file_metadata, fields='id').execute().get('id')


    def folder_list(self, folder_id=None, fields=GFile.fields_str, trashed=False):
        """Return files/folders in folder as GFile objects.

        Args:
            folder_id: ID of the folder to print files from.

        fields:
            fields to fetch for each file.
        trashed:
            iff False and 'trashed' in GFile.fields_str, exclude trashed files
        """
        if folder_id is None:
            folder_id = 'root'
        page_token = None
        g_files = []
        try:
            while True:
                response = self.service.files().list(
                    pageToken=page_token,
                    # pageSize=100 ...use default
                    fields='nextPageToken, files({})'.format(fields),  # '*' gives all fields
                    q="'{}' in parents".format(folder_id)).execute()  # '*' retrieves all fields
                for file_attrs in response.get('files', []):
                    if trashed or not file_attrs.get('trashed', False):
                        g_files.append(GFile(file_attrs))                  
                page_token = response.get('nextPageToken', None)
                if page_token is None:
                    break
        except Exception as ex:
            print('GDrive.list_folder() caught: {}'.format(ex))
            return []
        return g_files

def main():
    gdrive = GDrive()
    backup_files = ['~/.budget/amazon_cache.json',
                    '~/.budget/amazon_exceptions.json',
                    '~/.budget/emoney_cache.json',
                    '~/.budget/emoney_exceptions.json']
    budget_dir_id = gdrive.folder_get('budget')
    for file in backup_files:
        gdrive.file_upload(os.path.expanduser(file), os.path.basename(file), budget_dir_id)
    gdrive.file_upload(os.path.expanduser('~/.budget/report'), 'budget_report')

if __name__ == '__main__':
    main()
