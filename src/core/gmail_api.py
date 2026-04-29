import os.path
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

class GmailClient:
    def __init__(self, credentials_path='credentials.json', token_path='token.json'):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = self._authenticate()

    def _authenticate(self):
        creds = None
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    # For testing purposes, we might not have the credentials.json
                    # If we are mocking 'build', this won't be reached if we mock it early.
                    # But the __init__ calls _authenticate.
                    return None
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())

        try:
            return build('gmail', 'v1', credentials=creds)
        except Exception:
            return None

    def search_messages(self, query='', user_id='me'):
        try:
            results = self.service.users().messages().list(userId=user_id, q=query).execute()
            messages = results.get('messages', [])
            return messages
        except Exception as e:
            print(f"An error occurred searching messages: {e}")
            return []

    def get_message_body(self, msg_id, user_id='me'):
        try:
            message = self.service.users().messages().get(userId=user_id, id=msg_id, format='full').execute()
            payload = message.get('payload')
            body = ""

            if 'parts' in payload:
                for part in payload['parts']:
                    if part['mimeType'] == 'text/html':
                        data = part['body'].get('data')
                        if data:
                            body = base64.urlsafe_b64decode(data).decode()
                            break
                    elif part['mimeType'] == 'text/plain':
                        data = part['body'].get('data')
                        if data:
                            body = base64.urlsafe_b64decode(data).decode()
            else:
                data = payload['body'].get('data')
                if data:
                    body = base64.urlsafe_b64decode(data).decode()
            
            return body
        except Exception as e:
            print(f"An error occurred getting message body: {e}")
            return ""

    def modify_labels(self, msg_id, add_labels=None, remove_labels=None, user_id='me'):
        try:
            body = {}
            if add_labels:
                body['addLabelIds'] = add_labels
            if remove_labels:
                body['removeLabelIds'] = remove_labels
            
            self.service.users().messages().modify(userId=user_id, id=msg_id, body=body).execute()
            return True
        except Exception as e:
            print(f"An error occurred modifying labels: {e}")
            return False

    def get_or_create_label(self, label_name, user_id='me'):
        try:
            results = self.service.users().labels().list(userId=user_id).execute()
            labels = results.get('labels', [])
            
            for label in labels:
                if label['name'].lower() == label_name.lower():
                    return label['id']
            
            # Create label if not found
            label_body = {
                'name': label_name,
                'labelListVisibility': 'labelShow',
                'messageListVisibility': 'show'
            }
            created_label = self.service.users().labels().create(userId=user_id, body=label_body).execute()
            return created_label['id']
        except Exception as e:
            print(f"An error occurred managing label {label_name}: {e}")
            return None
