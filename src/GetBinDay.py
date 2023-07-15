from datetime import datetime
import logging
import os
from time import sleep
import requests
import json
import urllib3
from urllib3.util.ssl_ import create_urllib3_context

logging.basicConfig(level=logging.INFO)
logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

BIN_DAY_URL = os.environ.get("BIN_DAY_URL")

HA_URL = os.environ.get("HA_URL")
HA_TOKEN = os.environ.get("HA_TOKEN")

headers = {
  "Authorization": f"Bearer {HA_TOKEN}",
  "Content-Type": "application/json"
}

def GetBinDay():
    logging.info("Getting latest bin day infomation")
    ctx = create_urllib3_context()
    ctx.load_default_certs()
    ctx.options |= 0x4

    with urllib3.PoolManager(ssl_context=ctx) as http:
        response = http.request("GET", BIN_DAY_URL)
    return json.loads(response.data.decode("utf-8"))

def SendData(binType, schedule):
    if binType == "black":
        friendly_name = "Next Black Bin Day"
        next_date_str = schedule["residualNextDate"]
    if binType == "green":
        friendly_name = "Next Recycling Day"
        next_date_str = schedule["recyclingNextDate"]

    today = datetime.today()
    next_date = datetime.strptime(next_date_str,"%Y-%m-%dT%H:%M:%S.%fZ")
    days_to_go = (next_date - today).days

    if days_to_go < 1:
        message = "Today"
    elif days_to_go < 2:
        message = "Tomorrow"
    elif days_to_go < 6:
        message = f"This {next_date.strftime('%A')}"
    elif days_to_go < 13:
        message = f"Next {next_date.strftime('%A')}"
    else:
        message = f"{next_date.strftime('%d %b')}"

    payload = json.dumps(
        {
            "state": message,
            "attributes": {
                "friendly_name": friendly_name
            }
        }
    )

    url = f"{HA_URL}/sensor.{binType}_bin_day"
    logging.debug(f"Sending {binType} bin day info to HA")
    response = requests.post(url=url, headers=headers, data=payload)

BIN_DAY_URL_REFRESH_RATE = 3600
HA_UPDATE_RATE = 30

schedule = GetBinDay()

count = 0
max_count = BIN_DAY_URL_REFRESH_RATE/HA_UPDATE_RATE

while True:
    count += 1
    
    SendData("black", schedule)
    SendData("green", schedule)
    sleep(30)
    if count == max_count:
        schedule = GetBinDay()
        count = 0