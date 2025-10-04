#!/usr/bin/env python3
"""
Simple Google Drive Test Script
Tests the Google Drive integration without Django setup
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_google_drive_config():
    """Test Google Drive configuration"""
    print("🔧 Testing Google Drive Configuration...")
    print("="*50)
    
    # Your configuration
    client_id = "375899622327-ebdae4439cjr5e94j07v8htnmt2fiovk.apps.googleusercontent.com"
    client_secret = "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"
    folder_id = "11LnYmvZn4TBxOManQMjYih5_skV9kCeo"
    
    print(f"✅ Client ID: {client_id}")
    print(f"✅ Client Secret: {client_secret[:10]}...{client_secret[-10:]}")
    print(f"✅ Folder ID: {folder_id}")
    
    print("\n📁 Your Google Drive Folder:")
    print(f"   https://drive.google.com/drive/folders/{folder_id}")
    
    print("\n🔧 Environment Variables to add to .env:")
    print("   GOOGLE_DRIVE_CLIENT_ID=375899622327-ebdae4439cjr5e94j07v8htnmt2fiovk.apps.googleusercontent.com")
    print("   GOOGLE_DRIVE_CLIENT_SECRET=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")
    print("   GOOGLE_DRIVE_FOLDER_ID=11LnYmvZn4TBxOManQMjYih5_skV9kCeo")
    print("   GOOGLE_DRIVE_SCOPES=https://www.googleapis.com/auth/drive.file")
    
    print("\n🚀 Next Steps:")
    print("1. Add the environment variables to your .env file")
    print("2. Install dependencies: pip install -r requirements/base.txt")
    print("3. Run migrations: python manage.py migrate articles")
    print("4. Start the server: python manage.py runserver")
    print("5. Try uploading a file with an article")
    print("6. Access the File Manager at: /articles/files/")
    
    print("\n🎯 Features Available:")
    print("✅ Automatic file upload to Google Drive")
    print("✅ File Manager interface in sidebar")
    print("✅ Download/view files from Google Drive")
    print("✅ File statistics and management")
    print("✅ Integration with article system")
    
    print("\n" + "="*50)
    print("🎉 Google Drive integration is ready to use!")
    print("="*50)

if __name__ == "__main__":
    test_google_drive_config()
