from __future__ import print_function
from dotenv import load_dotenv

import os.path
from flask import Flask, request
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json
app = Flask(__name__)
load_dotenv()


def getCredentials():
    SCOPES = ['https://www.googleapis.com/auth/drive']
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds


def WriteToDatabase(data, creds):
    SAMPLE_SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
    SAMPLE_RANGE_NAME = 'Sheet1!A:N'
    try:
        service = build('sheets', 'v4', credentials=creds)

        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                    range=SAMPLE_RANGE_NAME).execute()
        values = result.get('values', [])

        print(len(values))
        newvalues = [
            [
                data["teamNumber"],
                data["matchNumber"],
                data["name"],
                data["startposition"],
                data["GeneralAutoBehavior"],
                data["boxCount"]["high"],
                data["boxCount"]["medium"],
                data["boxCount"]["low"],
                data["coneCount"]["high"],
                data["coneCount"]["medium"],
                data["coneCount"]["low"],
                data["GeneralEndgameBehavior"],
                data["robotCount"],
                data["extrathoughts"]
            ]
        ]
        body = {
            'values': newvalues
        }
        range = "Sheet1!A" + str(len(values) + 1) + ":N"
        result = sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=range,
                                       valueInputOption='USER_ENTERED', body=body).execute()
    except HttpError as err:
        print(err)


@app.route('/', methods=["POST"])
def index():
    creds = getCredentials()
    WriteToDatabase(request.json, creds)
    return "<p>Good</p>"
