import pytest
from unittest.mock import MagicMock, patch
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
def test_extract_jobs_from_html(mock_model_class):
    mock_model = mock_model_class.return_value
    mock_response = MagicMock()
    mock_response.text = '[{"title": "Senior Engineer", "company": "Tech Corp", "link": "http://example.com", "salary": 260000}]'
    mock_model.generate_content.return_value = mock_response
    
    jobs = extract_jobs_from_html("<html>...</html>")
    
    assert len(jobs) == 1
    assert jobs[0]['title'] == "Senior Engineer"
    assert jobs[0]['salary'] == 260000
