from datetime import datetime
import json

from tesla_launchpad.ClimateControl import climate_control


def lambda_handler(event, context):

    command = None
    try:
        if event['httpMethod'] == 'POST':
            args = json.loads(event['body'])
            command = args["command"]
    except KeyError:
        command = event["command"]

    return main(command)


def main(command):
    print(f"Launchpad executed at {datetime.now()}")

    if command is None:
        print("ERROR: No command given.")
        return

    if command == "ClimateControl":

        print("Activating climate control...\n")
        climate_control()

    print("\nLaunchpad shutting down...")
    print("\n\n\n")

    return
