import io
import logging
import os.path
import uuid
from typing import Final, List, Optional

from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseUpload
from services.configuration_service import configuration_service

SCOPES: Final[List[str]] = ["https://www.googleapis.com/auth/activity",
                            "https://www.googleapis.com/auth/drive.file",
                            "https://www.googleapis.com/auth/docs",
                            "https://www.googleapis.com/auth/drive",
                            "https://www.googleapis.com/auth/drive.activity",
                            "https://www.googleapis.com/auth/drive.activity.readonly",
                            "https://www.googleapis.com/auth/drive.readonly",
                            "https://www.googleapis.com/auth/drive.metadata",
                            "https://www.googleapis.com/auth/drive.metadata.readonly",
                            "https://www.googleapis.com/auth/drive.photos.readonly"]

TOKEN_FILE_NAME: Final[str] = 'token.json'
CREDENTIAL_FILE_NAME: Final[str] = 'credentials.json'
SERVICE: Optional[Resource] = None


def initialize():
    credentials: Optional[Credentials] = None
    if os.path.exists(TOKEN_FILE_NAME):
        credentials = Credentials.from_authorized_user_file(TOKEN_FILE_NAME, SCOPES)

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIAL_FILE_NAME, SCOPES)
            credentials = flow.run_local_server(port=0)

        with open(TOKEN_FILE_NAME, 'w') as token:
            token.write(credentials.to_json())

    try:
        global SERVICE
        SERVICE = build('drive', 'v3', credentials=credentials)

        results = SERVICE.files().list(pageSize=10, fields='nextPageToken, files(id, name)', q='name = \'Midjourney\'').execute()
        items = results.get('files', [])

        if not items:
            logging.error('Google Drive: No files found.')
            return
        else:
            for item in items:
                logging.info(f'Found: {item}')

    except HttpError as error:
        print(f'An error occurred: {error}')


async def upload(raw_bytes: bytes) -> bool:
    bytes_io = io.BytesIO(raw_bytes)
    bytes_io.seek(0, 0)
    media = MediaIoBaseUpload(bytes_io, mimetype='image/png', resumable=True)
    metadata = {'name': f'{str(uuid.uuid4())}.png', 'parents': [configuration_service.upload_destination]}
    try:
        file = SERVICE.files().create(body=metadata, media_body=media, fields='id').execute()
        logging.info('Uploaded: %s' % file.get('id'))
        return True
    except HttpError as error:
        logging.error(f'An error occurred when uploading file: {error}')
        return False
    except RefreshError as error:
        logging.error(f'An error occurred when uploading file: {error}. Try refreshing the token...')
        initialize()
        return await upload(raw_bytes)
