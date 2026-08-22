"""Extract plain text from a resume PDF."""

import pymupdf

MAX_FILE_BYTES = 5 * 1024 * 1024  # 5 MB
MAX_PAGES = 20
MIN_TEXT_CHARS = 100  # below this, it's almost certainly a scan with no text layer
PDF_MAGIC = b"%PDF-"


class PdfError(Exception):
    """Raised for any file we cannot turn into usable resume text."""


def extract_text(data: bytes, filename: str) -> tuple[str, int]:
    """Return (text, page_count). Raises PdfError with a user-facing message."""
    if not data:
        raise PdfError("The file is empty.")
    if len(data) > MAX_FILE_BYTES:
        raise PdfError(f"File is larger than {MAX_FILE_BYTES // (1024 * 1024)} MB.")
    # Check the real bytes, not the filename or Content-Type — both are
    # supplied by the client and neither is trustworthy.
    if not data.startswith(PDF_MAGIC):
        raise PdfError("That doesn't look like a PDF file.")

    try:
        doc = pymupdf.open(stream=data, filetype="pdf")
    except Exception as exc:
        raise PdfError("The PDF could not be opened. It may be corrupted.") from exc

    with doc:
        if doc.needs_pass:
            raise PdfError("This PDF is password protected.")
        if doc.page_count == 0:
            raise PdfError("The PDF has no pages.")
        if doc.page_count > MAX_PAGES:
            raise PdfError(f"Resume is longer than {MAX_PAGES} pages.")

        pages = [page.get_text("text") for page in doc]
        page_count = doc.page_count

    text = clean_text("\n".join(pages))

    if len(text) < MIN_TEXT_CHARS:
        raise PdfError(
            "No readable text found. If this is a scanned resume, "
            "please upload a text-based PDF instead."
        )
    return text, page_count


def clean_text(text: str) -> str:
    """Normalise whitespace without touching the characters themselves.

    Deliberately conservative: lowercasing or stripping punctuation here would
    destroy terms like C++, .NET and Node.js. That belongs in Phase 4, where it
    can be done with the exceptions those terms need.
    """
    lines = [" ".join(line.split()) for line in text.splitlines()]
    return "\n".join(line for line in lines if line).strip()
