#!/usr/bin/env python3
"""
Script:     extract_room_colors.py
Author:     Mike & ChatGPT
Version:    1.2.0
Purpose:    Extracts room name, room ID, and room color from all immediate subfolders
            of a given Google Drive parent folder. Displays color-coded output with contrast
            and writes to 'room_details.txt'.

Usage:
    python extract_room_colors.py --parent-id <FOLDER_ID>
"""

import os
import argparse
from googleapiclient.discovery import build
from google.oauth2 import service_account
from colorama import Fore, Back, Style, init as colorama_init

# --- Google API Setup ---
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']
SERVICE_ACCOUNT_FILE = 'pmf-project-449613-2898ccb0ff22.json'

creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=creds)

# --- Color Setup ---
colorama_init()

# Foreground colors (text color)
color_to_fore = {
    'red': Fore.RED,
    'green': Fore.GREEN,
    'blue': Fore.BLUE,
    'yellow': Fore.YELLOW,
    'orange': Fore.LIGHTRED_EX,
    'purple': Fore.MAGENTA,
    'cyan': Fore.CYAN,
    'pink': Fore.LIGHTMAGENTA_EX,
    'brown': Fore.LIGHTYELLOW_EX,
    'black': Fore.BLACK,
    'white': Fore.WHITE,
    'gray': Fore.LIGHTBLACK_EX
}

# Matching background colors for better contrast
bg_for_fore = {
    'black': Back.WHITE,
    'blue': Back.WHITE,
    'red': Back.WHITE,
    'green': Back.WHITE,
    'purple': Back.WHITE,
    'gray': Back.WHITE,
    'white': Back.BLACK,
    'yellow': Back.BLACK,
    'cyan': Back.BLACK,
    'orange': Back.BLACK,
    'pink': Back.BLACK,
    'brown': Back.BLACK
}

# --- Logic ---
def list_subfolders(folder_id):
    """Return a list of all immediate subfolders in a given folder."""
    query = f"'{folder_id}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    return results.get('files', [])

def parse_folder_name(folder_name):
    """Split a folder name like 'Dining Room-DR-Green' into its parts."""
    parts = folder_name.split('-')
    if len(parts) >= 3:
        return parts[0].strip(), parts[1].strip(), parts[2].strip()
    return folder_name.strip(), '', ''

def extract_room_details(parent_folder_id):
    subfolders = list_subfolders(parent_folder_id)
    details = []
    for folder in subfolders:
        room_name, room_id, room_color = parse_folder_name(folder['name'])
        details.append((room_name, room_id, room_color))
    return details

# --- Main Execution ---
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Extract room names, IDs, and colors from Google Drive folders")
    parser.add_argument('--parent-id', required=True, help='Parent folder ID containing room subfolders')
    args = parser.parse_args()

    output_path = 'room_details.txt'
    room_details = extract_room_details(args.parent_id)

    with open(output_path, 'w') as f:
        for room_name, room_id, room_color in room_details:
            color = room_color.lower()
            fore = color_to_fore.get(color, Fore.WHITE)
            back = bg_for_fore.get(color, Back.BLACK)
            print(f"{room_name:20} {room_id:5} {fore}{back}{room_color}{Style.RESET_ALL}")
            f.write(f"{room_name},{room_id},{room_color}\n")

    print(f"\n[OK] Extracted {len(room_details)} rooms to {output_path}")
