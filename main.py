"""
Input data: flat table in test.xlsx
Output data: output.csv; contains data from test.xlsx,
extended with information about IP (source: http://ip-api.com)
"""

import pandas as pd
import requests
import time

initial_data = pd.read_excel('test.xlsx')
all_ips = list(initial_data['ips'])
output_name = 'output.csv'


def get_ip_list(raw_list: list) -> list:
    """
    1. splits ips records by ','
    2. creates a list of unique ips from initial_data['ips']
    :param raw_list: is a list from column 'ips' in test.xlsx
    :return: list of unique ips
    """
    result = list()
    for unit in raw_list:
        if unit.find(',') == -1:
            result.append(unit)
        else:
            result += unit.split(',')
    return list(set(result))


def connect_api(ips: list) -> dict:
    """
    returns dict with information about IP {'ip': dict of parameters}
    :param ips: list of unique ips
    :return: dict of ips, structure: {ip: {values: data} }
    """
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


def create_flat_table(raw_table: pd.DataFrame) -> pd.DataFrame:
    """
    adds new rows with single ip, removes rows with merged ips (example: '192.168.0.1,192.168.0.2')
    :param raw_table: pd.DataFrame with merged ips
    :return: pd.DataFrame, each row contains single ip
    """
    row_to_remove = []
    result = pd.DataFrame(dict(raw_table))
    for index, row in raw_table.iterrows():
        if row['ips'].find(',') != -1:
            row_to_remove.append(index)
            for ip in row['ips'].split(','):
                result.loc[len(result) + 1] = pd.Series(list(row)[:-1] + [ip], index=raw_table.columns)
    result = result.drop(row_to_remove).reset_index(drop=True)
    return result


def get_failed_ip_list(ips: dict) -> list:
    """
    returns list of ips without "success" status (errors during connect_api-function)
    :param ips: dict, result of connect_api-function
    :return: list of ip which status is not "success"
    """
    return [key for key, value in ips.items() if value.get('status') != 'success']


def concate_data(ips: str, fields: list, source: dict) -> list:
    """
    :param ips: single value of column 'ips' in initial dataframe
    :param fields: fields to concate
    :param source: dict, result of connect_api
    :return: list(row) of data to concate with initial_data, set '' for cell if there is no value of some column
    """
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

initial_data = create_flat_table(initial_data)

data_to_concate = connect_api(api_data['ips'])

# name of columns to concate (fields without 'status', 'message', 'query')
concate_fields = list(api_data['fields'].keys())[2:-1]

# concating data to initial data
initial_data[concate_fields] = initial_data['ips'].apply(
    lambda x: pd.Series(concate_data(x, concate_fields, data_to_concate))
)

initial_data.to_csv(output_name, mode='w', index=False)
