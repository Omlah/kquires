#!/usr/bin/env python3
"""
Google Drive Setup Script for Kquires
This script helps set up the Google Drive integration with your credentials.
"""

import os
import sys
import django
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from kquires.utils.google_drive_service import google_drive_service

def test_google_drive_connection():
    """Test the Google Drive connection"""
    print("🔧 Testing Google Drive connection...")
    
    try:
        # Test authentication
        if google_drive_service.authenticate():
            print("✅ Google Drive authentication successful!")
            
            # Test folder access
            if google_drive_service.folder_id:
                print(f"📁 Using folder ID: {google_drive_service.folder_id}")
                
                # Try to get folder info
                try:
                    folder_info = google_drive_service.service.files().get(
                        fileId=google_drive_service.folder_id,
                        fields='id,name,webViewLink'
                    ).execute()
                    
                    print(f"📂 Folder name: {folder_info.get('name', 'Unknown')}")
                    print(f"🔗 Folder URL: {folder_info.get('webViewLink', 'N/A')}")
                    print("✅ Folder access confirmed!")
                    
                except Exception as e:
                    print(f"❌ Error accessing folder: {str(e)}")
                    print("💡 Make sure the folder ID is correct and the app has access to it.")
                    return False
            else:
                print("❌ No folder ID configured")
                return False
                
            return True
        else:
            print("❌ Google Drive authentication failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error during setup: {str(e)}")
        return False

def show_setup_instructions():
    """Show setup instructions"""
    print("\n" + "="*60)
    print("🚀 GOOGLE DRIVE INTEGRATION SETUP")
    print("="*60)
    
    print("\n📋 Your Configuration:")
    print(f"   Client ID: {google_drive_service.client_id}")
    print(f"   Folder ID: {google_drive_service.folder_id}")
    print(f"   Scopes: {', '.join(google_drive_service.scopes)}")
    
    print("\n🔧 Setup Steps:")
    print("1. Make sure your .env file contains:")
    print("   GOOGLE_DRIVE_CLIENT_ID=375899622327-ebdae4439cjr5e94j07v8htnmt2fiovk.apps.googleusercontent.com")
    print("   GOOGLE_DRIVE_CLIENT_SECRET=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")
    print("   GOOGLE_DRIVE_FOLDER_ID=11LnYmvZn4TBxOManQMjYih5_skV9kCeo")
    
    print("\n2. Run the Django server:")
    print("   python manage.py runserver")
    
    print("\n3. Try uploading a file with an article - the first time will open a browser")
    print("   for OAuth authentication.")
    
    print("\n4. After authentication, files will be automatically uploaded to Google Drive!")
    
    print("\n📁 Your Google Drive Folder:")
    print("   https://drive.google.com/drive/folders/11LnYmvZn4TBxOManQMjYih5_skV9kCeo")
    
    print("\n🎯 File Manager:")
    print("   Access the file manager at: /articles/files/")
    print("   Or use the 'File Manager' link in the sidebar")

def main():
    """Main setup function"""
    print("🔧 Kquires Google Drive Integration Setup")
    print("="*50)
    
    # Test connection
    if test_google_drive_connection():
        print("\n🎉 Setup completed successfully!")
        print("✅ Google Drive integration is ready to use!")
    else:
        print("\n❌ Setup failed. Please check the configuration.")
        print("💡 Make sure your .env file is properly configured.")
    
    # Show instructions
    show_setup_instructions()
    
    print("\n" + "="*60)
    print("📚 For more information, see: GOOGLE_DRIVE_INTEGRATION.md")
    print("="*60)

if __name__ == "__main__":
    main()
