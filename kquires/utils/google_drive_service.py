"""
Google Drive Service for file uploads and management
"""
import os
import io
import json
from typing import Optional, Dict, Any
from django.conf import settings
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import logging

logger = logging.getLogger(__name__)


class GoogleDriveService:
    """Service class for Google Drive operations"""
    
    def __init__(self):
        self.service = None
        self.credentials = None
        self.scopes = getattr(settings, 'GOOGLE_DRIVE_SCOPES', [
            'https://www.googleapis.com/auth/drive.file'
        ])
        self.folder_id = getattr(settings, 'GOOGLE_DRIVE_FOLDER_ID', '11LnYmvZn4TBxOManQMjYih5_skV9kCeo')
        
        # OAuth credentials
        self.client_id = getattr(settings, 'GOOGLE_DRIVE_CLIENT_ID', '375899622327-ebdae4439cjr5e94j07v8htnmt2fiovk.apps.googleusercontent.com')
        self.client_secret = getattr(settings, 'GOOGLE_DRIVE_CLIENT_SECRET', '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')
        
        self.credentials_file = getattr(settings, 'GOOGLE_DRIVE_CREDENTIALS_FILE', None)
        self.token_file = 'token.json'
        
    def authenticate(self) -> bool:
        """
        Authenticate with Google Drive API using OAuth credentials
        Returns True if successful, False otherwise
        """
        try:
            # Load existing credentials
            if os.path.exists(self.token_file):
                self.credentials = Credentials.from_authorized_user_file(
                    self.token_file, self.scopes
                )
            
            # If there are no valid credentials, get new ones
            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    self.credentials.refresh(Request())
                else:
                    # Create OAuth flow with client credentials
                    client_config = {
                        "web": {
                            "client_id": self.client_id,
                            "client_secret": self.client_secret,
                            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                            "token_uri": "https://oauth2.googleapis.com/token",
                            "redirect_uris": ["http://localhost:8080/", "http://127.0.0.1:8080/", "urn:ietf:wg:oauth:2.0:oob"]
                        }
                    }
                    
                    flow = InstalledAppFlow.from_client_config(
                        client_config, self.scopes
                    )
                    self.credentials = flow.run_local_server(port=8080)
                
                # Save credentials for next run
                with open(self.token_file, 'w') as token:
                    token.write(self.credentials.to_json())
            
            # Build the service
            self.service = build('drive', 'v3', credentials=self.credentials)
            return True
            
        except Exception as e:
            logger.error(f"Google Drive authentication failed: {str(e)}")
            return False
    
    def upload_file(self, file_content: bytes, filename: str, 
                   mime_type: str = None, folder_id: str = None) -> Dict[str, Any]:
        """
        Upload a file to Google Drive
        
        Args:
            file_content: File content as bytes
            filename: Name of the file
            mime_type: MIME type of the file
            folder_id: ID of the folder to upload to (optional)
            
        Returns:
            Dict containing file_id, web_view_link, and web_content_link
        """
        try:
            if not self.service:
                if not self.authenticate():
                    return {'error': 'Failed to authenticate with Google Drive'}
            
            # Use provided folder_id or default folder
            parent_folder_id = folder_id or self.folder_id
            
            # Prepare file metadata
            file_metadata = {
                'name': filename,
            }
            
            if parent_folder_id:
                file_metadata['parents'] = [parent_folder_id]
            
            # Create media upload
            media = MediaIoBaseUpload(
                io.BytesIO(file_content),
                mimetype=mime_type,
                resumable=True
            )
            
            # Upload file
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,name,webViewLink,webContentLink,size'
            ).execute()
            
            return {
                'file_id': file.get('id'),
                'filename': file.get('name'),
                'web_view_link': file.get('webViewLink'),
                'web_content_link': file.get('webContentLink'),
                'size': file.get('size'),
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Google Drive upload failed: {str(e)}")
            return {'error': f'Upload failed: {str(e)}'}
    
    def delete_file(self, file_id: str) -> Dict[str, Any]:
        """
        Delete a file from Google Drive
        
        Args:
            file_id: ID of the file to delete
            
        Returns:
            Dict containing success status
        """
        try:
            if not self.service:
                if not self.authenticate():
                    return {'error': 'Failed to authenticate with Google Drive'}
            
            self.service.files().delete(fileId=file_id).execute()
            return {'success': True}
            
        except Exception as e:
            logger.error(f"Google Drive delete failed: {str(e)}")
            return {'error': f'Delete failed: {str(e)}'}
    
    def get_file_info(self, file_id: str) -> Dict[str, Any]:
        """
        Get information about a file in Google Drive
        
        Args:
            file_id: ID of the file
            
        Returns:
            Dict containing file information
        """
        try:
            if not self.service:
                if not self.authenticate():
                    return {'error': 'Failed to authenticate with Google Drive'}
            
            file = self.service.files().get(
                fileId=file_id,
                fields='id,name,webViewLink,webContentLink,size,createdTime,modifiedTime'
            ).execute()
            
            return {
                'file_id': file.get('id'),
                'filename': file.get('name'),
                'web_view_link': file.get('webViewLink'),
                'web_content_link': file.get('webContentLink'),
                'size': file.get('size'),
                'created_time': file.get('createdTime'),
                'modified_time': file.get('modifiedTime'),
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Google Drive get file info failed: {str(e)}")
            return {'error': f'Get file info failed: {str(e)}'}
    
    def create_folder(self, folder_name: str, parent_folder_id: str = None) -> Dict[str, Any]:
        """
        Create a folder in Google Drive
        
        Args:
            folder_name: Name of the folder to create
            parent_folder_id: ID of the parent folder (optional)
            
        Returns:
            Dict containing folder information
        """
        try:
            if not self.service:
                if not self.authenticate():
                    return {'error': 'Failed to authenticate with Google Drive'}
            
            # Prepare folder metadata
            folder_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            if parent_folder_id:
                folder_metadata['parents'] = [parent_folder_id]
            
            # Create folder
            folder = self.service.files().create(
                body=folder_metadata,
                fields='id,name,webViewLink'
            ).execute()
            
            return {
                'folder_id': folder.get('id'),
                'folder_name': folder.get('name'),
                'web_view_link': folder.get('webViewLink'),
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Google Drive create folder failed: {str(e)}")
            return {'error': f'Create folder failed: {str(e)}'}


# Global instance
google_drive_service = GoogleDriveService()
