# Google Drive Integration for Kquires

This document explains how to set up and use the Google Drive integration for file uploads in the Kquires application.

## Overview

The Google Drive integration allows users to upload files with their articles, which are automatically stored in Google Drive instead of the local server. This provides:

- **Cloud Storage**: Files are stored in Google Drive, reducing server storage requirements
- **File Management**: Admin interface to view and manage all uploaded files
- **Direct Access**: Users can view and download files directly from Google Drive
- **Backup**: Files are automatically backed up in Google Drive

## Setup Instructions

### 1. Google Cloud Console Setup

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Drive API:
   - Go to "APIs & Services" > "Library"
   - Search for "Google Drive API"
   - Click on it and press "Enable"

### 2. Create OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client IDs"
3. Choose "Web application" as the application type
4. Fill in the details:
   - Name: `Kquires Drive Integration`
   - Authorized redirect URIs: `http://localhost:8080/`
5. Click "Create"
6. Copy the Client ID and Client Secret

### 3. Create Google Drive Folder

1. Go to [Google Drive](https://drive.google.com/)
2. Create a new folder for Kquires files (e.g., "Kquires Files")
3. Copy the folder ID from the URL (the long string after `/folders/`)
4. Your folder is already set up at: [https://drive.google.com/drive/folders/11LnYmvZn4TBxOManQMjYih5_skV9kCeo](https://drive.google.com/drive/folders/11LnYmvZn4TBxOManQMjYih5_skV9kCeo)

### 4. Environment Configuration

Add the following variables to your `.env` file:

```env
# Google Drive Configuration
GOOGLE_DRIVE_CLIENT_ID=375899622327-ebdae4439cjr5e94j07v8htnmt2fiovk.apps.googleusercontent.com
GOOGLE_DRIVE_CLIENT_SECRET=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
GOOGLE_DRIVE_FOLDER_ID=11LnYmvZn4TBxOManQMjYih5_skV9kCeo
GOOGLE_DRIVE_SCOPES=https://www.googleapis.com/auth/drive.file
```

**Important Notes:**
- The Client ID and Client Secret are already configured for your project
- The folder ID `11LnYmvZn4TBxOManQMjYih5_skV9kCeo` points to your Google Drive folder
- The scope `https://www.googleapis.com/auth/drive.file` allows the app to create, read, update, and delete files that the app has created

### 6. Install Dependencies

The required packages are already added to `requirements/base.txt`:

```
google-api-python-client==2.149.0
google-auth-httplib2==0.2.0
google-auth-oauthlib==1.2.1
```

Install them with:
```bash
pip install -r requirements/base.txt
```

### 7. Database Migration

Run the migration to add Google Drive fields to the Article model:

```bash
python manage.py migrate articles
```

## Features

### 1. Automatic File Upload

When users upload files with articles, they are automatically:
- Uploaded to Google Drive
- Stored with metadata (file ID, filename, size, links)
- Linked to the article in the database

### 2. File Manager Interface

Access the File Manager through:
- **Sidebar**: Click "File Manager" in the navigation
- **URL**: `/articles/files/`

Features:
- View all uploaded files
- See file statistics (total files, total size)
- Download files directly from Google Drive
- View files in Google Drive
- Delete files from Google Drive
- Get detailed file information

### 3. Article Integration

Files uploaded with articles are displayed:
- In the article list table (with Google Drive download icon)
- In the article detail page (with file information and download links)
- In the file manager interface

### 4. Admin Features

The File Manager provides:
- **Statistics Dashboard**: Total files and storage used
- **File List**: Paginated list of all uploaded files
- **File Actions**: View, download, delete files
- **File Information**: Detailed metadata for each file

## Usage

### For Users

1. **Upload Files**: When creating or editing articles, attach files using the file input
2. **View Files**: Files are automatically displayed in article detail pages
3. **Download Files**: Click the download button to get files from Google Drive

### For Administrators

1. **Access File Manager**: Use the sidebar navigation or go to `/articles/files/`
2. **Monitor Storage**: View total files and storage usage
3. **Manage Files**: Delete files, view file information, or access files directly

## File Structure

```
kquires/
├── utils/
│   └── google_drive_service.py    # Google Drive service class
├── articles/
│   ├── models.py                  # Updated Article model with Google Drive fields
│   ├── views.py                   # File manager views
│   ├── urls.py                    # File manager URLs
│   └── templates/
│       └── articles/
│           └── file_manager.html  # File manager interface
└── templates/
    └── pages/
        └── layout/
            └── sidebar.html       # Updated with File Manager link
```

## API Endpoints

- `GET /articles/files/` - File Manager interface
- `POST /articles/files/delete/<article_id>/` - Delete file from Google Drive
- `GET /articles/files/info/<article_id>/` - Get file information

## Security Considerations

1. **Service Account**: Uses service account authentication (no user login required)
2. **Scoped Access**: Limited to files created by the application
3. **Environment Variables**: Sensitive data stored in environment variables
4. **File Permissions**: Only the service account can access uploaded files

## Troubleshooting

### Common Issues

1. **Authentication Failed**
   - Check if `credentials.json` file exists and is readable
   - Verify the service account has access to the Google Drive folder
   - Ensure the Google Drive API is enabled

2. **File Upload Failed**
   - Check internet connection
   - Verify folder ID is correct
   - Ensure service account has write permissions to the folder

3. **File Not Found**
   - Check if the file was actually uploaded to Google Drive
   - Verify the file ID is stored correctly in the database

### Debug Mode

Enable debug logging by adding to your Django settings:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'google_drive.log',
        },
    },
    'loggers': {
        'kquires.utils.google_drive_service': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```

## Future Enhancements

Potential improvements for the Google Drive integration:

1. **File Versioning**: Track file versions and changes
2. **Bulk Operations**: Upload/download multiple files at once
3. **File Sharing**: Share files with specific users
4. **Storage Quotas**: Monitor and enforce storage limits
5. **File Categories**: Organize files by type or category
6. **Search**: Search files by name, type, or content
7. **Backup**: Automatic backup of local files to Google Drive

## Support

For issues or questions regarding the Google Drive integration:

1. Check the troubleshooting section above
2. Review the Django logs for error messages
3. Verify all environment variables are set correctly
4. Test the Google Drive API connection independently

## License

This integration follows the same license as the main Kquires application.
