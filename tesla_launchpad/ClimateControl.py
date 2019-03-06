import requests
from datetime import datetime
from datetime import timedelta
import boto3
import time
import json
import os

from tesla_launchpad.Constants import base_uri
from tesla_launchpad.OauthTokenRefresh import refresh_oauth_token
from tesla_launchpad.OauthTokenRequest import oauth_token_request


def send_push(pushover_json, message):
    pushover_json["message"] = message
    requests.post("https://api.pushover.net/1/messages.json",
                  headers={"user-agent": "pushover_request"}, data=pushover_json)


def climate_control():

    bucket_name = "tesla-launchpad"
    secrets_file = "secrets.json"
    pushover_file = "pushover.json"
    session = boto3.Session(
        aws_access_key_id=os.environ["ACCESS_KEY"],
        aws_secret_access_key=os.environ["SECRET_KEY"]
    )
    s3 = session.resource("s3")

    try:
        pushover_json = json.loads(s3.Object(bucket_name, pushover_file).get()["Body"].read())
        has_pushover = True
    except:
        print("pushover.json does not exist.")
        has_pushover = False

    try:
        secrets_json = json.loads(s3.Object(bucket_name, secrets_file).get()["Body"].read())
        print(secrets_json)
        access_token, token_timestamp, id = secrets_json["access_token"], secrets_json["token_timestamp"], secrets_json["id"]
    except:
        print("secrets.json does not exist or is corrupted, requesting new token...")
        time.sleep(1)
        oauth_token_request()
        time.sleep(10)
        climate_control()
        return

    token_expiration_ts = datetime.strptime(token_timestamp, "%Y-%m-%d %H:%M:%S") + timedelta(days=45)
    current_ts = datetime.now()

    if current_ts > token_expiration_ts:
        print("Token has expired...")
        refresh_oauth_token()
        try:
            secrets_json = json.loads(s3.Object(bucket_name, secrets_file).get()["Body"].read())
            access_token, id = secrets_json["access_token"], secrets_json["id"]
        except:
            print("secrets.json does not exist, requesting new token...")
            oauth_token_request()
            climate_control()
            return

    header = {"user-agent": "morning-weather-check",
              "Authorization": f"Bearer {access_token}"
              }

    # Wake up vehicle and wait until its online
    climate_state = requests.get(f"{base_uri}/api/1/vehicles/{id}/data_request/climate_state", headers=header)

    while climate_state.status_code != 200:
        print("Waking up vehicle...")

        wake_up = requests.post(f"{base_uri}/api/1/vehicles/{id}/wake_up", headers=header)
        print(f"\n{wake_up.json()}\n")

        climate_state = requests.get(f"{base_uri}/api/1/vehicles/{id}/data_request/climate_state", headers=header)
        print(f"Climate State status code: {climate_state.status_code}")

    print(f"\n{climate_state.json()}\n")
    outside_temp = round(climate_state.json()["response"]["outside_temp"]*(9/5) + 32, 2)
    print(outside_temp)

    seat_heater_driver_medium = {
                                 "heater": "0",
                                 "level": "2"
                                 }
    set_temps_72_f = {
                      "driver_temp": "22.2",
                      "passenger_temp": "22.2"
                      }
    set_temps_77_f = {
                      "driver_temp": "25.0",
                      "passenger_temp": "25.0"
                      }
    set_temps_80_f = {
                      "driver_temp": "26.6",
                      "passenger_temp": "26.6"
                      }

    if 60 <= outside_temp < 70:
        requests.post(f"{base_uri}/api/1/vehicles/{id}/command/auto_conditioning_start",
                      headers=header)
        requests.post(f"{base_uri}/api/1/vehicles/{id}/command/set_temps", headers=header,
                      data=set_temps_72_f)

        message = f"Outside temp was {outside_temp} F. Temperature set to 72 F."
        print(message)

        if has_pushover:
            send_push(pushover_json, message)

    elif 50 <= outside_temp < 60:
        requests.post(f"{base_uri}/api/1/vehicles/{id}/command/auto_conditioning_start",
                      headers=header)
        requests.post(f"{base_uri}/api/1/vehicles/{id}/command/remote_seat_heater_request", headers=header,
                      data=seat_heater_driver_medium)
        requests.post(f"{base_uri}/api/1/vehicles/{id}/command/set_temps", headers=header,
                      data=set_temps_72_f)

        message = f"Outside temp was {outside_temp} F. Temperature set to 72 F and the driver's seat heater is set to medium."
        print(message)

        if has_pushover:
            send_push(pushover_json, message)

    elif 40 <= outside_temp < 50:
        requests.post(f"{base_uri}/api/1/vehicles/{id}/command/auto_conditioning_start",
                      headers=header)
        requests.post(f"{base_uri}/api/1/vehicles/{id}/command/remote_seat_heater_request", headers=header,
                      data=seat_heater_driver_medium)
        requests.post(f"{base_uri}/api/1/vehicles/{id}/command/set_temps", headers=header,
                      data=set_temps_77_f)

        message = f"Outside temp was {outside_temp} F. Temperature set to 77 F and the driver's seat heater is set to medium."
        print(message)

        if has_pushover:
            send_push(pushover_json, message)

    elif outside_temp < 40:
        requests.post(f"{base_uri}/api/1/vehicles/{id}/command/auto_conditioning_start",
                      headers=header)
        requests.post(f"{base_uri}/api/1/vehicles/{id}/command/remote_seat_heater_request", headers=header,
                      data=seat_heater_driver_medium)
        requests.post(f"{base_uri}/api/1/vehicles/{id}/command/set_temps", headers=header,
                      data=set_temps_80_f)

        message = f"Outside temp was {outside_temp} F. Temperature set to 80 F and the driver's seat heater is set to medium."
        print(message)

        if has_pushover:
            send_push(pushover_json, message)

    else:
        message = f"Outside temperature is {outside_temp} F. Climate controls were not activated."
        print(message)

        if has_pushover:
            send_push(pushover_json, message)


if __name__ == "__main__":
    climate_control()

