#!/usr/bin/env python3

import requests
from Constants import base_uri


#this will return 404 when car is asleep
#wake_up = requests.get(f"https://owner-api.teslamotors.com/api/1/vehicles/{id}/wake_up", headers=header)

#this only works when the car is awake (when I manually wake up my car via phone app or getting in it)
#charge_state = requests.get(f"https://owner-api.teslamotors.com/api/1/vehicles/{id}/data_request/charge_state", headers=header)
#print(charge_state.json())

