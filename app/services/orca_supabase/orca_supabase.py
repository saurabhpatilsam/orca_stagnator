import os
from supabase import create_client, Client
from dotenv import load_dotenv

from app.utils.decorators.timing.time import time_it

# Load .env
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", default='https://dcoukhtfcloqpfmijock.supabase.co')
SUPABASE_KEY = os.getenv("SUPABASE_KEY", default='sb_secret__t3NV0SUY8ywb2y_44jRDA_JOcR--G_')

from zoneinfo import ZoneInfo
# Create Supabase client
SUPABASE: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
LONDON = ZoneInfo("Europe/London")


def stream_ticks(table: str, page_size: int = 1000):
    start = 0
    while True:
        end = start + page_size - 1
        resp = (
            SUPABASE.table(table)
              .select("*")
              .order("ts", desc=True)
              .range(start, end)
              .execute()
        )
        batch = resp.data or []
        if not batch:
            break
        for row in batch:
            yield row
        if len(batch) < page_size:
            break
        start += page_size

from datetime import datetime, timedelta

def stream_ticks_keyset1(
    table: str,
    data_from: datetime,
    data_to: datetime,
    page_size: int = 1000
):
    """
    Stream tick data from Supabase in descending order,
    restricted to minute-level range [data_from, data_to).

    Both datetimes are truncated to the start of their minute.
    Yields rows one by one.
    """
    # --- truncate to minute precision ---
    data_from = data_from.replace(second=0, microsecond=0)
    data_to = data_to.replace(second=0, microsecond=0)

    # make sure we include the entire last minute
    data_to_exclusive = data_to + timedelta(minutes=1)

    # Convert to ISO strings for Supabase filters
    from_iso = data_from.isoformat()
    to_iso = data_to_exclusive.isoformat()

    last_ts = None
    last_id = None

    while True:
        q = (
            SUPABASE.table(table)
            .select("*")
            .order("ts", desc=False)
            .gte("ts", from_iso)   # ts >= data_from
            .lt("ts", to_iso)      # ts < data_to + 1 min
            .limit(page_size)
        )

        if last_ts is not None:
            # Keyset pagination: fetch only rows before the last seen timestamp/id
            q = q.or_(f"ts.lt.{last_ts},and(ts.eq.{last_ts},id.lt.{last_id})")

        resp = q.execute()
        batch = resp.data or []
        if not batch:
            break

        for row in batch:
            yield row

        if len(batch) < page_size:
            break

        # advance cursor
        last_ts = batch[-1]["ts"]
        last_id = batch[-1]["id"]


def stream_ticks_keyset(
    table: str,
    data_from: datetime,
    data_to: datetime,
    page_size: int = 1000
):
    """
    Stream tick data from Supabase in ascending order using keyset pagination
    over the composite key (ts, id), restricted to [data_from, data_to] at
    minute precision.
    """
    # --- truncate to minute precision ---
    data_from = data_from.replace(second=0, microsecond=0)
    data_to = data_to.replace(second=0, microsecond=0)

    # include the entire last minute
    data_to_exclusive = data_to + timedelta(minutes=1)

    from_iso = data_from.isoformat()
    to_iso = data_to_exclusive.isoformat()

    last_ts = None
    last_id = None

    while True:
        q = (
            SUPABASE.table(table)
            .select("*")
            # order by BOTH keys to match the keyset predicate
            .order("ts", desc=False)
            .order("id", desc=False)
            .gte("ts", from_iso)
            .lt("ts", to_iso)
            .limit(page_size)
        )

        if last_ts is not None:
            # For ASC order, use "greater than" for the cursor
            # (ts, id) > (last_ts, last_id)
            q = q.or_(
                f"ts.gt.{last_ts},and(ts.eq.{last_ts},id.gt.{last_id})"
            )

        resp = q.execute()
        batch = resp.data or []
        if not batch:
            break

        for row in batch:
            yield row

        # advance cursor to the last row we returned
        last_ts = batch[-1]["ts"]
        last_id = batch[-1]["id"]

        # when the final page is shorter than page_size, we’re done
        if len(batch) < page_size:
            break


if __name__ == '__main__':
    # Example: stream data between July 24 and July 25, 2025
    start_time = datetime(2025, 7, 25, 15, 0,  tzinfo=LONDON)  # from 18:05
    end_time = datetime(2025, 7, 25, 18, 10, tzinfo=LONDON) # until 18:10
    for tick in stream_ticks_keyset("ticks_nq", start_time, end_time):
        # do something useful here
        print(tick)

    # dd= get_all_data()
    # d=3