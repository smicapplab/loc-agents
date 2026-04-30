import pytest
from unittest.mock import MagicMock, patch
import os
from logic import extract_jobs_from_html, filter_by_salary

def test_filter_by_salary():
    # Salary >= 250k should pass
    assert filter_by_salary({'salary': 250000}) == True
    assert filter_by_salary({'salary': 300000}) == True
    # Salary < 250k should fail
    assert filter_by_salary({'salary': 200000}) == False
    # None should pass (include if not mentioned)
    assert filter_by_salary({'salary': None}) == True
    assert filter_by_salary({}) == True

@patch('logic.genai.GenerativeModel')
def test_extract_jobs_from_html_gemini(mock_model_class):
    mock_model = mock_model_class.return_value
    mock_response = MagicMock()
    mock_response.text = '[{"title": "Senior Engineer", "company": "Tech Corp", "link": "http://example.com", "salary": 260000}]'
    mock_model.generate_content.return_value = mock_response
    
    # Ensure AI_PROVIDER is gemini (default)
    with patch.dict(os.environ, {"AI_PROVIDER": "gemini", "GOOGLE_API_KEY": "test_key"}):
        jobs = extract_jobs_from_html("<html>...</html>")
    
    assert len(jobs) == 1
    assert jobs[0]['title'] == "Senior Engineer"
    assert jobs[0]['salary'] == 260000

@patch('logic.OpenAI')
def test_extract_jobs_from_html_openai(mock_openai_class):
    # Set AI_PROVIDER to openai
    with patch.dict(os.environ, {"AI_PROVIDER": "openai", "OPENAI_API_KEY": "test_key"}):
        mock_client = mock_openai_class.return_value
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content='[{"title": "OpenAI Engineer", "company": "OpenAI", "link": "http://openai.com", "salary": 300000}]'))
        ]
        mock_client.chat.completions.create.return_value = mock_response
        
        jobs = extract_jobs_from_html("<html>...</html>")
        
        assert len(jobs) == 1
        assert jobs[0]['title'] == "OpenAI Engineer"
        assert jobs[0]['salary'] == 300000
        mock_client.chat.completions.create.assert_called_once()
