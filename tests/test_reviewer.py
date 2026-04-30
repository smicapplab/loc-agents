import pytest
from unittest.mock import MagicMock, patch
import os
import sys

# Add src to path if needed
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.reviewer import Reviewer

@pytest.mark.asyncio
@patch('src.core.reviewer.genai.GenerativeModel')
@patch.dict(os.environ, {"AI_PROVIDER": "gemini", "GOOGLE_API_KEY": "test_key"})
async def test_review_job_gemini(mock_model_class):
    mock_model = mock_model_class.return_value
    mock_response = MagicMock()
    mock_response.text = '{"score": 8, "reasoning": "Good match", "match_highlights": ["Python"], "concerns": []}'
    mock_model.generate_content.return_value = mock_response
    
    reviewer = Reviewer()
    job = {"title": "Python Dev", "company": "Test Co", "id": "123"}
    profile_md = "I know Python."
    
    result = await reviewer.review_job(job, profile_md)
    
    assert result['score'] == 8
    assert result['evaluation']['reasoning'] == "Good match"
    mock_model.generate_content.assert_called_once()

@pytest.mark.asyncio
@patch('src.core.reviewer.OpenAI')
@patch.dict(os.environ, {"AI_PROVIDER": "openai", "OPENAI_API_KEY": "test_key"})
async def test_review_job_openai(mock_openai_class):
    mock_client = mock_openai_class.return_value
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content='{"score": 9, "reasoning": "Great match", "match_highlights": ["AI"], "concerns": []}'))
    ]
    mock_client.chat.completions.create.return_value = mock_response
    
    reviewer = Reviewer()
    job = {"title": "AI Engineer", "company": "Test AI", "id": "456"}
    profile_md = "I know AI."
    
    result = await reviewer.review_job(job, profile_md)
    
    assert result['score'] == 9
    assert result['evaluation']['reasoning'] == "Great match"
    mock_client.chat.completions.create.assert_called_once()
