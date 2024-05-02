import sys
import os
from datetime import datetime
import hmac
import hashlib

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(SCRIPT_DIR)

"""System modules"""
from libs import slack as Slack
from libs import msteams as Teams
from libs import google_chat as Gchat
from libs.audit import audit
from libs.device_event import device_event
from libs.mxedge_events import mxedge_event
from libs.alarm import alarm
from libs.device_updown import device_updown
from libs.logger import Console
console = Console("mwtt")

#######################################
#  FUNCTIONS


def _get_time(event):
    if "timestamp" in event:
        dt = datetime.fromtimestamp(event["timestamp"])
    else:
        dt = datetime.now()
    return f"{dt} UTC"


def _process_event(topic, event, mist_conf, channels, slack_conf, msteams_conf, gchat_conf):
    """Process new event"""

    if topic == "audits":
        data = audit(
            mist_conf.get("mist_host", None),
            mist_conf.get("approved_admins", []),
            channels.get("audits", {}),
            event
        )
    elif topic == "device-updowns":
        data = device_updown(
            mist_conf.get("mist_host", None),
            channels.get("device-updowns", {}),
            event)
    elif topic == "device-events":
        data = device_event(
            mist_conf.get("mist_host", None),
            channels.get("device-events", {}),
            event
        )
    elif topic == "mxedge-events":
        data = mxedge_event(
            mist_conf.get("mist_host", None),
            channels.get("mxedge-events", {}),
            event
        )
    elif topic == "alarms":
        data = alarm(
            mist_conf.get("mist_host", None),
            channels.get("alarms", {}),
            event
        )
    else:
        data = {
            "text": "",
            "actions": [],
            "info": []}
        for key in event:
            data["info"].append(f"{key}: {event[key]}")

    # dt = _get_time(event)

    if slack_conf.get("enabled"):
        Slack.send_manual_message(
            slack_conf,
            topic,
            data["title"],
            data["text"],
            data["info"],
            data["actions"],
            data["channel"]
        )
    if msteams_conf.get("enabled"):
        Teams.send_manual_message(
            msteams_conf,
            topic,
            data["title"],
            data["text"],
            data["info"],
            data["actions"],
            data["channel"]
        )
    if gchat_conf.get("enabled"):
        Gchat.send_manual_message(
            gchat_conf,
            topic,
            data["title"],
            data["text"],
            data["info"],
            data["actions"],
            data["channel"]
        )


def new_event(req, mist_conf, channels, slack_conf, msteams_conf, gchat_conf):
    '''
    Start to process new webhook message
    request         flask request
    secret          str             webhook secret
    host            str             Mist Cloud host (api.mist.com, ...)
    approved_admins str             List of approved admins (used for audit logs)
    channels        obj             channels config:
                                        {
                                            event_channels: {},
                                            updown_channels: {},
                                            alarm_channels: {},
                                            audit_channels: {}
                                        }
    slack_conf      obj             slack configuration (enable: bool, default_url: str, url: {})
    msteams_conf    obj             MsTeams configuration (enable: bool, default_url: str, url: {})
    console         console
    '''
    secret = mist_conf.get("mist_secret", None)
    if secret:
        signature = req.headers['X-Mist-Signature-v2'] if "X-Mist-Signature-v2" in req.headers else None
        key = str.encode(secret)
        message = req.data
        digester = hmac.new(key, message, hashlib.sha256).hexdigest()
    if secret and signature != digester:
        console.error("Webhook signature doesn't match")
        console.debug(f"message: {req.data}")
        console.debug(f"secret: {secret}")
        console.debug(f"signature: {signature}")
        return '', 401
    elif secret:
        console.info("Webhook signature confirmed")
    console.info("Processing new webhook message")
    content = req.get_json()
    console.debug(content)
    topic = content["topic"]
    if len(channels.get(topic, {})) == 0:
        console.warning(f"topic {topic} is not configured for this org")
        return '', 404

    console.info(f"Message topic: {topic}")
    events = content["events"]
    for event in events:
        _process_event(
            topic,
            event,
            mist_conf,
            channels,
            slack_conf,
            msteams_conf,
            gchat_conf
        )
    return '', 200
