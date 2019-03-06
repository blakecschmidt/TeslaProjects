import requests
import json
import boto3
import os
from datetime import datetime

from tesla_launchpad.Constants import base_uri
from tesla_launchpad.OauthTokenRequest import oauth_token_request


def refresh_oauth_token():
    print("Refreshing token...")

    bucket_name = "tesla-launchpad"
    secrets_file = "secrets.json"
    session = boto3.Session(
        aws_access_key_id=os.environ["ACCESS_KEY"],
        aws_secret_access_key=os.environ["SECRET_KEY"]
    )
    s3 = session.resource("s3")

    try:
        secrets_json = json.loads(s3.Object(bucket_name, secrets_file).get()["Body"].read())
    except:
        print("secrets.json file does not exist or is corrupted, requesting new token...")
        oauth_token_request()
        return

    oauth_token_refresh_data = {
      "grant_type": "refresh_token",
      "client_id": secrets_json["client_id"],
      "client_secret": secrets_json["client_secret"],
      "refresh_token": secrets_json["refresh_token"]
    }

    oauth_token = requests.post(f"{base_uri}/oauth/token?grant_type=refresh_token",
                                headers={"user-agent": "tesla_oauth_refresh"}, data=oauth_token_refresh_data)

    secrets_json["access_token"] = oauth_token.json()["access_token"]
    secrets_json["token_timestamp"] = datetime.utcfromtimestamp(oauth_token.json()["created_at"])
    secrets_json["refresh_token"] = oauth_token.json()["refresh_token"]

    try:
        json_obj = s3.Object(bucket_name, secrets_file)
        json_obj.put(Body=json.dumps(secrets_json, indent=2, default=str))
        print("Token has been created as secrets.json\n")
    except:
        print("Token could not be written to storage.\n")


if __name__ == "__main__":
    refresh_oauth_token()
