import fitz  # PyMuPDF

def extract_text_from_pdf(uploaded_file):

    text = ""

    try:

        pdf = fitz.open(
            stream=uploaded_file.read(),
            filetype="pdf"
        )

        for page in pdf:

            page_text = page.get_text()

            if page_text:
                text += page_text + "\n"

        return text.strip()

    except Exception as e:

        return f"PDF Extraction Error: {e}"