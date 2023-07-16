# Input data: flat table in test.xlsx
# Output data: output.csv; contains data from test.xlsx, extended with information about IP
#                                                                      (source: http://ip-api.com)


import pandas as pd
from pprint import pprint
import requests
import csv
import json
import time


initial_data = pd.read_excel('test.xlsx')
all_ips = list(initial_data['ips'])
output_name = 'output.csv'


# 1. splits ips records by ','
# 2. creates a list of unique ips from initial_data['ips']
def get_ip_list(raw_list: list) -> list:
    result = list()
    for unit in raw_list:
        if unit.find(',') == -1:
            result.append(unit)
        else:
            result += unit.split(',')
    return list(set(result))


# returns dict with information about IP {'ip': dict of parameters}
def connect_api(ips: list) -> dict:
    result = dict()
    for ip in ips:
        response = requests.get(api_data['base_url'] + ip + "?fields=" + ','.join(api_data['fields'].keys()))

        # requests left
        request_limit = int(response.headers['X-Rl'])
        # time left until limit refresh
        request_timeout = int(response.headers['X-Ttl'])

        if request_limit > 0 and response.status_code == 200:
            data = response.text[:-1].split(',')
            # no message field if status == "success"
            data.insert(1, '')
            print(data)
            result.update(
                {
                    ip: dict(zip(api_data['fields'].keys(), data))
                }
            )
            # according to the website regulations, the maximum number of requests is 45/min
            time.sleep(1.5)
        else:
            data = ['error;' + str(response.status_code)] + ['' for i in range(len(api_data['fields']) - 3)] + [ip]
            result.update(
                {
                    ip: {'status': data[0]}
                }
            )
    return result


# returns list of ips without "success" status
def get_failed_ip_list(ips: dict) -> list:
    return [key for key, value in ips.items() if value.get('status') != 'success']


# for each ip returns list(row) of data to concate with initial_data
def concate_data(ips: str, fields: list, source: dict) -> list:
    result = list()
    if ips.find(',') == -1:
        for field in fields:
            result.append('' if (source.get(ips).get(field) is None) else source[ips].get(field))
    else:
        ips_list = ips.split(',')
        result = concate_data(ips_list[0], fields, source)
        for ip in ips_list[1:]:
            result = list(
                map(lambda x, y: str(x) if str(x).lower().find(str(y).lower()) != -1 else ';'.join([str(x), str(y)]),
                    result,
                    concate_data(ip, fields, source)
                    )
            )
    return result


# data to create request
api_data = {
    'base_url': 'http://ip-api.com/csv/',

    # { <field_name>: <description> }
    'fields': {
        'status':       "success or fail",
        'message':      """included only when status is fail.Can be
                        one of the following: private range, reserved range, invalid query""",
        'country':      "Country name",
        'countryCode':  "Two-letter country code ISO 3166-1 alpha-2",
        'region':       "Region/state short code (FIPS or ISO)",
        'regionName':   "Region/state",
        'city':         "city",
        'zip':          "ZIP code",
        'lat':          "latitude",
        'lon':          "longitude",
        'timezone':     "timezone",
        # 'isp':          "Internet Service Provider",
        # 'org':          "organisation name",
        # 'as':           """AS number and organisation, separated by space (RIR).
        #                 Empty for IP blocks not being announced in BGP tables.""",
        'mobile':       'Mobile (cellular) connection',
        'proxy':        'Proxy, VPN or Tor exit address',
        'hosting':      'Hosting, colocated or data center',
        'query':        "ip",
    },

    # list of ips, each unit is one ip (type: str)
    'ips': get_ip_list(list(initial_data['ips'])),
}


# УБЕРИ КОММЕНТАРИЙ
# data_to_concate = connect_api(api_data['ips'])

# УБЕРИ МЕНЕДЖЕР КОНТЕКСТА И ФАЙЛ
with open("ip_dict.json", 'r') as file:
    data_to_concate = pd.read_json(file).to_dict()

# name of columns to concate (fields without 'status', 'message', 'query')
concate_fields = list(api_data['fields'].keys())[2:-1]

# concating data to initial data
initial_data[concate_fields] = initial_data['ips'].apply(
    lambda x: pd.Series(concate_data(x, concate_fields, data_to_concate))
)


initial_data.to_csv(output_name, mode='w', index=False)
