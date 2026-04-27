import datetime
import os.path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# The same scopes as in the authentication flow.
SCOPES = [
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/tasks.readonly'
]
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
        now_dt = datetime.datetime.now(datetime.UTC)
        now = now_dt.isoformat()
        # 6 months = approx 180 days
        time_max = (now_dt + datetime.timedelta(days=180)).isoformat()

        # Call the Calendar API to get upcoming events.
        # singleEvents=True expands recurring events into individual instances.
        events_result = service.events().list(
            calendarId='primary',
            timeMin=now,
            timeMax=time_max,
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
    

def get_today_tasks():
    """
    Fetches tasks from the primary Google Tasks list that are due today or overdue/undated.
    Returns a list of formatted tasks or an empty list on error.
    """
    if not os.path.exists(TOKEN_FILE):
        return []

    try:
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        service = build('tasks', 'v1', credentials=creds)

        # Fetch all task lists
        lists_result = service.tasklists().list().execute()
        task_lists = lists_result.get('items', [])
        
        target_list_names = ["Today's Tasks", "Daily Goals"]
        lists_to_fetch = [tl for tl in task_lists if tl['title'] in target_list_names]
        
        if not lists_to_fetch:
            # Fallback to default if targets not found
            lists_to_fetch = [{'id': '@default', 'title': "Today's Tasks"}]

        grouped_tasks = []
        now_date = datetime.datetime.now().date()

        for tl in lists_to_fetch:
            results = service.tasks().list(tasklist=tl['id'], showCompleted=False).execute()
            tasks = results.get('items', [])
            if not tasks:
                continue
                
            formatted_tasks = []
            for task in tasks:
                # Check if task is due today, in the past, or has no due date
                due = task.get('due')
                include_task = False
                
                if due:
                    due_date = datetime.datetime.fromisoformat(due.replace('Z', '+00:00')).astimezone().date()
                    if due_date <= now_date:
                        include_task = True
                else:
                    include_task = True # include tasks without due date

                if include_task:
                    formatted_tasks.append({
                        "title": task.get('title', 'Untitled Task'),
                        "due": due,
                        "id": task.get('id')
                    })
            
            if formatted_tasks:
                grouped_tasks.append({"list_title": tl['title'], "tasks": formatted_tasks})
                
        return grouped_tasks

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