#!/usr/bin/env bash

zip -r teslaLaunchpad.zip dependencies/
zip -r teslaLaunchpad.zip tesla_launchpad/
zip teslaLaunchpad.zip main.py

aws lambda update-function-code --function-name teslaLaunchpad --zip-file fileb://teslaLaunchpad.zip

rm teslaLaunchpad.zip
