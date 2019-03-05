from datetime import datetime
import json

from tesla_launchpad.ClimateControl import climate_control


def lambda_handler(event, context):

    args = {}
    if event['httpMethod'] == 'POST':
        args = json.loads(event['body'])

    return main(args)


def main(args):
    print(f"Launchpad executed at {datetime.now()}")

    command = args["command"]

    if command == "ClimateControl":

        print("Activating climate control...\n")
        climate_control()

    print("\nLaunchpad shutting down...")
    print("\n\n\n")

    return
