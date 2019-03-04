import requests
import time
import json
from datetime import datetime
from datetime import timedelta
import os

from tesla_launchpad.Constants import base_uri
from tesla_launchpad.OauthTokenRefresh import refresh_oauth_token
from tesla_launchpad.OauthTokenRequest import oauth_token_request


def send_push(pushover_json, message):

    pushover_json["message"] = message
    requests.post("https://api.pushover.net/1/messages.json",
                  headers={"user-agent": "pushover_request"}, data=pushover_json)


def charge_tracker():
    file_path = os.path.dirname(__file__)
    secrets_path = os.path.join(file_path, "secrets.json")
    pushover_path = os.path.join(file_path, "pushover.json")
    pushover_json = {}

    try:
        with open(pushover_path) as pushover_file:
            pushover_json = json.load(pushover_file)
            has_pushover = True

    except FileNotFoundError:
        has_pushover = False

    try:
        with open(secrets_path) as secrets_file:
            args = eval(secrets_file.read())
            access_token, token_timestamp, id = args["access_token"], args["token_timestamp"], args["id"]

    except FileNotFoundError:
        print("secrets.json file not found, requesting new token...")
        oauth_token_request()
        charge_tracker()
        return

    except SyntaxError:
        print("secrets.json file corrupted, requesting new token...")
        oauth_token_request()
        charge_tracker()
        return

    except KeyError:
        print("secrets.json does not contain a key that is needed, requesting new token...")
        oauth_token_request()
        charge_tracker()
        return

    token_expiration_ts = datetime.strptime(token_timestamp, "%Y-%m-%d %H:%M:%S") + timedelta(days=45)
    current_ts = datetime.now()

    if current_ts > token_expiration_ts:
        print("Token has expired...")
        refresh_oauth_token()
        with open(secrets_path) as secrets_file:
            args = eval(secrets_file.read())
            access_token, id = args["access_token"], args["id"]

    header = {"user-agent": "morning-weather-check",
              "Authorization": f"Bearer {access_token}"
              }