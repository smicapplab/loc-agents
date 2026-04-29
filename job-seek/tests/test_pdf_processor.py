import pytest
import os
from src.utils.pdf_processor import extract_text_from_pdf

def test_extract_text_from_pdf_exists():
    """Test that text is extracted from a valid PDF file."""
    # Use path relative to repo root if running from there
    pdf_path = "job-seek/data/resume.pdf"
    if not os.path.exists(pdf_path):
        pdf_path = "data/resume.pdf" # Fallback for running from job-seek/
    
    assert os.path.exists(pdf_path)
    
    text = extract_text_from_pdf(pdf_path)
    assert isinstance(text, str)
    assert len(text) > 0
    # Common resume keywords that should be present
    assert any(keyword in text.lower() for keyword in ["experience", "education", "skills"])

def test_extract_text_from_pdf_not_found():
    """Test handling of missing PDF file."""
    with pytest.raises(FileNotFoundError):
        extract_text_from_pdf("non_existent.pdf")
