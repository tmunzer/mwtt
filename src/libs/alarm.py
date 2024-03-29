from .alarm_security import SecurityAlarm
from .alarm_infra import InfraAlarm
from .alarm_marvis import MarvisAlarm
from .alarm_common import CommonAlarm

def alarm(mist_host, alarm_channels, mist_event):

    event = None
    if "group" in mist_event:
        if mist_event["group"] == "infrastructure":
            event = InfraAlarm(mist_host, alarm_channels, mist_event)
        elif mist_event["group"] == "marvis":
            event = MarvisAlarm(mist_host, alarm_channels, mist_event)
        elif mist_event["group"] == "security":
            event = SecurityAlarm(mist_host, alarm_channels, mist_event)
    if not event:
        event = CommonAlarm(mist_host, alarm_channels, mist_event)

    return event.get()
