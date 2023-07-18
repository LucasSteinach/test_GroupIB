# cell 1
import pandas as pd
import matplotlib.pyplot as plt
from pprint import pprint
from sklearn.cluster import SpectralClustering
from sklearn.preprocessing import OneHotEncoder
import networkx as nx
from pandas.plotting import scatter_matrix

# cell 2
fraudulent_device = '91b12379-8098-457f-a2ad-a94d767797c2'
fraudulent_account = '0007f265568f1abc1da791e852877df2047b3af9'
data = pd.read_csv('output.csv')
print(data.columns)


# cell 2.5
def get_node(row: pd.Series, fields_list: list):   # -> tuple:
    result = tuple(row[fields_list].to_list())
    return result


fields = ['identity', 'device_id', 'device_fingerprint']
# print(get_node(data.iloc[2], fields))

# cell 3
# features = data[['lon', 'lat']]
#
# encoded_features = pd.get_dummies(features)
#
#
# spectral = SpectralClustering(n_clusters=3, affinity='nearest_neighbors')
# labels = spectral.fit_predict(encoded_features)
# print(set(labels))

# cell 4
data['color'] = ['red' if list(dict(row).values()).count(fraudulent_account) > 0
                 or list(dict(row).values()).count(fraudulent_device) > 0
                 else 'blue'
                 for (index, row) in data.iterrows()]

data = data.sort_values(by='color')
# data.plot(kind='scatter', x='lon', y='lat', c=data['color'])
# plt.title('Cluster Visualization')
# plt.show()

# cell 5
pprint(set(data['device_id'][data['color'] == 'red']))
associated_devices = list(data['device_id'][data['color'] == 'red'])
print('devices amount =', len(set(data['device_id'][data['color'] == 'red'])))

pprint(set(data['identity'][data['color'] == 'red']))
associated_accounts = list(data['identity'][(data['color'] == 'red') & (data['identity'] != '-')])
# print('accounts amount =', len(set(data['identity'][data['color'] == 'red'])))
# print('===========================================================')
# print('unique accounts')
# pprint(set(data['identity'][(data['device_id'].isin(associated_devices)) & (data['identity'] != '-')]))
# print('===========================================================')
# print('unique devices')
# pprint(data[['device_id']][(data['identity'].isin(associated_accounts)) & (data['proxy'] is True)])
# print('===========================================================')
# print('unique fingerprints')
# pprint(set(data['device_fingerprint'][(data['device_id'].isin(associated_devices))
#                                       & (data['identity'] != '-')
#                                       & (data['identity'].isin(associated_accounts))]))
# associated_fingerprints = list(set(data['device_fingerprint'][(data['device_id'].isin(associated_devices))
#                                                               & (data['identity'] != '-')
#                                                               & (data['identity'].isin(associated_accounts))]))
# print('===========================================================')
# print('accounts with associated fingerprints')
# pprint(set(data['identity'][(data['device_fingerprint'].isin(associated_fingerprints))]))


# data.plot(kind='scatter', x='lon', y='lat', c=data['color'])
# plt.title('Cluster Visualization')
# plt.show()

# cell 6
G = nx.Graph()
#
G.add_nodes_from(list(data.apply(lambda x: get_node(x, fields), axis=1, )))
#
nx.draw(G, with_labels=False, node_color=list(data['color']))
# nx.write_graphml(nx.MultiGraph(), 'graph.graphml')
#

plt.show()