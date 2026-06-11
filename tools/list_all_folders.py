#!/usr/bin/env python3
"""
Script: list_all_folders.py
Purpose: List all folders owned by the service account.
"""

from googleapiclient.discovery import build
from google.oauth2 import service_account

SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']
SERVICE_ACCOUNT_FILE = 'pmf-project-449613-2898ccb0ff22.json'

creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=creds)

query = "mimeType = 'application/vnd.google-apps.folder' and trashed = false"
results = drive_service.files().list(q=query, fields="files(id, name)").execute()
folders = results.get('files', [])

print("Folders owned by service account:")
for folder in folders:
    print(f"{folder['name']:40} {folder['id']}")
