from googleapiclient.discovery import build
from google.oauth2 import service_account
import os
import csv

# Define the scope and load the credentials
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']
SERVICE_ACCOUNT_FILE = 'pmf-project-449613-2898ccb0ff22.json'  # Replace with the path to your credentials JSON file

creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# Build the Drive API service
service = build('drive', 'v3', credentials=creds)

def list_files_in_folder(folder_id):
    """List all files in a Google Drive folder and its subfolders."""
    query = f"'{folder_id}' in parents and trashed = false"
    results = service.files().list(q=query, fields="nextPageToken, files(id, name, mimeType, parents)").execute()
    items = results.get('files', [])

    all_files = []

    for item in items:
        if item['mimeType'] == 'application/vnd.google-apps.folder':
            # If the item is a folder, recursively list its contents
            #print(f"Found folder: {item['name']} (ID: {item['id']})")
            all_files.extend(list_files_in_folder(item['id']))
        else:
            # If the item is a file, add it to the list
            #           print(f"Found file: {item['name']} (ID: {item['id']}, MIME type: {item['mimeType']})")
            all_files.append({
                'id': item['id'],
                'name': item['name'],
                'mimeType': item['mimeType'],
                'parents': item['parents']
            })

    return all_files

def extract_sheet_ids(folder_id):
    """Extract Google Sheet IDs from a folder and its subfolders."""
    
    # print the folder ID and folder name
    folder = service.files().get(fileId=folder_id, fields="name").execute()
    print(f"Folder ID: {folder_id}")
    print(f"Folder Name: {folder['name']}")
    
    # List all files in the folder
    files = list_files_in_folder(folder_id)
    print(f"Total files found: {len(files)}")
    
    sheet_files = [file for file in files if file['mimeType'] == 'application/vnd.google-apps.spreadsheet']
    print(f"Total Google Sheets found: {len(sheet_files)}")

    sheet_info_list = []
    for sheet in sheet_files:
        sheet_info = {
            'id': sheet['id'],
            'name': sheet['name'],
            'parents': sheet['parents']
        }
        sheet_info_list.append(sheet_info)

    return sheet_info_list

if __name__ == "__main__":
    # Replace with your Google Drive folder ID
    start_folder_id = '1ftV0-vktmXabnRlknw2UU7yPXmrOsM4l'

    # Extract Google Sheet IDs
    sheet_info_list = extract_sheet_ids(start_folder_id)
        
    # Output the extracted information to a CSV file
    output_file = 'data/google_id.csv'
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['ID', 'Name'])
        for sheet_info in sheet_info_list:
            writer.writerow([sheet_info['id'], sheet_info['name']])

    print(f"Google Sheet IDs and names have been written to {output_file}")