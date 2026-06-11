#!/usr/bin/env python3
"""
Script:     list_rooms_under_parent.py
Purpose:    List all subfolders directly under a specified parent folder in Google Drive.
"""

from googleapiclient.discovery import build
from google.oauth2 import service_account

SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']
SERVICE_ACCOUNT_FILE = 'pmf-project-449613-2898ccb0ff22.json'

PARENT_ID = '1ftV0-vktmXabnRlknw2UU7yPXmrOsM4l'  # Packing Inventory-Mattinson

creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=creds)

query = f"'{PARENT_ID}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
results = drive_service.files().list(q=query, fields="files(id, name)", pageSize=1000).execute()
folders = results.get('files', [])

print(f"Rooms under parent folder '{PARENT_ID}':")
for folder in sorted(folders, key=lambda f: f['name']):
    print(f"  {folder['name']:35} {folder['id']}")
