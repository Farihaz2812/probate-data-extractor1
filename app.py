import streamlit as st
import pandas as pd
import fitz  # PyMuPDF
import re
import os
import io
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, cast

# --- Configuration ---
# Create an output directory if it doesn't exist
OUTPUT_DIR = "output_data"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)


# --- Core Functions ---


def extract_text_from_uploaded_pdf(pdf_file) -> str:
    """Extracts raw text from an uploaded PDF file using PyMuPDF."""
    full_text = ""
    try:
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        for page in doc:
            page_blocks = page.get_text("blocks")  # list of (x0,y0,x1,y1, text, block_no, ...)
            full_text += "\n".join(block[4] for block in sorted(page_blocks, key=lambda b: (b[1], b[0])))
        doc.close()
    except Exception as e:
        st.error(f"Error processing PDF: {e}")
    return full_text


# --- Helpers ---

TITLE_RE = re.compile(r'(?im)^\s*([^\n]+?)\s*\(\s*probate\s*\)\s*$', re.IGNORECASE | re.MULTILINE)

def _notice_type(body: str) -> str:
    b = body.lower()

    # Consider it a creditors notice if ANY of these patterns appear
    is_creditors_notice = (
        re.search(r'notice\s+to\s+(?:all\s+)?creditors', b) or
        re.search(r'creditors\s+of\s+the\s+decedent', b) or
        re.search(r'creditors\s+of\s+the\s+.*trust', b)
    )
    if not is_creditors_notice:
        return "Other"

    # Classify as trust vs estate
    if re.search(r'\btrust|revocable(?:\s+living)?\s+trust|settlor|grantor|trust\s+estate', b):
        return "Trust"
    if re.search(r'\bestate\b|decedent', b):
        return "Estate"
    return "Estate"  # sensible default once we've decided it's a creditors notice

DATE_RE = re.compile(
    r'\b(?:died|died on)\s+('
    r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}'                 # 06/06/2025 or 05-19-2025
    r'|[A-Za-z]{3,9}\s+\d{1,2},\s*\d{4}'             # July 8, 2025
    r')\b',
    re.IGNORECASE
)

DOB_RE = re.compile(
    r'(?:Date\s+of\s+Birth|Date\s+of\s+birth|Date\s+of\s+Birth:|Date\s+of\s+birth:)\s*[:\-]?\s*('
    r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}'
    r'|[A-Za-z]{3,9}\s+\d{1,2},\s*\d{4}'
    r'|[A-Za-z]{3}\.?[- ]\d{1,2},\s*\d{4}'
    r')',
    re.IGNORECASE
)

# e.g., "presented to Linda L. Tuomaala, named Trustee," or "presented to Charles ... and Lee ..., successor Co-Trustees,"
PRESENTED_TO_BLOCK_RE = re.compile(
    r'presented\s+to\s+(?P<names_block>.+?)(?=within\s+\d|\.\s|$)',
    re.IGNORECASE | re.DOTALL
)

# Walk the names block and pull every "Name, Role" pair
NAME_ROLE_RE = re.compile(
    r'([A-Z][A-Za-z.\'\-]*(?:\s+[A-Z][A-Za-z.\'\-]*){0,4}\s*(?:Jr\.|Sr\.|III|IV)?)\s*,\s*'
    r'((?:personal\s+representative|named\s+trustee|successor\s+trustee|co-?successor\s+trustee|trustee)s?)',
    re.IGNORECASE
)

# Generic US/MI-ish address + optional phone on the same/following lines
ADDRESS_RE = re.compile(
    r'(\d{1,6}\s+[A-Za-z0-9.\'#/&\- ]+?,\s*[A-Za-z.\- ]+?,\s*(?:MI|Michigan|[A-Z]{2})\s*\d{5}(?:-\d{4})?)'
)

PHONE_RE = re.compile(r'(\(?\d{3}\)?\s*[-.]?\s*\d{3}\s*[-.]?\s*\d{4})')

def _iter_records(full_text: str):
    """Yield (title, body) tuples for each '(Probate)' block."""
    matches = list(TITLE_RE.finditer(full_text))
    for idx, m in enumerate(matches):
        start = m.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(full_text)
        yield m.group(1).strip(), full_text[start:end].strip()


