import requests
from datetime import datetime
from datetime import timedelta
import boto3
import time
import json
import os

from tesla_launchpad.Constants import base_uri, battery_capacity_kwh, fence_points
from tesla_launchpad.OauthTokenRefresh import refresh_oauth_token
from tesla_launchpad.OauthTokenRequest import oauth_token_request
from tesla_launchpad.Picket import Fence


def send_push(pushover_json, message):
    pushover_json["message"] = message
    requests.post("https://api.pushover.net/1/messages.json",
                  headers={"user-agent": "pushover_request"}, data=pushover_json)


def charge_tracker():

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
        access_token, token_timestamp, id = secrets_json["access_token"], secrets_json["token_timestamp"], secrets_json["id"]
    except:
        print("secrets.json does not exist or is corrupted, requesting new token...")
        time.sleep(1)
        oauth_token_request()
        time.sleep(10)
        charge_tracker()
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
            charge_tracker()
            return

    header = {"user-agent": "morning-weather-check",
              "Authorization": f"Bearer {access_token}"
              }

    vehicle_data_request = requests.get(f"{base_uri}/api/1/vehicles/{id}/vehicle_data", headers=header)

    while vehicle_data_request.status_code != 200:
        print("Waking up vehicle...")

        wake_up = requests.post(f"{base_uri}/api/1/vehicles/{id}/wake_up", headers=header)
        print(f"\n{wake_up.json()}\n")

        vehicle_data_request = requests.get(f"{base_uri}/api/1/vehicles/{id}/vehicle_data", headers=header)
        print(f"Vehicle Data status code: {vehicle_data_request.status_code}")

    vehicle_data = vehicle_data_request.json()
    print(json.dumps(vehicle_data, indent=4))

    battery_level = vehicle_data["response"]["charge_state"]["battery_level"]
    battery_level_kwh = (battery_level/100) * battery_capacity_kwh
    charging_state = vehicle_data["response"]["charge_state"]["charging_state"]
    latitude = vehicle_data["response"]["drive_state"]["latitude"]
    longitude = vehicle_data["response"]["drive_state"]["longitude"]
    current_location = (latitude, longitude)

    print(f"battery_level: {battery_level}")
    print(f"charging_state: {charging_state}")
    print(f"latitude: {latitude}")
    print(f"longitude: {longitude}")
    print(f"battery_kwh: {battery_level_kwh}")
    # charging_state: Charging/ Disconnected/
    fence = Fence(fence_points)
    if fence.check_point(current_location):
        isHome = True
        print("Vehicle is inside the geofence.")
    else:
        isHome = False
        print("Vehicle is outside the geofence.")

    '''
    get rates from austin energy site https://austinenergy.com/ae/rates/residential-rates/residential-electric-rates-and-line-items
    set up amazon iot button
    get pandas for csv creation (or create an aws database)
    schema = start_ts|start_kwh|stop_ts|stop_kwh|total_charge_kwh
    '''




if __name__ == "__main__":
    charge_tracker()
