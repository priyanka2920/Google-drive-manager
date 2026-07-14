# Drive Manager

A lightweight Streamlit app for searching, previewing, and downloading files from Google Drive.

## Features

- 🔐 Google OAuth 2.0 login (read-only Drive access), with automatic token refresh
- 🔍 Search files by name, with a MIME-type filter dropdown
- 📊 Dashboard stats — total files scanned, storage used, and counts by PDF/image/video
- 👀 Inline previews for images, audio, video, and text files
- ⬇️ On-demand downloads — files are only fetched from Drive when you click "Load file," not automatically
- ⚡ Search is gated behind a form and results are cached per session, so the Drive API isn't hit on every keystroke or rerun

## Project structure

```
drive_manager/
├── app.py              # Streamlit UI and app flow
├── auth.py             # Google OAuth authentication and token management
├── drive_service.py     # Google Drive API wrapper (search, download, stats)
├── config.py            # Shared constants (scopes, file paths, limits)
├── assets/
│   └── styles.css       # Optional custom styling
├── credentials.json      # Your Google OAuth client secret (not included — see setup)
└── requirements.txt
```

## Prerequisites

- Python 3.9+
- A Google Cloud project with the **Google Drive API** enabled
- An OAuth 2.0 Client ID (Desktop app type) downloaded as `credentials.json`

## Setup

### 1. Clone / copy the project files

Place `app.py`, `auth.py`, `drive_service.py`, and `config.py` in the same directory.

### 2. Create a virtual environment and install dependencies

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

`requirements.txt`:
```
streamlit
google-api-python-client
google-auth-httplib2
google-auth-oauthlib
```

### 3. Get Google Drive API credentials

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a project (or select an existing one).
3. Enable the **Google Drive API** under APIs & Services → Library.
4. Go to APIs & Services → Credentials → Create Credentials → OAuth client ID.
5. Choose **Desktop app** as the application type.
6. Download the resulting JSON file, rename it to `credentials.json`, and place it in the project root.

### 4. (Optional) Add styling

Create `assets/styles.css` if you want custom CSS. The app will skip loading it if the file doesn't exist.

## Running the app

```bash
streamlit run app.py
```

On first run, a browser window will open asking you to log in and grant read-only Drive access. After granting access, a `token.json` file is created locally so you won't be prompted again unless the token is revoked or deleted.

## Configuration

Edit `config.py` to adjust:

| Setting | Purpose | Default |
|---|---|---|
| `SCOPES` | Google API permission scope | Drive read-only |
| `SUPPORTED_MIME_TYPES` | File types shown in search/filter | PDF, JPEG, PNG, DOCX, DOC, MP3, MP4, TXT |
| `DASHBOARD_SCAN_LIMIT` | Max files scanned for dashboard stats | 500 |
| `MAX_PREVIEW_DOWNLOAD_BYTES` | Max file size allowed for inline preview/download | 100 MB |

## Security notes

- `credentials.json` and `token.json` contain sensitive secrets — **do not commit them to version control**. Add both to `.gitignore`.
- The app only requests `drive.readonly` access; it cannot modify or delete files in your Drive.
- Files above `MAX_PREVIEW_DOWNLOAD_BYTES` are not loaded into memory — the app will show a notice instead.

## Troubleshooting

| Issue | Fix |
|---|---|
| `Missing credentials.json` error on launch | Download OAuth credentials from Google Cloud Console (see Setup step 3) and place the file in the project root. |
| Browser doesn't open for login | Check your firewall/port settings; `run_local_server(port=0)` picks a random free local port. |
| "Drive search failed" error | Usually a transient API/network issue, or an expired token — delete `token.json` and rerun to force re-authentication. |
| Stats look incomplete on a very large Drive | Increase `DASHBOARD_SCAN_LIMIT` in `config.py` (higher values mean slower stat loads). |
