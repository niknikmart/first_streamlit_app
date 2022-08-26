import streamlit
import pandas
import requests
import snowflake.connector

def get_fruityvice_normalized(i_fruit_choice):
    fruityvice_response = requests.get(f"https://www.fruityvice.com/api/fruit/{i_fruit_choice}")
    fruityvice_normalized = pandas.json_normalize(fruityvice_response.json())
    return fruityvice_normalized

def connect():
    lcnx = snowflake.connector.connect(**streamlit.secrets["snowflake"])
    return (lcnx, lcnx.cursor())


my_cnx = None
my_cur = None

streamlit.header('Breakfast Menu')
streamlit.text('🥣 Omega 3 & Blueberry Oatmeal')
streamlit.text('🥗 Kale, Spinach & Rocket Smoothie')
streamlit.text('🐔 Hard-Boiled Free-Range Egg')
streamlit.text('🥑🍞 Avocado Toast')

streamlit.header('🍌🥭 Build Your Own Fruit Smoothie 🥝🍇')
my_fruit_list = pandas.read_csv('https://uni-lab-files.s3.us-west-2.amazonaws.com/dabw/fruit_macros.txt')
my_fruit_list = my_fruit_list.set_index('Fruit')
fruits_selected = streamlit.multiselect('Pick some fruits: ', list(my_fruit_list.index))
if fruits_selected:
    fruits_to_show = my_fruit_list.loc[fruits_selected]
else:
    fruits_to_show = my_fruit_list
streamlit.dataframe(fruits_to_show)

streamlit.header('Fruityvice Fruit Advice')
fruit_choice = streamlit.text_input('What fruit would you like information about?','Kiwi')
if fruit_choice:
    streamlit.dataframe(get_fruityvice_normalized(fruit_choice))
else:
    streamlit.error('Enter a fruit name')

if streamlit.button('Get fruit load list'):
    if not my_cnx:
        my_cnx, my_cur = connect()
    my_cur.execute("select fruit_name from fruit_load_list")
    my_data_row = my_cur.fetchall()
    streamlit.text('The fruit load list contains:')
    streamlit.dataframe(my_data_row)

new_fruit = streamlit.text_input('What fruit would you like to add?')
if new_fruit:
    if streamlit.button(f'Add {new_fruit}'):
        if not my_cnx:
            my_cnx, my_cur = connect()
        sql_str = f"insert into fruit_load_list (fruit_name) values('{new_fruit}')"
        my_cur.execute(sql_str)
        streamlit.text(f'{new_fruit} successfully inserted')