# --- Replacement core parser ---
def parse_probate_records(text: str) -> List[Dict]:
    extracted = []
    for title, body in _iter_records(text):
        ntype = _notice_type(body)

        # don't skip here — keep everything and tag it
        deceased_name = title

        # Dates
        m_dod = DATE_RE.search(body)
        dod = m_dod.group(1).strip() if m_dod else "Not Found"

        m_dob = DOB_RE.search(body)
        dob = m_dob.group(1).strip() if m_dob else "Not Found"

        reps, rep_addresses, rep_phones = [], [], []

        m_block = PRESENTED_TO_BLOCK_RE.search(body)
        if m_block:
            names_block = m_block.group("names_block")
            for nm_role in NAME_ROLE_RE.finditer(names_block):
                reps.append(nm_role.group(1).strip())

        if not reps:
            for nm_role in NAME_ROLE_RE.finditer(body):
                reps.append(nm_role.group(1).strip())

        rep_addresses = [a.strip() for a in ADDRESS_RE.findall(body)]
        rep_phones = [p.strip() for p in PHONE_RE.findall(body)]

        extracted.append({
            "Notice Type": ntype,
            "Deceased / Settlor": deceased_name,
            "Date of Birth": dob,
            "Date of Death": dod,
            "Personal Representative(s) / Trustee(s)": " | ".join(reps) if reps else "Not Found",
            "Representative Address(es)": " | ".join(rep_addresses) if rep_addresses else "Not Found",
            "Representative Phone(s)": " | ".join(rep_phones) if rep_phones else "Not Found",
        })
    return extracted

def search_for_property(name):
    """Searches for property assets for a given name in Oakland County, MI."""

    if not name or name == "Not Found":
        return "No property search (name missing)."
    

    # This is a simplified example for demonstration purposes.
    # Real-world public record sites can be much more complex.
    base_url = "https://www.oakgov.com/property/Pages/default.aspx" # This is a placeholder

    # In a real scenario, you would need to find the actual property search portal
    # and simulate the search requests. For this example, we'll simulate a search.

    # Let's assume we found a fictional search result.
    # We will simulate this by returning a dummy address if the name is in the sample PDF.
    if "Ciarelli" in name:
        return "123 Main St, Royal Oak, MI 48073 (Simulated)"
    if "Tuomaala" in name:
        return "3021 Helen Ct, Royal Oak, MI 48073 (From PDF)"

    return "No property found in simulated search."


# --- Streamlit UI ---

st.set_page_config(page_title="Probate Data Extractor", layout="wide")

st.title("Probate Record Data Extractor 📄")
st.markdown("Upload a PDF of probate records to extract key information and search for related assets.")

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    with st.spinner("Processing PDF... This may take a moment."):
        raw_text = extract_text_from_uploaded_pdf(uploaded_file)

        if raw_text:
            st.subheader("Extracted Raw Text (First 500 characters)")
            st.text_area("Raw Text", raw_text[:500] + "...", height=150)

            records = parse_probate_records(raw_text)
            df = pd.DataFrame(records).rename(columns={"Deceased / Settlor": "Deceased Name"})

            # Show everything (should be 35)
            st.caption(f"Found {len(df)} total '(Probate)' entries.")
            st.dataframe(df)

            # Then filter to deceased notices only
            deceased_df = df[df["Notice Type"].isin(["Estate", "Trust"])].copy()
            st.caption(f"Deceased creditor notices (Estate/Trust): {len(deceased_df)}")
            st.dataframe(deceased_df)

            # Use deceased_df for asset search + download
            with st.spinner("Searching for assets..."):
                deceased_df["Property Address"] = deceased_df["Deceased Name"].apply(search_for_property)
            st.download_button(
                "Download Deceased Notices as CSV",
                deceased_df.to_csv(index=False).encode("utf-8"),
                "probate_records_with_assets.csv",
                "text/csv",
            )
        else:
            st.error("Could not extract any text from the PDF.")

st.sidebar.header("About")
st.sidebar.info(
    "This is Version 1 of a tool to automate the extraction of data from public probate notices. "
    "The asset search functionality is a simplified simulation and would need to be adapted for "
    "specific public records websites."
)
