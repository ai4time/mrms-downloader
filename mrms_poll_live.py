import os
import time

import anylearn

from mrms import MrmsTimer, MrmsDownloader


if os.environ.get('ANYLEARN_TASK_ID', None) is not None:
    data_workspace = anylearn.get_dataset("yhuang/MRMS").download()
else:
    data_workspace = "./data"


def run():
    timer = MrmsTimer()
    downloader = MrmsDownloader(base_dir=data_workspace)
    while True:
        bounds = timer.get_bouding_datetime()
        if downloader.download1(bounds.last):
            wait = timer.get_waiting_time(bounds)
            time.sleep(wait)
        else:
            time.sleep(10)


if __name__ == "__main__":
    run()
