from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import os
import pickle
import time
from datetime import datetime, timezone
import json

class CloudSync:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/drive.file']
        self.creds = None
        self.service = None
        self.folder_id = None
        self.local_cache_dir = os.path.expanduser('~/InsuranceDashboardCache')
        self.sync_status_file = os.path.join(self.local_cache_dir, 'sync_status.json')
        
        # Ensure cache directory exists
        if not os.path.exists(self.local_cache_dir):
            os.makedirs(self.local_cache_dir)

    def authenticate(self):
        """Handle Google Drive authentication"""
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)
        
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.SCOPES)
                self.creds = flow.run_local_server(port=0)
            
            with open('token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)

        self.service = build('drive', 'v3', credentials=self.creds)
        self._ensure_app_folder_exists()

    def _ensure_app_folder_exists(self):
        """Create or get the application folder in Google Drive"""
        folder_name = 'InsuranceDashboard'
        
        # Search for an existing folder
        results = self.service.files().list(
            q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'",
            spaces='drive',
            fields='files(id)').execute()
        
        if results['files']:
            self.folder_id = results['files'][0]['id']
        else:
            # Create a new folder
            folder_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            file = self.service.files().create(
                body=folder_metadata, fields='id').execute()
            self.folder_id = file['id']

    def sync_file(self, local_path, file_name):
        """Sync a file between local storage and Google Drive"""
        if not self.service:
            print(f"Skipping sync for {file_name} - running in offline mode")
            return
            
        try:
            print(f"Starting sync for {file_name}")
            # Load existing sync status and get the last synced modification time (defaulting to 0)
            sync_status = self._get_sync_status()
            last_synced_mod_time = sync_status.get(file_name, {}).get('last_modified', 0)
            
            # Get the local file's modification time
            local_modified = os.path.getmtime(local_path)
            print(f"Local file last modified: {datetime.fromtimestamp(local_modified)}")
            
            # Get cloud file modification time (if the file exists)
            cloud_file_id = self._get_file_id(file_name)
            cloud_modified = 0
            if cloud_file_id:
                cloud_file = self.service.files().get(
                    fileId=cloud_file_id,
                    fields='modifiedTime'
                ).execute()
                # Convert the cloud timestamp to a timezone-aware datetime in UTC
                cloud_dt = datetime.strptime(
                    cloud_file['modifiedTime'], '%Y-%m-%dT%H:%M:%S.%fZ'
                ).replace(tzinfo=timezone.utc)
                cloud_modified = cloud_dt.timestamp()
                print(f"Cloud file last modified: {datetime.fromtimestamp(cloud_modified)}")
            
            # Compare the modification times and decide whether to upload or download.
            # Priority: if cloud file exists and is newer than local, download.
            if cloud_file_id and cloud_modified > local_modified:
                print(f"Downloading newer version of {file_name} from cloud")
                self._download_file(cloud_file_id, local_path)
                sync_status[file_name] = {'last_modified': cloud_modified}
            # If the local file is newer than the cloud version, upload it.
            elif local_modified > cloud_modified:
                print(f"Uploading newer version of {file_name} to cloud")
                self._upload_file(local_path, file_name)
                sync_status[file_name] = {'last_modified': local_modified}
            else:
                print(f"No update needed for {file_name}")
            
            # Save updated sync status
            self._save_sync_status(sync_status)
            print(f"Sync completed for {file_name}")
            
        except Exception as e:
            print(f"Error syncing {file_name}: {str(e)}")
            # Continue using local file if sync fails
            pass

    def _get_file_id(self, file_name):
        """Get the ID of a file in Google Drive"""
        results = self.service.files().list(
            q=f"name='{file_name}' and '{self.folder_id}' in parents",
            spaces='drive',
            fields='files(id)').execute()
        files = results.get('files', [])
        return files[0]['id'] if files else None

    def _upload_file(self, local_path, file_name):
        """Upload a file to Google Drive"""
        try:
            print(f"DEBUG: Attempting to upload {file_name}")
            file_metadata = {'name': file_name}
            media = MediaFileUpload(local_path, resumable=True)
            
            # Check if the file exists
            file_id = self._get_file_id(file_name)
            print(f"DEBUG: File ID found: {file_id}")
            
            if file_id:
                # Update the existing file
                print(f"DEBUG: Updating existing file {file_name}")
                result = self.service.files().update(
                    fileId=file_id,
                    body=file_metadata,
                    media_body=media,
                    fields='id'
                ).execute()
                print(f"DEBUG: Update result: {result}")
            else:
                # Create a new file with the parent folder set
                print(f"DEBUG: Creating new file {file_name}")
                file_metadata['parents'] = [self.folder_id]
                result = self.service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id'
                ).execute()
                print(f"DEBUG: Create result: {result}")
        except Exception as e:
            print(f"DEBUG: Error in _upload_file: {str(e)}")
            raise

    def _download_file(self, file_id, local_path):
        """Download a file from Google Drive"""
        request = self.service.files().get_media(fileId=file_id)
        with open(local_path, 'wb') as f:
            downloader = MediaIoBaseDownload(f, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()

    def _get_sync_status(self):
        """Get the sync status from local cache"""
        if os.path.exists(self.sync_status_file):
            with open(self.sync_status_file, 'r') as f:
                return json.load(f)
        return {}

    def _save_sync_status(self, status):
        """Save the sync status to local cache"""
        with open(self.sync_status_file, 'w') as f:
            json.dump(status, f)
