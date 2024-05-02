"""System modules"""
import os
import sys
from datetime import datetime

from flask import Flask
from flask import request
from config import mist_conf
from config import slack_conf
from config import msteams_conf
from config import gchat_conf
from config import event_channels
from config import updown_channels
from config import alarm_channels
from config import mxedge_events
from config import audit_channels
###########################
# APP SETTINGS
DEBUG = False
LOG_LEVEL = "INFO"
SERVER_PORT = 51361

try:
    import config
    if hasattr(config, 'debug'):
        DEBUG = config.debug
    if hasattr(config, 'log_level'):
        print(config.log_level)
        LOG_LEVEL = config.log_level
    if hasattr(config, 'port'):
        SERVER_PORT = config.port
except:
    pass
finally:
    os.environ["LOG_LEVEL"]= LOG_LEVEL
    if not DEBUG:
        os.environ['FLASK_ENV'] = 'PRODUCTION'
    import mwtt
    from libs.logger import Console
    console = Console("main")
###########################
# CONF FUNCTIONS
def load_conf(value):
    """Process config"""
    print(f"Loading {value} ".ljust(79, "."), end="", flush=True)
    if value in mist_conf:
        print("\033[92m\u2714\033[0m")
        return mist_conf[value]
    else:
        print('\033[31m\u2716\033[0m')
        sys.exit(255)


def display_conf():
    """Display config"""
    print(f"Mist Hist       : {MIST_HOST}")
    print(f"Webhook Secret  : {MIST_SECRET}")
    print(f"MWTT URI        : {SERVER_URI}")
    print(f"Ignored Sites   : {SITE_ID_IGNORED}")
    print(f"Approved Admins : {APPROVED_ADMINS}")
    print(f"Debug Mode      : {DEBUG}")
    print()
    print(f"SLACK           : {slack_conf.get('enabled', False)}")
    print(f"MS Teams        : {msteams_conf.get('enabled', False)}")
    print(f"Google Chat     : {gchat_conf.get('enabled', False)}")


###########################
# ENTRY POINT
print("Loading configuration ".center(80, "_"))
MIST_HOST = load_conf("mist_host")
MIST_SECRET = load_conf("mist_secret")
SERVER_URI = load_conf("server_uri")
SITE_ID_IGNORED = load_conf("site_id_ignored")
APPROVED_ADMINS = load_conf("approved_admins")
print("Configuraiton loaded".center(80, "_"))
display_conf()

app = Flask(__name__)


@app.route(SERVER_URI, methods=["POST"])
def postJsonHandler():
    console.info(" New message reveived ".center(60, "-"))
    start =  datetime.now()
    res= mwtt.new_event(
        request,
        mist_conf,
        {
            "device-events": event_channels,
            "device-updowns": updown_channels,
            "alarms": alarm_channels,
            "mxedge-events": mxedge_events,
            "audits": audit_channels
        },
        slack_conf,
        msteams_conf,
        gchat_conf
    )
    delta = datetime.now() - start
    console.info(f"Processing time {delta.seconds}.{delta.microseconds}s")
    return res
    # mwtt.new_event(topic, event)


if __name__ == '__main__':
    print(f"Starting Server: 0.0.0.0:{SERVER_PORT}".center(80, "_"))
    app.run(debug=False, host='0.0.0.0', port=SERVER_PORT)
