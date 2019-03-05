from datetime import datetime

from tesla_launchpad.ClimateControl import climate_control


def lambda_handler(event, context):
    args = event["event"]["command"]
    main(args)
    return {
        "status": 200,
        "body": "Lambda executed successfully!"
    }


def main(args):
    print(f"Launchpad executed at {datetime.now()}")

    command = args

    if command == "ClimateControl":

        print("Activating climate control...\n")
        climate_control()

    print("\nLaunchpad shutting down...")
    print("\n\n\n")

    return
