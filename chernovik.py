import pandas as pd
from pprint import pprint
import networkx as nx
from pyvis.network import Network

fraudulent_device = '91b12379-8098-457f-a2ad-a94d767797c2'
fraudulent_account = '0007f265568f1abc1da791e852877df2047b3af9'
data = pd.read_csv('output.csv')
print(data.columns)


def get_tuple_from_row(row: pd.Series, fields_list: list = None):   # -> tuple:
    if fields_list is None:
        return tuple(row.tolist())
    else:
        return tuple(row[fields_list].to_list())

# print(get_tuple_from_row(data.iloc[1]))


def prepare_nodes_parameters(df:pd.DataFrame, fields: list = None) -> dict:
    result = {
        'n_id': [],
        'value': [],
        'title': [],
        'label': [],
        'color': [],
    }
    for index, row in df.iterrows():
        result['n_id'].append(index)
        if fields is None:
            result['value'].append(get_tuple_from_row(row))
        else:
            result['value'].append(get_tuple_from_row(row, fields))
        result['title'].append('')
        result['label'].append(index)
        result['color'].append('gray')
    return result


def calc_edge_width_and_title(row1: dict, row2: dict, fields: list = list(data.columns)) -> (int, str):
    """
    Compares each column of both nodes data and calculates how many connections they have.
    If there are connections in device_id, device_fingerprint, identitywill width grow by 10
    :return: integer value of edge width and title for edge.
    Title contains names of connection fields.
    """
    title = ['These fields are equal:']
    width = 0
    for field in fields:
        if row1[field] == row2[field]:
            title.append(field)
            width += 1
            if field in ['device_id', 'identity', 'device_fingerprint']:
                width += 9
    return width, '\n'.join(title)


def one_node_to_many_list(node1: dict, nodes_dict: dict) -> list:
    result = []
    for i in range(len(nodes_dict['n_id'])):
        width, title = calc_edge_width_and_title(node1[list(node1.keys())[0]], nodes_dict['values'][i])
        if width != 0:
            result.append((list(node1.keys())[0], nodes_dict['n_id'][i], width, title))
    return result


print(calc_edge_width_and_title(data.iloc[1], data.iloc[2]))

# net.add_edge(0, 1, width=.87, title='')

# print(prepare_nodes_parameters(data.iloc[:10]))

# 1. searching for device fingerprints associated with compromised records
print('=============================')
associated_fingerprints = list(set(data['device_fingerprint'][
    ((data['device_id'] == fraudulent_device)
    | (data['identity'] == fraudulent_account))
    & (data['device_fingerprint'] != 'No data')
].values))
print(associated_fingerprints)

# 2. searching for devices associated with compromised records and fingerprints
# print('=============================')
associated_devices = list(set(data['device_id'][
    (data['device_id'] == fraudulent_device)
    | (data['identity'] == fraudulent_account)
    | (data['device_fingerprint'].isin(associated_fingerprints))
].values))
# print(associated_devices)

# 3. searching for accounts associated to compromised records and found devices
# print('=============================')
associated_accounts = list(set(data['identity'][
    (data['device_id'].isin(associated_devices))
    | (data['identity'] == fraudulent_account)
    | (data['device_fingerprint'].isin(associated_fingerprints))
].values))
# print(associated_accounts)


# print('=============================')
associated_os = list(set(data['os'][
    (data['device_id'].isin(associated_devices)) |
    (data['identity'].isin(associated_accounts)) |
    (data['device_fingerprint'].isin(associated_fingerprints))
].values))
# print(set(associated_os))

# parameters_of_screen = {
#     'os': [],
#     'browser': [],
#     'screen': [],
# }
#
# for index, row in data[data['device_fingerprint'].isin(associated_fingerprints)].iterrows():
#     parameters_of_screen['os'].append(row['os'])
#     parameters_of_screen['browser'].append(row['browser'])
#     parameters_of_screen['screen'].append(row['screen'])
#
# for key in parameters_of_screen.keys():
#     parameters_of_screen[key] = list(set(parameters_of_screen[key]))
#
# pprint(parameters_of_screen)