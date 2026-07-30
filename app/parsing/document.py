import io


def load_text(suffix: str, data: bytes) -> str:
    """Extract plain text from an uploaded resume document."""
    if suffix == ".txt":
        return data.decode("utf-8", errors="ignore")

    if suffix == ".pdf":
        import pdfplumber

        with pdfplumber.open(io.BytesIO(data)) as pdf:
            return "\n".join((page.extract_text() or "") for page in pdf.pages)

    if suffix == ".docx":
        from docx import Document

        doc = Document(io.BytesIO(data))
        return "\n".join(p.text for p in doc.paragraphs)

    raise ValueError(f"Unsupported suffix: {suffix}")
