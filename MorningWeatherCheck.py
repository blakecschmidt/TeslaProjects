#!/usr/bin/env python3

import requests
import json
import time
from datetime import datetime
from datetime import timedelta

from Constants import base_uri
from OauthTokenRefresh import refresh_oauth_token


def morning_weather_check():

    with open("secrets.json") as secrets_file:
        args = eval(secrets_file.read())
        access_token, token_timestamp, id = args["access_token"], args["token_timestamp"], args["id"]

    token_expiration_ts = datetime.strptime(token_timestamp, "%Y-%m-%d %H:%M:%S") + timedelta(days=45)
    current_ts = datetime.utcnow()

    if current_ts > token_expiration_ts:
        refresh_oauth_token()
        time.sleep(5)

        with open("secrets.json") as secrets_file:
            args = eval(secrets_file.read())
            access_token, id = args["access_token"], args["id"]

    header = {"user-agent": "morning-weather-check",
              "Authorization": f"Bearer {access_token}",
              "Content-Type": "application/json; charset=utf-8"}

    #wake_up = requests.post(f"https://owner-api.teslamotors.com/api/1/vehicles/{id}/wake_up", headers=header)
    #print(wake_up.json())

    #this only works when the car is awake (when I manually wake up my car via phone app or getting in it)
    #charge_state = requests.get(f"https://owner-api.teslamotors.com/api/1/vehicles/{id}/data_request/charge_state", headers=header)
    #print(charge_state.json())


if __name__ == "__main__":
    morning_weather_check()

