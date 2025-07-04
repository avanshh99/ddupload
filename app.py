import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv
from urllib.parse import quote
import os
from datetime import datetime
import re
import unicodedata

def sanitize_filename(name):
    name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode()
    name = name.replace(' ', '_')
    name = re.sub(r'[^\w\-_\.]', '', name)
    return name

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
BUCKET_NAME = os.getenv("SUPABASE_BUCKET")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.title("📤 Upload the file ")

uploaded_file = st.file_uploader("Choose a file (PDF, Excel, CSV)", type=["pdf", "csv", "xlsx"])

if uploaded_file is not None:
    file_bytes = uploaded_file.read()
    original_filename = uploaded_file.name

    # check filename
    safe_filename = sanitize_filename(original_filename)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    supabase_path = f"{timestamp}_{safe_filename}"

    try:
        response = supabase.storage.from_(BUCKET_NAME).upload(
            supabase_path,
            file_bytes,
            {"content-type": uploaded_file.type}
        )
        if response:
            raw_url = supabase.storage.from_(BUCKET_NAME).get_public_url(supabase_path)
            public_url = raw_url.rsplit("/", 1)[0] + "/" + quote(supabase_path)
            st.success("File uploaded to Supabase successfully!")
            st.markdown(f"[🔗 View File]({public_url})")
        else:
            st.error("❌ Upload failed.")
    except Exception as e:
        st.error(f"Error: {str(e)}")
