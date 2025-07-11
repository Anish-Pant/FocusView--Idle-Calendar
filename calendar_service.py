import datetime
import os.path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# The same scope as in the authentication flow.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
TOKEN_FILE = 'token.json'

def get_upcoming_events():
    """
    Fetches the next 10 upcoming events from the primary Google Calendar.
    Returns a list of formatted events or an empty list on error.
    """
    if not os.path.exists(TOKEN_FILE):
        print(f"Error: '{TOKEN_FILE}' not found.")
        print("Please run authenticate.py first to generate the token file.")
        return []

    try:
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        service = build('calendar', 'v3', credentials=creds)

        # Get the current time in UTC to use as the minimum time for events.
        now = datetime.datetime.now(datetime.UTC).isoformat()

        # Call the Calendar API to get upcoming events.
        # singleEvents=True expands recurring events into individual instances.
        events_result = service.events().list(
            calendarId='primary',
            timeMin=now,
            maxResults=10,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])

        if not events:
            return []

        # Format the events into a simpler structure for the UI to use.
        formatted_events = []
        for event in events:
            start_info = event['start']
            # All-day events have a 'date', timed events have 'dateTime'.
            start = start_info.get('dateTime', start_info.get('date'))
            summary = event.get('summary', 'No Title')
            formatted_events.append({"start": start, "summary": summary})
            
        return formatted_events

    except HttpError as error:
        print(f'An API error occurred: {error}')
        return []
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []
    

if __name__ == '__main__':
    upcoming_events = get_upcoming_events()
    if upcoming_events:
        print("Upcoming Events:")
        for event in upcoming_events:
            print(f"- {event['summary']} (Starts: {event['start']})")
    else:
        print("No upcoming events found or an error occurred.")