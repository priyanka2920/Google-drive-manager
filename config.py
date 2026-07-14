SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

TOKEN_FILE = 'token.json'
CREDENTIALS_FILE = 'credentials.json'

SUPPORTED_MIME_TYPES = {
    'application/pdf': '.pdf',
    'image/jpeg': '.jpg',
    'image/png': '.png',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
    'application/msword': '.doc',
    'audio/mpeg': '.mp3',
    'video/mp4': '.mp4',
    'text/plain': '.txt',
}

# Cap on how many files we scan for dashboard stats.
# Keeps the stats call cheap; raise if you need exact totals on huge drives.
DASHBOARD_SCAN_LIMIT = 500

# Max file size (bytes) we'll download inline for preview/download in the UI.
MAX_PREVIEW_DOWNLOAD_BYTES = 100 * 1024 * 1024  # 100 MB