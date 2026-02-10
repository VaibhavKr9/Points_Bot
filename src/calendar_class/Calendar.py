from google.oauth2 import service_account
from googleapiclient.discovery import build
import datetime

class Calendar:
    def __init__(self):
        self._creds = service_account.Credentials.from_service_account_file(
            'discord-bot-dipc.json',
             scopes=["https://www.googleapis.com/auth/calendar.readonly"])
        
        self._calendar = build("calendar", "v3", credentials=self._creds)

    def get(self):
        now = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
        print("Getting the upcoming 10 events")
        events_result = self._calendar.events().list(
                calendarId="82a78296921f8716050017647ed3bdb8cb164c97e2901cdc11c6b6922670e47e@group.calendar.google.com",
                timeMin=now,
                maxResults=10,
                singleEvents=True,
                orderBy="startTime",
            ).execute()
        events = events_result.get("items", [])

        if not events:
            print("No upcoming events found.")
            return

        # Prints the start and name of the next 10 events
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            name = event["summary"]
            print(name, start)

    def getAllCalendars(self):
        calendar_list = self._calendar.calendarList().list().execute()
        print(calendar_list)
        '''calendars = calendar_list.get("items", [])
        for calendar in calendars:
            print(calendar["summary"], calendar["id"])'''

    def getNextRaceInfo(self) -> tuple[str, datetime.datetime, datetime.datetime]:
        now = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
        events_result = self._calendar.events().list(
                calendarId="82a78296921f8716050017647ed3bdb8cb164c97e2901cdc11c6b6922670e47e@group.calendar.google.com",
                timeMin=now,
                maxResults=10,
                singleEvents=True,
                orderBy="startTime",
            ).execute()
        
        events = events_result.get("items", [])
        if events:
            for ind, event in enumerate(events):
                if "- Race" in event["summary"]:
                    raceName: str = event["summary"][1:-7]
                    raceTimeStr: str = event["start"].get("dateTime", event["start"].get("date"))
                    raceTime = datetime.datetime.fromisoformat(raceTimeStr.replace("Z", "+00:00"))
                    try:
                        qualiTimeStr: str = events[ind - 1]["start"].get("dateTime", events[ind - 1]["start"].get("date"))
                        qualiTime = datetime.datetime.fromisoformat(qualiTimeStr.replace("Z", "+00:00"))
                    except IndexError:
                        qualiTime = None

                    return (raceName, qualiTime, raceTime)
        
        return (None, None, None)

if __name__ == "__main__":
    calendar = Calendar()
    calendar.get()