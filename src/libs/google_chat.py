import requests
import json


def _generate_button(actions):
    gchat_buttonList = {}
    if actions:
        gchat_buttonList = {"widgets": {"buttonList": {"buttons": []}}}
        i = 0
        for action in actions:
            i += 1
            gchat_buttonList["widgets"]["buttonList"]["buttons"].append(
                {
                    "text": action["text"],
                    "onClick": {"openLink": {"url": action["url"]}},
                }
            )
    return gchat_buttonList


def _generate_info(info):
    gchat_info = {}
    if info:
        gchat_info = {
            "collapsible": True,
            "uncollapsibleWidgetsCount": 1,
            "widgets": [],
        }

        for entry in info:
            for elem in entry.split("\r\n"):
                if ":" in elem:
                    key = f"<b>{elem.split(':')[0].replace('*', '').replace('>', '').strip()}</b>"
                    value = elem.split(":")[1].strip()
                    gchat_info["widgets"].append(
                        {"decoratedText": {"text": f"{key}: {value}"}}
                    )
                else:
                    gchat_info["widgets"].append({"decoratedText": {"text": elem}})
    return gchat_info


def send_manual_message(
    config, topic, title, text, info=None, actions=None, channel=None
):
    """
    Send message to gchat Channel

    Params:
        config  obj         gchat URL Configuration {default_url: str, url: {channels: str}}
        topic   str         Mist webhook topic
        title   str         Message Title
        text    str         Message Text
        info    [str]       Array of info
        actions [obj]       Array of actions {text: btn text, action: btn url, tag: btn id}
        channel str         gchat Channel
    """
    gchat_info = _generate_info(info)
    gchat_button = _generate_button(actions)
    body = {
        "cardsV2": [
            {
                "cardId": "test",
                "card": {
                    "header": {
                        "title": title,
                        "imageType": "CIRCLE",
                        "imageUrl": "https://store-images.s-microsoft.com/image/apps.19533.84ffe9b6-4972-479a-8cf1-58dffbebffe8.d177c04c-aaa0-42aa-8155-572fe4514fed.537f56b8-8ddd-4d68-8697-e9d67b9a8c8c.png",
                    },
                    "sections": [],
                },
            }
        ]
    }
    if text:
        body["cardsV2"][0]["card"]["header"]["subtitle"] = text

    if gchat_info:
        body["cardsV2"][0]["card"]["sections"].append(gchat_info)
    if gchat_button:
        body["cardsV2"][0]["card"]["sections"].append(gchat_button)

    default_url = config.get("default_url", None)
    gchat_url = config.get("url", {}).get(channel, default_url)
    if gchat_url:
        data = json.dumps(body)
        requests.post(
            gchat_url, headers={"Content-type": "application/json"}, data=data
        )
