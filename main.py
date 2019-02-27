from datetime import datetime

from tesla_launchpad.ClimateControl import climate_control


def lambda_handler(event, context):
    args = event["queryStringParameters"]["command"], event["queryStringParameters"]["days"]
    main(args)
    return {
        "status": 200,
        "body": "Lambda executed successfully!"
    }


def main(args):
    print(f"Launchpad executed at {datetime.now()}")


    command = args[0]
    days = args[1]
    params = []
    param_dict = {}
    try:
        for param in params:
            kv = param.split("=")
            param_dict[kv[0]] = kv[1]
    except TypeError:
        pass

    # Monday is 0 and Sunday is 6
    weekday = datetime.today().weekday()

    if command == "ClimateControl":

        if days == "weekdays" and weekday > 4:
            print("No work today. Cancelling program...")
            return
        elif days == "weekends" and weekday < 5:
            print("Not a weekend. Cancelling program...")
            return

        print("Activating climate control...\n")
        climate_control()

    print("\nLaunchpad shutting down...")
    print("\n\n\n")

    return
