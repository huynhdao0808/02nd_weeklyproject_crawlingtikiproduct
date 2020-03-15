from bs4 import BeautifulSoup
import requests
import sqlite3
from collections import deque
import re

from createdatabase import get_url, Category

conn = sqlite3.connect('tiki.db')
cur = conn.cursor()

def create_product_table():
    query ="""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(255),
        url TEXT,
        price INT,
        brand TEXT,
        sku BIGINT,
        category_id INT,
        create_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """

    try:
        cur.execute(query)
    except Exception as err:
        print('ERROR BY CREATE TABLE', err)

class Product:
    def __init__(self, pro_id, name, url, price, brand, sku, cat_id):
        self.pro_id = pro_id
        self.name = name
        self.url = url
        self.price = price
        self.brand = brand
        self.sku = sku
        self.cat_id = cat_id

    def __repr__(self):
        return "ID: {}, Name: {}, URL: {}, Price: {}, Brand: {}, SKU: {}, Category: {}".format(self.pro_id, self.name, self.url, self.price, self.brand, self.sku, self.cat_id)

    def save_into_db(self):
        query = """
            INSERT INTO products (name, url, price, brand, sku, cat_id)
            VALUES (?, ?, ?, ?, ?, ?);
        """
        val = (self.name, self.url, self.price, self.brand, self.sku, self.cat_id)
        try:
            cur.execute(query, val)
            conn.commit()
            self.cat_id = cur.lastrowid
        except Exception as err:
            print('ERROR BY INSERT:', err)

def get_categories(limit, offset):
    category_list = []
    query = """
            SELECT *
            FROM categories
            LIMIT ? OFFSET ?
        """
    val = (limit, offset)
    try:
        categories_data = cur.execute(query, val)
    except Exception as err:
        print('ERROR BY SELECT:', err)
    for category in categories_data:
        _category_id = category[0]
        _category_name = category[1]
        _category_url = category[2]
        _category_parent_id = category[3]
        _category = Category(_category_id,_category_name,_category_url,_category_parent_id)
        print(_category)
        category_list.append(_category)
    return category_list

def get_parent_list():
    query = """
            SELECT DISTINCT parent_id
            FROM categories
        """
    try:
        return cur.execute(query)
    except Exception as err:
        print('ERROR BY SELECT DISTINCT:', err)

def crawl_product(categories_list, save_db=False):
    #parent_list = get_parent_list()
    parent_list = []
    for category in categories_list:
        if category.cat_id not in parent_list:
            soup = get_url(category.url)
            product_list = soup.findAll('div',{'class':"product-item    "})
            for product in product_list:
                _url = product.a['href']
                soup = get_url(_url)
                _name = soup.find('h1', {'class':'item-name'}).text
                _sku = int(soup.find('div',{'class':"item-brand item-sku"}).p.text.strip())
                _brand = soup.find('div',{'class':"item-brand"}).p.text
                _price_coarse = soup.find('span',{'id':"span-price"}).text
                _regex = '[\d+\.]+'
                _price = int(re.sub('\.','',re.findall(_regex,_price_coarse)[0]))
                _cat_id = category.cat_id
                new_product = Product(None,_name,_url,_price,_brand,_sku,_cat_id)
                print(new_product)
                if save_db==True:
                    new_product.save_into_db()

create_product_table()
crawl_product([Category(1,'abc','https://tiki.vn/may-tinh-bang/c1794?src=c.1789.hamburger_menu_fly_out_banner&_lc=Vk4wMzkwMDEwMDQ%3D',2)])
