from pymongo import MongoClient
import streamlit as st
import matplotlib.pyplot as plt
from datetime import date, timedelta


def mongo_connect(idb, icoll):
    creds = st.secrets["mongo"]
    cluster = MongoClient('mongodb+srv://' +
        creds['user'] + ':' + creds['password'] + 
        '@cluster0.tizsziq.mongodb.net/?retryWrites=true&w=majority')
    db = cluster[idb]
    coll = db[icoll]
    return coll


def get_by_hour():
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
    return rs


def get_by_days():
    rs = coll.aggregate([
        {
            '$match': {
                '$text':{'$search': '"Увага! Повітряна тривога!"'}
            }
        },
        {
            '$group': {
                '_id': {
                    'year': {'$year': '$date'},
                    'month': {'$month': '$date'},
                    'day': {'$dayOfMonth': '$date'}
                },
                'cnt': {'$sum': 1}
            }
        },
        {
            '$sort': {'_id': 1}
        }
    ])
    return rs


def get_by_days_running_total():
    rs = coll.aggregate([
        {
            '$match': {
                '$text':{'$search': '"Увага! Повітряна тривога!"'}
            }
        },
        {
            '$group': {
                '_id': {
                    'year': {'$year': '$date'},
                    'month': {'$month': '$date'},
                    'day': {'$dayOfMonth': '$date'}
                    },
                'cnt': {'$sum': 1}
            }
        },
        {
            '$setWindowFields': {
                'sortBy': {'_id': 1},
                'output': {
                    'cumSum': {
                        '$sum': '$cnt',
                        'window': {'documents': ["unbounded", "current"]}
                    }
                }
            }
        },
        {
            '$sort': {'_id': 1}
        }
    ])
    return rs


def get_by_day_of_week():
    rs = coll.aggregate([
        {
            '$match': {
                '$text':{'$search': '"Увага! Повітряна тривога!"'}
            }
        },
        {
            '$group': {
                '_id': {
                    'dw': {
                        '$dayOfWeek': '$date'
                    }
                },
                'cnt': {'$sum': 1}
            }
        },
        {
            '$sort': {'_id.dw': 1}
        }
    ])
    return rs


(BY_H, BY_DS, BY_DSRT, BY_WD) = ('By hour', 'By days', 'By days (running total)', 'By day of week')

coll = mongo_connect('tst', 'tst')

fig, ax = plt.subplots()

st.header('Lviv alarms statistics')
stype = st.radio('Stats type', (BY_H, BY_DS, BY_DSRT, BY_WD), horizontal=True)
if stype == BY_H:
    rs = get_by_hour()
    dfs = [[e['_id']['hr'], e['cnt']] for e in rs]
    hours = [e[0] for e in dfs]
    counts = [e[1] for e in dfs]
    ax.bar(hours, counts)
    plt.xticks([e for e in range(1, 24, 2)])
    plt.yticks([e for e in range(0, max(counts)+4, 5)])
    plt.margins(0.01, 0.1)
elif stype in {BY_DS, BY_DSRT}:
    if stype == BY_DS:
        rs = get_by_days()
        cntField = 'cnt'
        ystep = 2
    else:
        rs = get_by_days_running_total()
        cntField = 'cumSum'
        ystep = 10
    dfs = [[date(e['_id']['year'], e['_id']['month'], e['_id']['day']),
        e[cntField]] for e in rs]
    days = [e[0] for e in dfs]
    counts = [e[1] for e in dfs]
    if stype == BY_DS:
        ax.plot(days, counts)
    else:
        ax.fill_between(days, counts)
    plt.xticks([min(days) + timedelta(days=e) 
        for e in range(0, (max(days) - min(days)).days, 10)],
        rotation=90)
    plt.yticks([e for e in range(0, max(counts)+ystep-1, ystep)])
    plt.margins(0.01)
elif stype == BY_WD:
    rs = get_by_day_of_week()
    dfs = [[e['_id']['dw'], e['cnt']] for e in rs]
    wdays = ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa']
    counts = [e[1] for e in dfs]
    ax.bar(wdays, counts)
    plt.yticks([e for e in range(0, max(counts)+4, 5)])
    plt.margins(0.01, 0.1)

st.pyplot(fig)
