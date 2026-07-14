import io

import streamlit as st
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

from auth import get_fresh_credentials
from config import DASHBOARD_SCAN_LIMIT, SUPPORTED_MIME_TYPES


def _escape(value: str) -> str:
    """Escape single quotes so user input can't break/inject into a Drive query."""
    return value.replace("\\", "\\\\").replace("'", "\\'")


class GoogleDriveService:

    def __init__(self):
        creds = get_fresh_credentials()
        self.service = build('drive', 'v3', credentials=creds)

    def search_files(self, query='', file_type='All', page_size=20):
        mime_query = ' or '.join(
            f"mimeType='{mime}'" for mime in SUPPORTED_MIME_TYPES.keys()
        )
        search_query = f"({mime_query})"

        if query:
            search_query += f" and name contains '{_escape(query)}'"

        if file_type != 'All':
            search_query += f" and mimeType='{_escape(file_type)}'"

        try:
            results = self.service.files().list(
                q=search_query,
                spaces='drive',
                fields='files(id,name,mimeType,size,createdTime,modifiedTime)',
                pageSize=page_size,
                orderBy='modifiedTime desc',
            ).execute()
        except HttpError as e:
            st.error(f"Drive search failed: {e}")
            return []

        return results.get('files', [])

    def download_file(self, file_id) -> io.BytesIO:
        request = self.service.files().get_media(fileId=file_id)
        file_stream = io.BytesIO()
        downloader = MediaIoBaseDownload(file_stream, request)

        done = False
        while not done:
            _, done = downloader.next_chunk()

        file_stream.seek(0)
        return file_stream

    def get_dashboard_stats(self):
        """Aggregate stats over up to DASHBOARD_SCAN_LIMIT files, paginating as needed."""

        files = []
        page_token = None

        try:
            while len(files) < DASHBOARD_SCAN_LIMIT:
                results = self.service.files().list(
                    pageSize=min(100, DASHBOARD_SCAN_LIMIT - len(files)),
                    fields='nextPageToken, files(id,mimeType,size)',
                    pageToken=page_token,
                ).execute()

                files.extend(results.get('files', []))
                page_token = results.get('nextPageToken')

                if not page_token:
                    break
        except HttpError as e:
            st.error(f"Could not load dashboard stats: {e}")
            return {
                'total_files': 0,
                'storage_gb': 0,
                'pdf_count': 0,
                'image_count': 0,
                'video_count': 0,
            }

        total_storage = 0
        pdf_count = 0
        image_count = 0
        video_count = 0

        for file in files:
            total_storage += int(file.get('size', 0) or 0)
            mime = file.get('mimeType', '')

            if mime == 'application/pdf':
                pdf_count += 1
            elif mime.startswith('image/'):
                image_count += 1
            elif mime.startswith('video/'):
                video_count += 1

        return {
            'total_files': len(files),
            'storage_gb': round(total_storage / (1024 ** 3), 2),
            'pdf_count': pdf_count,
            'image_count': image_count,
            'video_count': video_count,
        }