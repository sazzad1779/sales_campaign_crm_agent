import os
import base64
import google.auth
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import config as settings
from googleapiclient.errors import HttpError

class GmailTool:
    def __init__(self):
        """Authenticate using OAuth 2.0 to access Gmail API"""
        #SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
        SCOPES = [
            "https://www.googleapis.com/auth/gmail.send",
            "https://www.googleapis.com/auth/gmail.readonly",
            "https://www.googleapis.com/auth/gmail.modify",
        ]
        creds = None
        token_file = settings.TOKEN_FILE

        # Check if token file exists
        if os.path.exists(token_file):
            try:
                creds = Credentials.from_authorized_user_file(token_file, SCOPES)
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(google.auth.transport.requests.Request())  # Refresh expired token
            except Exception as e:
                print(f"⚠️ Error loading token.json: {e}")
                creds = None  # Force re-authentication

        # If credentials are not available, authenticate
        if not creds or not creds.valid:
            flow = InstalledAppFlow.from_client_secrets_file(token_file, SCOPES)
            creds = flow.run_local_server(port=0)
            # Save new token
            with open(token_file, "w") as token:
                token.write(creds.to_json())
        self.service = build("gmail", "v1", credentials=creds)


    def send_email(self, recipient, subject, message):
        print(recipient, subject, message)
        """Sends an email using Gmail API with correct formatting"""
        if not recipient:
            raise ValueError("❌ Error: Recipient email address is required.")

        # Construct raw email format
        email_msg = f"To: {recipient}\nSubject: {subject}\n\n{message}"
        encoded_msg = base64.urlsafe_b64encode(email_msg.encode("utf-8")).decode("utf-8")
        message_body = {"raw": encoded_msg}

        try:
            self.service.users().messages().send(userId="me", body=message_body).execute()
            print(f"✅ Email sent to {recipient}")
            return True
        except Exception as e:
            print(f"❌ Error sending email: {e}")
            return False

    def fetch_email_responses(self):
        """
        Fetch unread email responses and return only the sender email and message content.
        Returns a dictionary: { sender_email: message_text }
        """
        response_data = {}

        try:
            # Fetch unread emails
            results = self.service.users().messages().list(
                userId="me",
                labelIds=["INBOX"],
                q="is:unread"
            ).execute()

            messages = results.get("messages", [])
            for msg in messages:
                msg_id = msg["id"]
                message = self.service.users().messages().get(userId="me", id=msg_id, format="full").execute()

                payload = message.get("payload", {})
                headers = payload.get("headers", [])
                email_body = ""

                # Extract sender email
                sender_email = ""
                for header in headers:
                    if header["name"] == "From":
                        sender_email = header["value"]
                        sender_email = sender_email.split("<")[-1].replace(">", "").strip()  # Clean email format
                        break

                # Extract message content
                if "parts" in payload:
                    for part in payload.get("parts", []):
                        if part.get("mimeType") == "text/plain":
                            body_data = part.get("body", {}).get("data", "")
                            if body_data:
                                email_body = base64.urlsafe_b64decode(body_data).decode("utf-8").strip()
                                break
                else:
                    body_data = payload.get("body", {}).get("data", "")
                    if body_data:
                        email_body = base64.urlsafe_b64decode(body_data).decode("utf-8").strip()

                # Store response (only email and message)
                if sender_email and email_body:
                    response_data[sender_email] = email_body

                # Mark email as read
                self.service.users().messages().modify(
                    userId="me",
                    id=msg_id,
                    body={"removeLabelIds": ["UNREAD"]}
                ).execute()

        except HttpError as error:
            print(f"❌ Gmail API error: {error}")
        except Exception as e:
            print(f"❌ Error fetching email responses: {e}")

        return response_data