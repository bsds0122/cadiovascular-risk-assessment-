from datetime import datetime
from zoneinfo import ZoneInfo

def get_greeting():
    now = datetime.now(ZoneInfo("Africa/Blantyre"))
    period = now.strftime("%p")  # "AM" or "PM"

    if period == "AM":
        return "Good Morning"
    else:
        return "Good Afternoon / Evening"

print(get_greeting())