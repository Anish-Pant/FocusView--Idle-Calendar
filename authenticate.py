import os
import sys
from google_auth_oauthlib.flow import InstalledAppFlow

# This scope allows read-only access to the user's calendar.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.json'

def run_authentication():
   #Performs a one-time user authentication to generate 'token.json'. This script opens a web browser for the user to grant calendar access. The main application uses the generated token to operate.

    if os.path.exists(TOKEN_FILE):
        print(f"'{TOKEN_FILE}' already exists. To re-authenticate, delete it and run this script again.")
        return

    try:
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
    except FileNotFoundError:
        print(f"Error: '{CREDENTIALS_FILE}' not found.")
        print("Please download your OAuth 2.0 credentials from the Google Cloud Console and place the file here.")
        sys.exit(1)

    creds = flow.run_local_server(port=0)

    with open(TOKEN_FILE, 'w') as token:
        token.write(creds.to_json())

    print(f"\nAuthentication successful. '{TOKEN_FILE}' created.")
    print("You may now run the main application.")

if __name__ == '__main__':
    run_authentication()