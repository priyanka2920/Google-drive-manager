import os

import streamlit as st

from config import MAX_PREVIEW_DOWNLOAD_BYTES
from drive_service import GoogleDriveService

st.set_page_config(
    page_title='Drive Manager',
    page_icon='📁',
    layout='wide',
)

_css_path = 'assets/styles.css'
if os.path.exists(_css_path):
    with open(_css_path) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


@st.cache_resource
def get_drive_service():
    return GoogleDriveService()


service = get_drive_service()

st.markdown(
    """
    <div style='text-align:center;'>
        <h1 style='color:white;'>Drive Manager</h1>
        <p style='color:#cbd5e1;'>Search your documents with ease</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Dashboard stats are cached for 5 minutes so they aren't recomputed on every rerun.
@st.cache_data(ttl=300)
def load_stats():
    return service.get_dashboard_stats()

stats = load_stats()

stat_cols = st.columns(5)
stat_cols[0].metric('Files scanned', stats['total_files'])
stat_cols[1].metric('Storage (GB)', stats['storage_gb'])
stat_cols[2].metric('PDFs', stats['pdf_count'])
stat_cols[3].metric('Images', stats['image_count'])
stat_cols[4].metric('Videos', stats['video_count'])

# A form batches the text input + selectbox into a single search request,
# instead of re-querying the Drive API on every keystroke.
with st.form('search_form'):
    search_col1, search_col2, search_col3 = st.columns([3, 1, 1])

    with search_col1:
        query = st.text_input(
            'Search',
            placeholder='Search files here...',
            label_visibility='collapsed',
        )

    with search_col2:
        file_type = st.selectbox(
            'Filter',
            options=[
                'All',
                'application/pdf',
                'image/jpeg',
                'image/png',
                'audio/mpeg',
                'video/mp4',
                'text/plain',
            ],
        )

    with search_col3:
        st.write('')
        st.write('')
        submitted = st.form_submit_button('Search', use_container_width=True)

# Results (and the query/filter used to produce them) persist across reruns
# so that clicking a download/preview button doesn't blank the results out.
if submitted or 'files' not in st.session_state:
    st.session_state['files'] = service.search_files(query, file_type)

files = st.session_state['files']

if files:
    st.subheader('Search Results')

    for file in files:
        with st.container(border=True):
            col1, col2, col3 = st.columns([4, 2, 2])

            with col1:
                st.write(f"📄 {file['name']}")
                st.caption(file['mimeType'])

            with col2:
                st.caption(f"Modified: {file.get('modifiedTime', 'N/A')}")

            mime = file['mimeType']
            size = int(file.get('size', 0) or 0)
            cache_key = f"filedata_{file['id']}"

            with col3:
                too_large = size > MAX_PREVIEW_DOWNLOAD_BYTES

                if too_large:
                    st.caption('File too large to preview inline.')
                elif cache_key not in st.session_state:
                    # Nothing is downloaded until the user actually asks for it.
                    if st.button('Load file', key=f"load_{file['id']}", use_container_width=True):
                        with st.spinner('Downloading...'):
                            st.session_state[cache_key] = service.download_file(file['id']).getvalue()
                        st.rerun()
                else:
                    st.download_button(
                        label='Download',
                        data=st.session_state[cache_key],
                        file_name=file['name'],
                        use_container_width=True,
                        key=f"dl_{file['id']}",
                    )

            # Only render a preview once the bytes have actually been fetched.
            if cache_key in st.session_state:
                data = st.session_state[cache_key]

                if mime == 'application/pdf':
                    st.caption('PDF loaded — use the Download button above to save it.')
                elif mime.startswith('image/'):
                    st.image(data)
                elif mime.startswith('audio/'):
                    st.audio(data)
                elif mime.startswith('video/'):
                    st.video(data)
                elif mime == 'text/plain':
                    st.text_area('Preview', data.decode('utf-8', errors='replace'), height=200)
else:
    st.info('No files found.')