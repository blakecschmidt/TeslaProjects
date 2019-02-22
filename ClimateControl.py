#!/usr/bin/env python3

import requests
import time
from datetime import datetime
from datetime import timedelta
import os

from Constants import base_uri
from OauthTokenRefresh import refresh_oauth_token


def climate_control():

    file_path = os.path.dirname(__file__)
    secrets_path = os.path.join(file_path, "secrets.json")

    with open(secrets_path) as secrets_file:
        args = eval(secrets_file.read())
        access_token, token_timestamp, id = args["access_token"], args["token_timestamp"], args["id"]

    token_expiration_ts = datetime.strptime(token_timestamp, "%Y-%m-%d %H:%M:%S") + timedelta(days=45)
    current_ts = datetime.utcnow()

    if current_ts > token_expiration_ts:
        refresh_oauth_token()
        with open(secrets_path) as secrets_file:
            args = eval(secrets_file.read())
            access_token, id = args["access_token"], args["id"]

    header = {"user-agent": "morning-weather-check",
              "Authorization": f"Bearer {access_token}"
              }

    # Wake up vehicle and wait until its online
    wake_up = requests.post(f"{base_uri}/api/1/vehicles/{id}/wake_up", headers=header)
    time.sleep(60)

    climate_state = requests.get(f"{base_uri}/api/1/vehicles/{id}/data_request/climate_state", headers=header)
    print(climate_state.json())
    inside_temp = climate_state.json()["response"]["inside_temp"]*(9/5) + 32
    print(inside_temp)

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

    if 50 <= inside_temp < 60:
        requests.post(f"{base_uri}/api/1/vehicles/{id}/command/auto_conditioning_start",
                      headers=header)
        requests.post(f"{base_uri}/api/1/vehicles/{id}/command/remote_seat_heater_request", headers=header,
                      data=seat_heater_driver_medium)
        requests.post(f"{base_uri}/api/1/vehicles/{id}/command/set_temps", headers=header,
                      data=set_temps_72_f)
        print(f"Inside temp was {inside_temp} F. Temperature set to 72 F and the driver's seat heater is set to medium.")

    elif 40 <= inside_temp < 50:
        requests.post(f"{base_uri}/api/1/vehicles/{id}/command/auto_conditioning_start",
                      headers=header)
        requests.post(f"{base_uri}/api/1/vehicles/{id}/command/remote_seat_heater_request", headers=header,
                      data=seat_heater_driver_medium)
        requests.post(f"{base_uri}/api/1/vehicles/{id}/command/set_temps", headers=header,
                      data=set_temps_77_f)
        print(f"Inside temp was {inside_temp} F. Temperature set to 77 F and the driver's seat heater is set to medium.")

    elif inside_temp < 40:
        requests.post(f"{base_uri}/api/1/vehicles/{id}/command/auto_conditioning_start",
                      headers=header)
        requests.post(f"{base_uri}/api/1/vehicles/{id}/command/remote_seat_heater_request", headers=header,
                      data=seat_heater_driver_medium)
        requests.post(f"{base_uri}/api/1/vehicles/{id}/command/set_temps", headers=header,
                      data=set_temps_80_f)
        print(f"Inside temp was {inside_temp} F. Temperature set to 80 F and the driver's seat heater is set to medium.")
    else:
        print("Climate controls were not activated.")


if __name__ == "__main__":
    climate_control()

