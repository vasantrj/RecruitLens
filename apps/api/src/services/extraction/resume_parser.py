import io
import pdfplumber
from docx import Document


def extract_text_from_pdf(file_bytes: bytes) -> str:
    text_parts = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n".join(text_parts)


def extract_text_from_docx(file_bytes: bytes) -> str:
    doc = Document(io.BytesIO(file_bytes))
    return "\n".join(paragraph.text for paragraph in doc.paragraphs)


def extract_resume_text(file_bytes: bytes, filename: str) -> str:
    if filename.lower().endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)
    elif filename.lower().endswith(".docx"):
        return extract_text_from_docx(file_bytes)
    else:
        raise ValueError("Unsupported file type. Only PDF and DOCX are supported.")
    

def extract_pdf_hyperlinks(file_bytes: bytes) -> list[str]:
    """
    Extracts actual hyperlink URLs embedded as clickable annotations in a PDF —
    catches links where the visible text is just "GitHub" or "LinkedIn"
    but the underlying URL isn't present as literal text.
    """
    urls = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            hyperlinks = getattr(page, "hyperlinks", None)
            if hyperlinks:
                for link in hyperlinks:
                    uri = link.get("uri")
                    if uri:
                        urls.append(uri)
            else:
                for annot in (page.annots or []):
                    uri = annot.get("data", {}).get("uri") if isinstance(annot.get("data"), dict) else None
                    if uri:
                        urls.append(uri)
    return list(dict.fromkeys(urls))