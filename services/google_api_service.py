import io
import logging
import os.path
import uuid
from typing import Final, List, Optional

from google.auth.exceptions import RefreshError
from google.oauth2.service_account import Credentials
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
    if os.path.exists(CREDENTIAL_FILE_NAME):
        credentials = Credentials.from_service_account_file(CREDENTIAL_FILE_NAME, scopes=SCOPES)
    else:
        logging.error(f'Cannot build credentials from service account file.')
        return

    try:
        global SERVICE
        SERVICE = build('drive', 'v3', credentials=credentials)

        results = SERVICE.files().list(pageSize=10, fields='nextPageToken, files(id, name)', q='name = \'AI\'').execute()
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
