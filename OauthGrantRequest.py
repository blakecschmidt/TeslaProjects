#!/usr/bin/env python3

import requests
import json
from datetime import datetime

from Constants import base_uri

with open("secrets.json") as secrets_file:
    args = eval(secrets_file.read())

oauth_grant_request_data = {
  "grant_type": "password",
  "client_id": args["client_id"],
  "client_secret": args["client_secret"],
  "email": args["email"],
  "password": args["password"]
}

oauth_grant = requests.post(base_uri + "oauth/token?grant_type=password",
                            headers={"user-agent": "tesla_oauth_grant"}, data=oauth_grant_request_data)

header = {"user-agent": "vehicles-request/0.0.1",
           "Authorization": f"Bearer {oauth_grant.json()['access_token']}",
           "Content-Type": "application/json; charset=utf-8"}

vehicles = requests.get("https://owner-api.teslamotors.com/api/1/vehicles", headers=header)
vehicle_count = vehicles.json()["count"]

if vehicle_count > 1:
    print("You have more than one vehicle tied to your account:\n")
    for idx in range(0, vehicle_count):
        print(f"{idx + 1}. {vehicles.json()['response'][idx]['display_name']}")
    vehicle_idx = input("\nEnter the number of the vehicle you would like to use: ")
    id = vehicles.json()["response"][vehicle_idx]["id"]

elif vehicle_count < 1:
    print("No vehicles were found for this account.")
    id = None
    exit()

else:
    id = vehicles.json()["response"][0]["id"]

args["access_token"] = oauth_grant.json()["access_token"]
args["token_timestamp"] = datetime.utcfromtimestamp(oauth_grant.json()["created_at"])
args["refresh_token"] = oauth_grant.json()["refresh_token"]
args["id"] = str(id)


with open("secrets.json", "w") as secrets_file:
    json.dump(args, secrets_file, indent=2, default=str)
