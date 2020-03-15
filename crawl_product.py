from bs4 import BeautifulSoup
import requests
import sqlite3
from collections import deque

conn = sqlite3.connect('tiki.db')
cur = conn.cursor()

def create_product_table():
    query ="""
    CREATE TABLE IF NOT EXISTS product (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(255),
        price INT,
        url TEXT,
        category_id INT,
        create_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """

    try:
        cur.execute(query)
    except Exception as err:
        print('ERROR BY CREATE TABLE', err)

class Category:
    def __init__(self, cat_id, name, url, parent_id):
        self.cat_id = cat_id
        self.name = name
        self.url = url
        self.parent_id = parent_id

    def __repr__(self):
        return "ID: {}, Name: {}, URL: {}, Parent_id: {}".format(self.cat_id, self.name, self.url, self.parent_id)

    def save_into_db(self):
        query = """
            INSERT INTO categories (name, url, parent_id)
            VALUES (?, ?, ?);
        """
        val = (self.name, self.url, self.parent_id)
        try:
            cur.execute(query, val)
            conn.commit()
            self.cat_id = cur.lastrowid
        except Exception as err:
            print('ERROR BY INSERT:', err)

def get_url(url):
    try:
        response = requests.get(url).text
        response = BeautifulSoup(response, 'html.parser')
        return response
    except Exception as err:
            print('ERROR BY REQUEST:', err)