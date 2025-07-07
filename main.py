import streamlit as st
import pandas as pd
import re
from datetime import datetime
import io

st.set_page_config(page_title="Sensor Query Extractor", layout="wide")
st.title("📦 Sensor Query Cleaner + Auto Tagger (Box Silvassa)")

uploaded_file = st.file_uploader("📄 Upload WhatsApp chat .txt file", type="txt")

# --- Auto-tag sensor types ---
sensor_keywords = {
    "Proximity": ["e2e", "e2b", "proximity", "tl-w", "tl-w5", "tlq", "tl-n"],
    "Reed Switch": ["reed", "magnetic"],
    "Photoelectric": ["e3fa", "e3jk", "e3x", "e3c"],
    "Capacitive": ["ec2", "ec5", "capacitive"],
    "Inductive": ["inductive"],
    "Pressure": ["pressure", "dz"],
    "Temperature": ["temperature", "pt100"]
}

def auto_tag(product_name):
    product_name = product_name.lower()
    for tag, keywords in sensor_keywords.items():
        if any(k in product_name for k in keywords):
            return tag
    return "Other"

# --- Discard phrases ---
discard_phrases = [
    "extra dalwa", "check kar lena", "confirm", "image omitted", "sir", "done", "rate dena",
    "update", "just sent", "is this okay", "check this", "same", "ok", "👍", "ho sakta hai",
    "dekh lena", "will share", "photo", "image", "not dispatch", "this sensor", "sensor update",
    "dispatch", "ready", "send photo", "send image", "this one", "share", "kindly"
]

# --- Clean & extract helpers ---
def extract_date(line):
    match = re.search(r"\[(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{2,4})", line)
    if match:
        day, month, year = match.groups()
        if len(year) == 2:
            year = '20' + year
        return f"{year}-{int(month):02d}-{int(day):02d}"
    return None

def extract_quantity(text):
    if pd.isna(text): return None
    text = str(text).lower()
    match = re.search(r'(qty\s*\d+|\d+\s*pcs\b|\d+\s*nos\b|\d+\s*each\b|\d+\s*no\b)', text)
    return match.group(0) if match else None

def remove_quantity(text):
    return re.sub(r'(qty\s*\d+|\d+\s*pcs\b|\d+\s*nos\b|\d+\s*each\b|\d+\s*no\b)', '', str(text), flags=re.IGNORECASE).strip()

def remove_context(text):
    text = str(text)
    patterns = [
        r'\bwe\s*require\b', r'\bwe\s*need\b', r'\bneed\b', r'\brequirement\s*of\b',
        r'\bwe\s*are\s*looking\s*for\b', r'\blooking\s*for\b', r'\bsend\s*me\b',
        r'\bcan\s*you\s*send\b', r'\bcan\s*you\s*share\b', r'\bgive\s*me\b',
        r'\bi\s*want\b', r'\bi\s*need\b', r'\bpls\s*share\b'
    ]
    for p in patterns:
        text = re.sub(p, '', text, flags=re.IGNORECASE)
    return text.strip()

def clean_product(text):
    text = remove_quantity(text)
    text = remove_context(text)
    text = re.sub(r"[^\w\s\-_/.,]", "", text)  # clean special chars
    text = re.sub(r"\bbox silvassa\b", "", text, flags=re.IGNORECASE)
    return text.strip()

# --- Main logic ---
if uploaded_file:
    raw_text = uploaded_file.read().decode("utf-8", errors="ignore")
    lines = raw_text.splitlines()
    records = []

    for line in lines:
        if not line.strip(): continue
        if "Box Silvassa" not in line: continue
        if any(p in line.lower() for p in discard_phrases): continue
        if not re.search(r"\[\d{1,2}/\d{1,2}/\d{2,4}", line): continue

        date = extract_date(line)
        msg_part = line.split("]")[-1] if "]" in line else line
        quantity = extract_quantity(msg_part)
        product_name = clean_product(msg_part)

        if product_name and (len(product_name.split()) >= 2 or "-" in product_name or re.search(r"\d", product_name)):
            sensor_type = auto_tag(product_name)
            records.append({
                "Product Line": line.strip(),
                "Product Name (with Model)": product_name,
                "Sensor Type": sensor_type,
                "Extracted Quantity": quantity,
                "Date": date
            })

    if records:
        df = pd.DataFrame(records)
        st.success("✅ Extracted Queries")
        st.dataframe(df)

        # --- Download to Excel ---
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name="Sensor Queries")
        st.download_button(
            label="⬇ Download Excel",
            data=output.getvalue(),
            file_name="sensor_queries_cleaned_tagged.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("⚠ No valid queries found from Box Silvassa.")
