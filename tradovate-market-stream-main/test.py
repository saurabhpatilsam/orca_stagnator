from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import json
from dotenv import load_dotenv
import os
uk_time_now = datetime.now(timezone.utc)\
                .astimezone(ZoneInfo("Europe/London"))\
                .strftime("%Y-%m-%d %H:%M:%S.%f")

print(uk_time_now)