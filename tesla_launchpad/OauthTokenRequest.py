import requests
import json
import base64
import boto3
import os
from datetime import datetime

from tesla_launchpad.Constants import base_uri, client_id, client_secret


def oauth_token_request():

    email = os.environ["EMAIL"]
    password = os.environ["PASSWORD"]

    secrets = {
        "email": email,
        "password": base64.b64encode(password.encode()).decode(),
        "client_id": client_id,
        "client_secret": client_secret,
        "access_token": "",
        "token_timestamp": "",
        "refresh_token": "",
        "id": ""
    }

    oauth_token_request_data = {
      "grant_type": "password",
      "client_id": secrets["client_id"],
      "client_secret": secrets["client_secret"],
      "email": secrets["email"],
      "password": password
    }

    print("Requesting token...")
    oauth_token = requests.post(f"{base_uri}/oauth/token?grant_type=password",
                                headers={"user-agent": "tesla_oauth_grant"}, data=oauth_token_request_data)

    secrets["access_token"] = oauth_token.json()["access_token"]
    secrets["token_timestamp"] = datetime.fromtimestamp(oauth_token.json()["created_at"])
    secrets["refresh_token"] = oauth_token.json()["refresh_token"]

    header = {"user-agent": "vehicles-request",
               "Authorization": f"Bearer {secrets['access_token']}",
               "Content-Type": "application/json; charset=utf-8"}

    vehicles = requests.get("https://owner-api.teslamotors.com/api/1/vehicles", headers=header)
    vehicle_count = vehicles.json()["count"]

    if vehicle_count > 1:
        print("You have more than one vehicle tied to your account:\n")
        for idx in range(0, vehicle_count):
            print(f"{idx + 1}. {vehicles.json()['response'][idx]['display_name']}")
        vehicle_idx = input("\nEnter the number of the vehicle you would like to use: ")
        secrets["id"] = vehicles.json()["response"][vehicle_idx]["id"]

    elif vehicle_count < 1:
        print("No vehicles were found for this account.")
        exit()

    else:
        secrets["id"] = vehicles.json()["response"][0]["id"]

    print(secrets)

    bucket_name = "tesla-launchpad"
    secrets_file = "secrets.json"
    session = boto3.Session(
        aws_access_key_id=os.environ["ACCESS_KEY"],
        aws_secret_access_key=os.environ["SECRET_KEY"]
    )
    s3 = session.resource("s3")

    try:
        json_obj = s3.Object(bucket_name, secrets_file)
        json_obj.put(Body=json.dumps(secrets, indent=2, default=str))
        print("\nToken has been created as secrets.json\n")
    except:
        print("\nToken could not be written to storage.\n")


if __name__ == "__main__":
    oauth_token_request()
