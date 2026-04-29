import pytest
from unittest.mock import MagicMock, patch
from src.core.gmail_api import GmailClient

@pytest.fixture
def mock_gmail_client():
    with patch('src.core.gmail_api.GmailClient._authenticate') as mock_auth:
        mock_service = MagicMock()
        mock_auth.return_value = mock_service
        client = GmailClient()
        yield client, mock_service

def test_gmail_client_search_messages(mock_gmail_client):
    client, mock_service = mock_gmail_client
    # Setup mock response
    mock_list = mock_service.users().messages().list()
    mock_list.execute.return_value = {
        'messages': [{'id': 'msg1'}, {'id': 'msg2'}]
    }
    
    messages = client.search_messages(query="from:linkedin.com")
    
    assert len(messages) == 2
    assert messages[0]['id'] == 'msg1'
    
    # Verify the call
    mock_service.users().messages().list.assert_called_with(
        userId='me', q='from:linkedin.com'
    )

def test_gmail_client_get_message_body(mock_gmail_client):
    client, mock_service = mock_gmail_client
    # Setup mock response with base64 encoded data
    html_body = "<h1>Job Title</h1>"
    encoded_body = base64.urlsafe_b64encode(html_body.encode()).decode()
    
    mock_service.users().messages().get().execute.return_value = {
        'payload': {
            'parts': [
                {'mimeType': 'text/html', 'body': {'data': encoded_body}}
            ]
        }
    }
    
    body = client.get_message_body('msg1')
    assert body == html_body

def test_gmail_client_modify_labels(mock_gmail_client):
    client, mock_service = mock_gmail_client
    
    client.modify_labels('msg1', add_labels=['Jobs'], remove_labels=['Updates'])
    
    mock_service.users().messages().modify.assert_called_with(
        userId='me', id='msg1', body={'addLabelIds': ['Jobs'], 'removeLabelIds': ['Updates']}
    )

import base64
