"""
Input: .csv, output file of main.py
Output: .csv contains compromised and associated with them records;
"""


import pandas as pd
import matplotlib.pyplot as plt


fraudulent_device = '91b12379-8098-457f-a2ad-a94d767797c2'
fraudulent_account = '0007f265568f1abc1da791e852877df2047b3af9'
data = pd.read_csv('output.csv')


associated_fingerprints = list(set(data['device_fingerprint'][
    ((data['device_id'] == fraudulent_device)
    | (data['identity'] == fraudulent_account))
    & (data['device_fingerprint'] != 'No data')
].values))


fraudulent_data = data[(data['device_id'] == fraudulent_device)
                       | (data['identity'] == fraudulent_account)
                       | (data['device_fingerprint'].isin(associated_fingerprints))
                       ].copy()
fraudulent_data.loc[:, 'color'] = 'red'


parameters_of_user_agent = {
    'os': [],
    'browser': [],
    'screen': [],
}
for index, row in data[data['device_fingerprint'].isin(associated_fingerprints)].iterrows():
    parameters_of_user_agent['os'].append(row['os'])
    parameters_of_user_agent['browser'].append(row['browser'])
    parameters_of_user_agent['screen'].append(row['screen'])
for key in parameters_of_user_agent.keys():
    parameters_of_user_agent[key] = list(set(parameters_of_user_agent[key]))


associated_data = data[
        (data['os'].isin(parameters_of_user_agent['os']))
        & (data['browser'].isin(parameters_of_user_agent['browser']))
        & (data['screen'].isin(parameters_of_user_agent['screen']))
        & (data['country'] == 'Russia')
        & (data['device_id'] != fraudulent_device)
        & (data['identity'] != fraudulent_account)
        & ~(data['device_fingerprint'].isin(associated_fingerprints))
    ].copy()
associated_data.loc[:, 'color'] = 'yellow'

result_data = pd.concat([fraudulent_data, associated_data])
result_data.to_csv('analysis_result.csv')

result_data = result_data.sort_values(by='color')
result_data.plot(kind='scatter', x='lon', y='lat', c=result_data['color'])

plt.show()
