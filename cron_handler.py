import requests


def lambda_handler(event, context):
    requests.get("https://izu5gdz14g.execute-api.us-east-1.amazonaws.com/default/teslaLaunchpad?command=ClimateControl&days=all")
    return {
        "status": 200,
        "body": "Lambda executed successfully!"
    }