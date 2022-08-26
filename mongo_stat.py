import imp
from itertools import count
from pymongo import MongoClient
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

creds = st.secrets["mongo"]
cluster = MongoClient('mongodb+srv://' +
    creds['user'] + ':' + creds['password'] + 
    '@cluster0.tizsziq.mongodb.net/?retryWrites=true&w=majority')
db = cluster['tst']
coll = db['tst']

rs = coll.aggregate([
    {
        '$match': {
            '$text':{'$search': '"Увага! Повітряна тривога!"'}
        }
    },
    {
        '$group': {
            '_id': {
                'hr': {
                    '$hour': '$date'
                }
            },
            'cnt': {'$sum': 1}
        }
    },
    {
        '$sort': {'_id.hr': 1}
    }
])
# dfs = [{'hr': e['_id']['hr'], 'cnt': e['cnt']} for e in rs]
dfs = [[e['_id']['hr'], e['cnt']] for e in rs]
# dfs = pd.DataFrame(dfs, columns=['Hour', 'Count'])
hours = [e[0] for e in dfs]
counts = [e[1] for e in dfs]

st.header('Lviv alarms statistics')
st.subheader('By hour')
# fig = dfs.plot(x = 'Hour', kind = 'area', figsize = (15, 7))
fig, ax = plt.subplots()
ax.bar(hours, counts)
plt.xticks([e for e in range(1, 24, 2)])
plt.yticks([e for e in range(0, max(counts)+4, 5)])
plt.margins(0.01, 0.1)
fig.tight_layout()
st.pyplot(fig)
