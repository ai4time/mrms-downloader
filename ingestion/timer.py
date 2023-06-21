from dataclasses import dataclass
from datetime import datetime, timedelta, timezone


def round_down(now: datetime, interval: timedelta) -> datetime:
    now_ts = int(now.timestamp())
    interval_s = int(interval.total_seconds())
    last_ts = now_ts - (now_ts % interval_s)
    return datetime.fromtimestamp(last_ts, tz=now.tzinfo)


@dataclass
class TimerBounds:
    last: datetime
    next: datetime


class Timer:

    def __init__(
        self,
        interval: timedelta,
        delay: timedelta = timedelta(0),
        tz: datetime.tzinfo = timezone.utc,
    ):
        if not isinstance(interval, timedelta):
            raise TypeError(f"interval must be a timedelta: {type(interval)} given")
        if interval <= timedelta(0):
            raise ValueError(f"interval must be a positive time delta: {interval} given")
        if not isinstance(delay, timedelta):
            raise TypeError(f"delay must be a timedelta: {type(delay)} given")
        if delay < timedelta(0):
            raise ValueError(f"delay must be a non-negative time delta: {delay} given")

        self.interval = interval
        self.delay = delay
        self.tz = tz

    def get_bouding_datetime(self) -> TimerBounds:
        now = self._now()
        last = round_down(now, self.interval)
        next = last + self.interval
        return TimerBounds(last, next)

    def get_waiting_time(self, bounds: TimerBounds) -> int:
        now = self._now()
        now_ts = int(now.timestamp())
        next_ts = int(bounds.next.timestamp())
        return next_ts - now_ts

    def _now(self) -> datetime:
        return datetime.now(self.tz) - self.delay


class MrmsTimer(Timer):
    
    def __init__(self):
        super().__init__(
            interval=timedelta(minutes=2),
            delay=timedelta(minutes=3, seconds=10),
        )


class TjwfTimer(Timer):
    
    def __init__(self):
        super().__init__(
            interval=timedelta(minutes=6),
            delay=timedelta(0),
            tz=timezone(timedelta(hours=8)),
        )


class FixedDateRealTimeTimer(Timer):

    def __init__(
        self,
        date: datetime,
        interval: timedelta,
        delay: timedelta = timedelta(0),
        tz: datetime.tzinfo = timezone.utc,
    ):
        super().__init__(interval=interval, delay=delay, tz=tz)
        self.date = date

    def _now(self) -> datetime:
        now = super()._now()
        return datetime(
            year=self.date.year,
            month=self.date.month,
            day=self.date.day,
            hour=now.hour,
            minute=now.minute,
            second=now.second,
            microsecond=now.microsecond,
            tzinfo=self.tz,
        )
