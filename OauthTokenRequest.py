#!/usr/bin/env python3

import requests
import json
import os
from datetime import datetime

from Constants import base_uri, client_id, client_secret


def oauth_token_request():

    email = input("Enter your Tesla account email address: ")
    password = input("Enter your Tesla account password: ")

    secrets = {
        "email": email,
        "password": password,
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
      "password": secrets["password"]
    }

    oauth_token = requests.post(f"{base_uri}/oauth/token?grant_type=password",
                                headers={"user-agent": "tesla_oauth_grant"}, data=oauth_token_request_data)

    secrets["access_token"] = oauth_token.json()["access_token"]
    secrets["token_timestamp"] = datetime.utcfromtimestamp(oauth_token.json()["created_at"])
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

    file_path = os.path.dirname(__file__)
    secrets_path = os.path.join(file_path, "secrets.json")

    with open(secrets_path, "w+") as secrets_file:
        json.dump(secrets, secrets_file, indent=2, default=str)


if __name__ == "__main__":
    oauth_token_request()
