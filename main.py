import os.path
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.text import MIMEText
import base64

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

creds = None
if os.path.exists("token.json"):
    with open("token.json", "r") as f:
        creds = Credentials.from_authorized_user_info(json.load(f))

if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            "credentials.json", SCOPES
        )
        creds = flow.run_local_server(port=0)
    with open("token.json", "w") as f:
        f.write(creds.to_json())

service = build("gmail", "v1", credentials=creds)
flaggedAddresses = os.getenv("FLAGGED_ADDRESSES").split(",")

messages = service.users().messages().list(userId="me", q="is:unread").execute().get("messages", [])
for message in messages:
    msg = service.users().messages().get(
        userId="me",
        id=message["id"],
        format="full"
    ).execute()

    headers = msg["payload"]["headers"]
    thread_id = msg["threadId"]
    sender = next(header["value"] for header in headers if header["name"] == "From")
    if any(flaggedAddress == sender[sender.find("<") + 1 : sender.find(">")] if '<' in sender else sender for flaggedAddress in flaggedAddresses):
        # Get the email details
        original_subject = next(header["value"] for header in headers if header["name"] == "Subject")
        original_message_id = next((header["value"] for header in headers if header["name"].lower() == "message-id"), None)

        # Construct the reply
        body = "NUH UH LOSER L + RATIO IMAGINE LOLLLLLLLLLLLLLLLLLL"
        mimeMessage = MIMEText(body)
        mimeMessage["to"] = sender[sender.find("<") + 1 : sender.find(">")] if '<' in sender else sender
        mimeMessage["from"] = "me"
        if original_message_id:
            mimeMessage["In-Reply-To"] = original_message_id
            mimeMessage["References"] = original_message_id
            
        if original_subject.startswith("Re:"):
            subject = original_subject
        else:
            subject = "Re: " + original_subject
        mimeMessage["subject"] = subject

        # Encode - Gmail API requires base64 encoding
        raw_bytes = mimeMessage.as_bytes()
        encoded_message = base64.urlsafe_b64encode(raw_bytes).decode()

        # Mark emails as read and send replies
        service.users().messages().send(
            userId="me",
            body={
                "raw": encoded_message,
                "threadId": thread_id
            }
        ).execute()

        # Mark message as read
        service.users().messages().modify(
            userId="me",
            id=message["id"],
            body={"removeLabelIds": ["UNREAD"]},
        ).execute()