from bs4 import BeautifulSoup
import requests
import sqlite3
from collections import deque
import re
import functools

conn = sqlite3.connect('tiki.db')
cur = conn.cursor()

def debug(func):
    """Print the function signature and return value"""
    @functools.wraps(func)
    def wrapper_debug(*args, **kwargs):
        args_repr = [repr(a) for a in args]                      # 1
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]  # 2
        signature = ", ".join(args_repr + kwargs_repr)           # 3
        print(f"Calling {func.__name__}({signature})")
        value = func(*args, **kwargs)
        print(f"{func.__name__!r} returned {value!r}")           # 4
        return value
    return wrapper_debug 

def create_product_table():
    query ="""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(255),
        url TEXT,
        price INT,
        brand TEXT,
        productid INT,
        cat_id INT,
        img_link TEXT,
        create_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """

    try:
        cur.execute(query)
    except Exception as err:
        print('ERROR BY CREATE TABLE', err)

class Product:
    def __init__(self, pro_id, name, url, price, brand, productid, cat_id,img_link):
        self.pro_id = pro_id
        self.name = name
        self.url = url
        self.price = price
        self.brand = brand
        self.productid = productid
        self.cat_id = cat_id
        self.img_link = img_link

    def __repr__(self):
        return "ID: {}, Name: {}, URL: {}, Price: {}, Brand: {}, PRODUCT-ID: {}, Category: {}, Image Link: {}".format(self.pro_id, self.name, self.url, self.price, self.brand, self.productid, self.cat_id, self.img_link)

    def save_into_db(self):
        query = """
            INSERT INTO products (name, url, price, brand, productid, cat_id, img_link)
            VALUES (?, ?, ?, ?, ?, ? , ?);
        """
        val = (self.name, self.url, self.price, self.brand, self.productid, self.cat_id, self.img_link)
        try:
            cur.execute(query, val)
            conn.commit()
            self.cat_id = cur.lastrowid
        except Exception as err:
            print('ERROR BY INSERT:', err)

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
            self.cat_id = cur.lastrowid
            conn.commit()
        except Exception as err:
            print('ERROR BY INSERT:', err)

def get_url(url):
    try:
        response = requests.get(url).text
        response = BeautifulSoup(response, 'html.parser')
        return response
    except Exception as err:
            print('ERROR BY REQUEST:', err)

def get_categories():
    category_list = []
    query = """
            SELECT *
            FROM categories
        """
    try:
        categories_data = cur.execute(query)
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

def crawl_product(soup,category,save_db=False):
    product_list = soup.findAll('div',{'class':'product-item'})
    for product in product_list:
        _url = product.a['href']
        _name = product['data-title']
        _productid = product['data-id']
        _brand = product['data-brand']
        _price = product['data-price']
        _cat_id = category.cat_id
        _img_link = product.a.div.span.img['src']
        new_product = Product(None,_name,_url,_price,_brand,_productid,_cat_id,_img_link)
        print(new_product)
        if save_db==True:
            new_product.save_into_db()

def crawl_all_product(categories_list, save_db=False):
    #parent_list = get_parent_list()
    parent_list = []
    for category in categories_list:
        if (category.cat_id,) not in parent_list:
            soup = get_url(category.url)
            crawl_product(soup,category,save_db)
            try:
                max_page = int(soup.find('div',{'class':'list-pager'}).text.split()[-1])
                if max_page >2:
                    for i in range(2,max_page+1):
                        soup = get_url(f"{category.url}&page={i}")
                        crawl_product(soup,category,save_db)
            except: pass

create_product_table()
#cur.execute('DROP TABLE products;')
#conn.commit()

crawl_all_product(get_categories(),save_db=True)