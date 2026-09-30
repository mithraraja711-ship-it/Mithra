import os
from datetime import date

import requests
import streamlit as st

from dotenv import load_dotenv

from document_utils.text_utils import (
    text_to_html
)


load_dotenv()


BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8000"
).rstrip("/")


st.set_page_config(
    page_title="LegalEase",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ---------------------------------------------------------
# CSS
# ---------------------------------------------------------

st.markdown(
    """
    <style>

    .main-title {
        text-align: center;
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        color: #777;
        font-size: 17px;
        margin-bottom: 30px;
    }

    .preview-card {
        background-color: #111827;
        color: #f9fafb;
        padding: 30px;
        border-radius: 14px;
        border: 1px solid #374151;
        max-height: 650px;
        overflow-y: auto;
        line-height: 1.7;
    }

    .legal-heading {
        text-align: center;
        margin-top: 10px;
        margin-bottom: 20px;
    }

    .legal-section {
        margin-top: 20px;
    }

    .legal-paragraph {
        margin-bottom: 12px;
    }

    .legal-bullet {
        margin-left: 15px;
        margin-bottom: 8px;
    }

    .disclaimer {
        background-color: #fff4cc;
        color: #664d03;
        padding: 15px;
        border-radius: 8px;
        margin-top: 20px;
        font-size: 13px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ---------------------------------------------------------
# Header
# ---------------------------------------------------------

st.markdown(
    '<div class="main-title">⚖️ LegalEase</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="subtitle">
    AI-Powered Legal Document Generator
    </div>
    """,
    unsafe_allow_html=True
)


# ---------------------------------------------------------
# Session state
# ---------------------------------------------------------

if "generated_document" not in st.session_state:
    st.session_state.generated_document = ""

if "generated" not in st.session_state:
    st.session_state.generated = False


# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------

with st.sidebar:

    st.header("⚙️ Settings")

    st.write(
        "Backend:"
    )

    st.code(
        BACKEND_URL
    )

    st.divider()

    st.info(
        """
        LegalEase generates legal-document drafts
        using generative AI.

        Always review AI-generated documents with
        a qualified legal professional before signing
        or relying on them.
        """
    )


# ---------------------------------------------------------
# Input area
# ---------------------------------------------------------

st.subheader("📄 Document Information")


document_type = st.selectbox(
    "Document Type",
    [
        "Employment Contract",
        "Non-Disclosure Agreement",
        "Lease Agreement",
        "Freelance Work Contract",
        "Service Agreement",
        "Partnership Agreement",
        "Consulting Agreement",
        "Offer Letter",
        "General Agreement",S
        "Custom Legal Document"
    ]
)


if document_type == "Custom Legal Document":

    custom_type = st.text_input(
        "Enter document type"
    )

    if custom_type.strip():

        document_type = custom_type


col1, col2 = st.columns(2)


with col1:

    parties = st.text_area(
        "Parties Involved",
        placeholder=(
            "Example:\n"
            "Jane Doe (Service Provider)\n"
            "TechNova Inc. (Client)"
        ),
        height=150
    )


with col2:

    effective_date = st.date_input(
        "Effective Date",
        value=date.today()
    )


terms = st.text_area(
    "Terms & Conditions",
    placeholder=(
        "Enter each term separated by a semicolon.\n\n"
        "Example:\n"
        "Payment within 30 days; "
        "Confidentiality must be maintained; "
        "Either party may terminate with 15 days notice"
    ),
    height=180
)


# ---------------------------------------------------------
# Generate
# ---------------------------------------------------------

generate_button = st.button(
    "✨ Generate Document",
    type="primary",
    use_container_width=True
)


if generate_button:

    if not parties.strip():

        st.error(
            "Please enter the parties involved."
        )

        st.stop()

    if not terms.strip():

        st.error(
            "Please enter at least one term or condition."
        )

        st.stop()

    payload = {
        "document_type": document_type,
        "parties": parties,
        "terms": terms,
        "effective_date": str(effective_date)
    }

    with st.spinner(
        "Generating your legal document..."
    ):

        try:

            response = requests.post(
                f"{BACKEND_URL}/generate",
                json=payload,
                timeout=180
            )

            if response.status_code == 200:

                result = response.json()

                st.session_state.generated_document = (
                    result["content"]
                )

                st.session_state.generated = True

                st.success(
                    "Document generated successfully."
                )

            else:

                try:
                    error = response.json().get(
                        "detail",
                        response.text
                    )
                except Exception:
                    error = response.text

                st.error(
                    f"Generation failed: {error}"
                )

        except requests.exceptions.ConnectionError:

            st.error(
                "Could not connect to the FastAPI backend. "
                "Make sure the backend is running on "
                f"{BACKEND_URL}."
            )

        except requests.exceptions.Timeout:

            st.error(
                "The request timed out. "
                "Please try again."
            )

        except Exception as exc:

            st.error(
                f"Unexpected error: {exc}"
            )


# ---------------------------------------------------------
# Generated document
# ---------------------------------------------------------

if st.session_state.generated:

    st.divider()

    st.subheader(
        "📝 Generated Document"
    )

    tab_preview, tab_edit = st.tabs(
        [
            "Preview",
            "Edit Document"
        ]
    )


    with tab_preview:

        preview_html = text_to_html(
            st.session_state.generated_document
        )

        st.markdown(
            f"""
            <div class="preview-card">
                {preview_html}
            </div>
            """,
            unsafe_allow_html=True
        )


    with tab_edit:

        edited_document = st.text_area(
            "Edit your document below",
            value=st.session_state.generated_document,
            height=650
        )

        if st.button(
            "💾 Save Edits",
            use_container_width=True
        ):

            st.session_state.generated_document = (
                edited_document
            )

            st.success(
                "Changes saved."
            )

            st.rerun()


    # -----------------------------------------------------
    # Download
    # -----------------------------------------------------

    st.divider()

    st.subheader(
        "⬇️ Download Document"
    )

    download_col1, download_col2, download_col3 = (
        st.columns(3)
    )


    export_payload = {
        "content": st.session_state.generated_document,
        "document_type": document_type,
        "parties": parties,
        "effective_date": str(effective_date),
        "terms": terms
    }


    # TXT
    with download_col1:

        try:

            txt_response = requests.post(
                f"{BACKEND_URL}/export/txt",
                json=export_payload,
                timeout=30
            )

            if txt_response.status_code == 200:

                st.download_button(
                    label="📄 Download TXT",
                    data=txt_response.content,
                    file_name=(
                        document_type
                        .lower()
                        .replace(" ", "_")
                        + ".txt"
                    ),
                    mime="text/plain",
                    use_container_width=True
                )

        except Exception:

            st.warning(
                "TXT export unavailable."
            )


    # DOCX
    with download_col2:

        try:

            docx_response = requests.post(
                f"{BACKEND_URL}/export/docx",
                json=export_payload,
                timeout=30
            )

            if docx_response.status_code == 200:

                st.download_button(
                    label="📝 Download DOCX",
                    data=docx_response.content,
                    file_name=(
                        document_type
                        .lower()
                        .replace(" ", "_")
                        + ".docx"
                    ),
                    mime=(
                        "application/vnd.openxmlformats-"
                        "officedocument.wordprocessingml.document"
                    ),
                    use_container_width=True
                )

        except Exception:

            st.warning(
                "DOCX export unavailable."
            )


    # PDF
    with download_col3:

        try:

            pdf_response = requests.post(
                f"{BACKEND_URL}/export/pdf",
                json=export_payload,
                timeout=30
            )

            if pdf_response.status_code == 200:

                st.download_button(
                    label="📕 Download PDF",
                    data=pdf_response.content,
                    file_name=(
                        document_type
                        .lower()
                        .replace(" ", "_")
                        + ".pdf"
                    ),
                    mime="application/pdf",
                    use_container_width=True
                )

        except Exception:

            st.warning(
                "PDF export unavailable."
            )


    st.markdown(
        """
        <div class="disclaimer">
        ⚠️ <strong>Important:</strong>
        LegalEase generates AI-assisted drafts.
        The generated content is not a substitute for
        professional legal advice. Review the document
        with a qualified legal professional before signing
        or relying upon it.
        </div>
        """,
        unsafe_allow_html=True
    )