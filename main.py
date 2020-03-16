from flask import Flask, render_template

import sqlite3

app = Flask(__name__)

conn = sqlite3.connect('tiki.db')
cur = conn.cursor()

def get_number_total():
    query = """
        SELECT MAX(products.id)
        FROM products
        """
    nototal = cur.execute(query)
    return nototal

def get_number_categories():
    query = """
        SELECT MAX(categories.id)
        FROM categories
        """
    nocat = cur.execute(query)
    return nocat

def get_number_brand():
    query = """
        SELECT COUNT(DISTINCT brand)
        FROM products
        """
    nobrand = cur.execute(query)
    return nobrand

def get_average_price():
    query = """
        SELECT AVERAGE(price)
        FROM products
        """
    avgprice = cur.execute(query)
    return avgprice

def get_top5_brands():
    query = """
        SELECT brand, COUNT(name) as count
        FROM products
        GROUP BY brand
        ORDER BY count DES
        LIMIT 5
        """
    top5brand = cur.execute(query)
    return top5brand

def get_top5_cats():
    query = """
        SELECT categories.name, COUNT(products.name) as count
        FROM products
        INNER JOINT categories ON categories.id = products.cat_id
        GROUP BY cat_id
        ORDER BY count DES
        LIMIT 5
        """
    top5cat = cur.execute(query)
    return top5cat

def get_top5_highest():
    query = """
        SELECT name, price , img_link, url
        FROM products
        ORDER BY price DES
        LIMIT 5
        """
    top5cat = cur.execute(query)
    return top5cat

@app.route('/')
def index():
    data = {}
    data['nototal'] = get_number_total
    data['nocat'] = get_number_categories
    data['nobrand'] = get_number_brand
    data['avgprice'] = get_average_price
    data['top5brands'] = get_top5_brands
    data['top5cats'] = get_top5_cats
    data['top5highest'] = get_top5_highest
    return render_template('index.html',data=data)

if __name__ == '__main__':
  app.run(host='127.0.0.1', port=8000, debug=True)
 