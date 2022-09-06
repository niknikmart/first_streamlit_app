from pickle import ADDITEMS
from pymongo import MongoClient, TEXT, ASCENDING
import json
from io import open
from datetime import datetime


def is_alarm(i_s):
    LS = ['Повітряна тривога!', 'Відбій повітряної тривоги!']
    for s in LS:
        if i_s.find(s):
            return True
    return False


def init_data():
    with open('result.json', encoding='utf-8') as f:
        s = ''.join(e.strip() for e in f.readlines())
    j = json.loads(s)['messages']
    # docs = (m for m in j if isinstance(m['text'], str) and is_alarm(m['text']))
    docs = []
    prev_t = None
    for m in j:
        if isinstance(m['text'], str) and is_alarm(m['text']):
            m['date'] = datetime.fromisoformat(m['date'])
            if not prev_t:
                prev_t = m['date']
                docs.append(m)
            else:
                if (m['date'] - prev_t).total_seconds() / 60 >= 5:
                    prev_t = m['date']
                    docs.append(m)
    coll.drop()
    coll.insert_many(docs)
    coll.create_index([('text', TEXT)])


cluster = MongoClient('mongodb+srv://mongo_user:iNXJUiI_gxUTu7edQDHh@cluster0.tizsziq.mongodb.net/?retryWrites=true&w=majority')
db = cluster['tst']
coll = db['tst']

init_data()
