#!/usr/bin/env python3

import os
import shutil
import time

tesla_cam_path = "/TeslaCam"
save_path = "/home/pi/TeslaCamArchives"

while True:

    archived_videos = os.listdir(save_path)

    os.chdir(tesla_cam_path)
    for file in os.listdir("."):
        file_size = os.stat(os.path.join(tesla_cam_path, file)).st_size

        if file_size > 1000 and file not in archived_videos:
            shutil.copy2(file, save_path)

    time.sleep(300)
