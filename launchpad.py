#!/usr/bin/env python3

import sys
from argparse import RawTextHelpFormatter
from argparse import ArgumentParser
from datetime import datetime

from ClimateControl import climate_control


def main():

    parser = ArgumentParser(description="Tesla Launchpad", formatter_class=RawTextHelpFormatter)

    parser.add_argument("--execute", "-e", help="The program you want to execute.", required=True,
                        choices=["ClimateControl"])

    parser.add_argument("--param", "-p", help="Add parameters for your program with format <PARAM_NAME>=<VALUE>",
                        action="append")

    parser.add_argument("--days", "-d", help="What days of the week can this be executed (weekdays, weekends, all)",
                        choices=["weekdays", "weekends", "all"], default="all")

    arg_vars = vars(parser.parse_args())

    command = arg_vars["execute"]
    params = arg_vars["param"]
    param_dict = {}
    try:
        for param in params:
            kv = param.split("=")
            param_dict[kv[0]] = kv[1]
    except TypeError:
        print("No parameters given.")

    # Monday is 0 and Sunday is 6
    weekday = datetime.today().weekday()

    if command == "ClimateControl":

        if arg_vars["days"] == "weekdays" and weekday > 4:
            print("No work today. Cancelling program...")
            return
        elif arg_vars["days"] == "weekends" and weekday < 5:
            print("Not a weekend. Cancelling program...")
            return

        print("Activating climate control...")
        climate_control()


main()
