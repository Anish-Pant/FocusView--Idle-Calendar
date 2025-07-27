# FocusView-IdleCalendar

Take a quick break, stretch, or look away — and FocusView fades in with your upcoming tasks from Google Calendar. It’s a gentle nudge to keep you in sync with your day. Move your mouse or press a key, and it fades out until next time.

This is a complete rebuild of my earlier project that controlled the Google Calendar PWA. This new version is a native desktop app with a much cleaner look, using the Google Calendar API for a more seamless experience.



### What it does:

*   **Shows Your Agenda:** Displays your upcoming events on clean "glass" panels over a custom background.
*   **Knows When You're Idle:** Pops up automatically after a set time of inactivity.
*   **Connects to Google Calendar:** Pulls your schedule directly from the source.
*   **Gets Out of Your Way:** Vanishes the second you touch your mouse or keyboard.

## Setup

Getting this running involves three main steps: getting the code, setting up Google's permissions, and running the app.

#### 1. Get the Code & Install Packages

First, get the code and install the necessary libraries. I recommend using a virtual environment.

```bash
# Clone the repository
git clone https://github.com/Anish-Pant/FocusView--Idle-Calendar
cd IdleCalendar

# Set up and activate a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install the requirements
pip install -r requirements.txt
```

#### 2. Set Up Google API Access

You need to tell Google your app is allowed to see your calendar.

1.  Go to the **[Google Cloud Console](https.console.cloud.google.com/)**.
2.  Create a new project and **Enable the Google Calendar API**.
3.  Go to the **OAuth consent screen**, choose **External**, and add your email as a **Test User**.
4.  Go to **Credentials**, create an **OAuth client ID** for a **Desktop app**.
5.  **Download the JSON file**. Rename it to `credentials.json` and place it in the project folder.

#### 3. Authorize Your Account

Now, run the `authenticate.py` script once. It will open your browser for you to log in and approve access.

```bash
python authenticate.py
```

This creates a `token.json` file, which is what the main app uses to stay logged in.

## Run It!

That's it for setup. Just run the main script. It will run silently in the background.

```bash
python main.py
```

Move away for 30 seconds, and you should see it appear.

## Configuration

Want to tweak it? Just edit the top of the `main.py` file.

*   `IDLE_THRESHOLD_SECONDS`: Change how long the app waits before appearing.
*   **Background Image:** To use your own background, just replace the `background.jpg` file in the folder with your own image.

**A Quick Note:** This was built for Windows, as it uses the Windows API to check for idle time. It won't work on macOS or Linux out of the box.