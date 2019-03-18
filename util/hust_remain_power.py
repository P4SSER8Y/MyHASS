#!/usr/bin/env python3
import logging
logging.debug("=== INITIALIZING ===")

import yaml
import os
logging.info("parse secrets.yaml")
script_file = os.path.realpath(__file__)
yaml_file = os.path.join(os.path.dirname(script_file), '../secrets.yaml')
with open(yaml_file, 'r') as f:
    configure_data = yaml.load(f)

MQTT_AUTH = {'username': configure_data['mqtt_username'], 'password': configure_data['mqtt_password']}

url = 'http://202.114.18.218/main.aspx'
data = {'__EVENTTARGET': '',
        '__EVENTARGUMENT': '',
        '__LASTFOCUS': '',
        '__VIEWSTATE': '/wEPDwULLTE4NDE5OTM2MDEPZBYCAgMPZBYIAgEPEA8WBh4NRGF0YVRleHRGaWVsZAUM5qW85qCL5Yy65Z+fHg5EYXRhVmFsdWVGaWVsZAUM5qW85qCL5Yy65Z+fHgtfIURhdGFCb3VuZGdkEBUGBuS4nOWMugnnlZnlrabnlJ8G6KW/5Yy6BumfteiLkQbntKvoj5gLLeivt+mAieaLqS0VBgbkuJzljLoJ55WZ5a2m55SfBuilv+WMugbpn7Xoi5EG57Sr6I+YAi0xFCsDBmdnZ2dnZxYBZmQCBQ8QDxYGHwAFBualvOWPtx8BBQbmpbzlj7cfAmdkEBUUB+S4nDHoiI0H5LicMuiIjQfkuJwz6IiNB+S4nDToiI0H5LicNeiIjQfkuJw26IiNB+S4nDfoiI0H5LicOOiIjQzpmYTkuK3kuLvmpbwH5pWZN+iIjQfmlZk46IiNB+WNlzHoiI0H5Y2XMuiIjQfljZcz6IiNC+aygeiLkTEw6IiNC+aygeiLkTEx6IiNC+aygeiLkTEy6IiNC+aygeiLkTEz6IiNCuaygeiLkTnoiI0LLeivt+mAieaLqS0VFAfkuJwx6IiNB+S4nDLoiI0H5LicM+iIjQfkuJw06IiNB+S4nDXoiI0H5LicNuiIjQfkuJw36IiNB+S4nDjoiI0M6ZmE5Lit5Li75qW8B+aVmTfoiI0H5pWZOOiIjQfljZcx6IiNB+WNlzLoiI0H5Y2XM+iIjQvmsoHoi5ExMOiIjQvmsoHoi5ExMeiIjQvmsoHoi5ExMuiIjQvmsoHoi5ExM+iIjQrmsoHoi5E56IiNAi0xFCsDFGdnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZGQCEw88KwANAGQCFQ88KwANAGQYAwUeX19Db250cm9sc1JlcXVpcmVQb3N0QmFja0tleV9fFgIFDEltYWdlQnV0dG9uMQUMSW1hZ2VCdXR0b24yBQlHcmlkVmlldzEPZ2QFCUdyaWRWaWV3Mg9nZLHWUKnsT4U5B01iOoW0cLHinyY9',
        '__EVENTVALIDATION': '/wEWIgLS+p/fDgLorceeCQLc1sToBgL+zpWoBQK50MfoBgKj5aPiDQLtuMzrDQLrwqHzBQKX+9a3BALahLK2BQLahLa2BQLahIq2BQLahI62BQLahIK2BQLahIa2BQLahJq2BQLahN61BQL4w577DwKH0Zq2BQKH0d61BQKVrbK2BQKVrba2BQKVrYq2BQKY14SVBQKY1+jwDAKY1/zbCwKY18CmAwLr76OiDwKUlLDaCAL61dqrBgLSwpnTCALSwtXkAgLs0fbZDALs0Yq1BYiiagV69FGjEwsWCICpCTfoshaE',
        'programId': configure_data['hust_district'],
        'txtyq': configure_data['hust_building'],
        'Txtroom': configure_data['hust_room'],
        'ImageButton1.x': '42',
        'ImageButton1.y': '14',
        'TextBox2': '',
        'TextBox3': '',
       }

import requests
import paho.mqtt.publish as publish
from bs4 import BeautifulSoup
from datetime import datetime
import json

def fetch():
    ret_date = []
    ret_remain = []

    logging.info("request information")
    req = requests.post(url=url, data=data)

    logging.info("parse webpage")
    soup = BeautifulSoup(req.content, features="html.parser")
    table = soup.select_one('#GridView2')
    for item in table.select('tr'):
        if item.td:
            columns = item.find_all('td')
            remain = float(columns[0].get_text())
            dt = datetime.strptime(columns[1].get_text(), r"%Y-%m-%d %H:%M:%S")
            ret_date.append(dt)
            ret_remain.append(remain)
    return ret_date, ret_remain

def publish_electricity_fee(date, yesterday_usage, remain):
    msg = json.dumps({'date': date.isoformat(), 'yesterday_usage': '{:0.1f}'.format(yesterday_usage), 'remain': '{:0.1f}'.format(remain)})
    publish.single('hass/dorm/power',
        hostname=configure_data['mqtt_broker'],
        port=configure_data['mqtt_port'],
        auth=MQTT_AUTH, payload=msg, retain=1)
    

if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    (date, remain) = fetch()
    publish_electricity_fee(date[0], remain[1] - remain[0], remain[0])

