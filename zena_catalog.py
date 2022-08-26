import imp
from os import access
import streamlit
import pandas
import requests
import snowflake.connector
from common import catalog


def connect():
    lcnx = snowflake.connector.connect(**streamlit.secrets["snowflake1"])
    return (lcnx, lcnx.cursor())

def out_text(iS):
    return streamlit.caption('<font size="+3">' + iS + '</font>', unsafe_allow_html=True)

my_cnx = None
my_cur = None

cat_query = 'select color_or_style, price, direct_url, size_list, upsell_product_desc from catalog_for_website'

if not catalog:
    if not my_cnx:
        my_cnx, my_cur = connect()
    assert my_cnx, 'Connected to Snowflake'
    my_cur.execute(cat_query)
    catalog = my_cur.fetchall()
assert catalog, 'Data has been fetched'

colors_styles = [t[0] for t in catalog]
streamlit.header("Zena's catalog")
item_selected = streamlit.selectbox('Select an item.', list(colors_styles))
if item_selected:
    item = catalog[colors_styles.index(item_selected)]
    streamlit.image(item[2], 'Our warm, comfortable, ' + item[0], 400)
    out_text('Price: $' + str(item[1]))
    out_text(str(item[3]))
    out_text(str(item[4]))
