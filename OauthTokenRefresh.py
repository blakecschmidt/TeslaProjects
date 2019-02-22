#!/usr/bin/env python3

import requests
import json
import os
from datetime import datetime

from Constants import base_uri


def refresh_oauth_token():

    file_path = os.path.dirname(__file__)
    secrets_path = os.path.join(file_path, "secrets.json")

    with open(secrets_path) as secrets_file:
        args = eval(secrets_file.read())

    oauth_token_refresh_data = {
      "grant_type": "refresh_token",
      "client_id": args["client_id"],
      "client_secret": args["client_secret"],
      "refresh_token": args["refresh_token"]
    }

    oauth_token = requests.post(base_uri + "oauth/token?grant_type=refresh_token",
                                headers={"user-agent": "tesla_oauth_refresh"}, data=oauth_token_refresh_data)

    args["access_token"] = oauth_token.json()["access_token"]
    args["token_timestamp"] = datetime.utcfromtimestamp(oauth_token.json()["created_at"])
    args["refresh_token"] = oauth_token.json()["refresh_token"]

    with open(secrets_path, "w") as secrets_file:
        json.dump(args, secrets_file, indent=2, default=str)


if __name__ == "__main__":
    refresh_oauth_token()
