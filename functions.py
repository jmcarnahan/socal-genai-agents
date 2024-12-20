import json
import pandas as pd
from pandasql import sqldf
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
from email.mime.text import MIMEText
from dotenv import load_dotenv
load_dotenv()

class Functions:

  def use_numbers (self, a, b):
      return json.dumps({"value": a - b})
  
  def _get_google_creds ():
    # If modifying these scopes, delete the file .token.json.
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly", "https://www.googleapis.com/auth/gmail.send"]
    creds = None

    if not os.getenv('GOOGLE_SECRETS_FILE'):
      raise ValueError("GOOGLE_SECRETS_FILE is not set. Please ensure the GOOGLE_SECRETS_FILE is set")

    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(".token.json"):
      creds = Credentials.from_authorized_user_file(".token.json", SCOPES)

    if not creds or not creds.valid:
      if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
      else:
        flow = InstalledAppFlow.from_client_secrets_file(os.getenv('GOOGLE_SECRETS_FILE'), SCOPES)
        creds = flow.run_local_server(port=0)
      # Save the credentials for the next run
      with open(".token.json", "w") as token:
        token.write(creds.to_json())
        print("created new .token.json")
    else:
      # print("using existing .token.json")
      pass
    
    return creds


  def execute_sql_googlesheets (self, sql_query):
    print("Executing SQL: " + sql_query)

    # The ID and range of a google spreadsheet.
    SPREADSHEET_ID = os.getenv('GOOGLE_SHEETS_ID')
    RANGE_NAME = os.getenv('GOOGLE_SHEETS_RANGE')

    creds = Functions._get_google_creds()
    try:
      service = build("sheets", "v4", credentials=creds)

      # Call the Sheets API
      sheet = service.spreadsheets()
      result = (
          sheet.values()
          .get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME)
          .execute()
      )
      values = result.get("values", [])

      if not values:
          print('No data found.')
          return json.dumps({"value": "No data found."})
      else:
          df = pd.DataFrame(values[1:], columns=values[0])
          result = sqldf(sql_query, locals())
          return json.dumps(result.to_json(orient='records'))

    except HttpError as err:
      print(err)
      return json.dumps({"value": "No data found."})
    
  def send_email(self, to, subject, body):

    creds = Functions._get_google_creds()
    try:
      service = build('gmail', 'v1', credentials=creds)
      message = MIMEText(body)
      message['to'] = to
      message['subject'] = subject
      raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

      # Send the email
      message = service.users().messages().send(userId="me", body={'raw': raw}).execute()
      print(f"Message sent! Message ID: {message['id']}")
      return json.dumps({"value": "Message sent! Message ID: " + message['id']})

    except HttpError as err:
      print(err)
      return json.dumps({"value": "No data found."})
    
  # def get_bigquery_client():
  #   from google.cloud import bigquery
  #       if self.bq is None:
  #           self.bq = bigquery.Client(project=self.project_id)
  #       return self.bq







  


