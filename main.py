from flask import Flask, render_template

import sqlite3

app = Flask(__name__)

def get_number_total(cur):
    query = """
        SELECT MAX(products.id)
        FROM products
        """
    nototal = cur.execute(query)
    return nototal.fetchall()

def get_number_categories(cur):
    query = """
        SELECT MAX(categories.id)
        FROM categories
        """
    nocat = cur.execute(query)
    return nocat.fetchall()

def get_number_brand(cur):
    query = """
        SELECT COUNT(DISTINCT brand)
        FROM products
        """
    nobrand = cur.execute(query)
    return nobrand.fetchall()

def get_average_price(cur):
    query = """
        SELECT AVG(price)
        FROM products
        """
    avgprice = cur.execute(query)
    return int(avgprice.fetchall()[0][0])

def get_top5_brands(cur):
    query = """
        SELECT brand, COUNT(name) as count
        FROM products
        GROUP BY brand
        ORDER BY count DESC
        LIMIT 5 OFFSET 5
        """
    top5brand = cur.execute(query)
    return top5brand.fetchall()

def get_top5_cats(cur):
    query = """
        SELECT categories.name, COUNT(products.name) as count
        FROM products
        INNER JOIN categories ON categories.id = products.cat_id
        GROUP BY cat_id
        ORDER BY count DESC
        LIMIT 5
        """
    top5cat = cur.execute(query)
    return top5cat.fetchall()

def get_top5_highest(cur):
    query = """
        SELECT name, price , img_link, url
        FROM products
        ORDER BY price DESC
        LIMIT 5
        """
    top5cat = cur.execute(query)
    return top5cat.fetchall()

@app.route('/')
def index():
    data = {}
    conn = sqlite3.connect('tiki.db')
    cur = conn.cursor()
    data['nototal'] = get_number_total(cur)
    data['nocat'] = get_number_categories(cur)
    data['nobrand'] = get_number_brand(cur)
    data['avgprice'] = get_average_price(cur)
    data['top5brands'] = get_top5_brands(cur)
    data['top5cats'] = get_top5_cats(cur)
    data['top5highest'] = get_top5_highest(cur)
    return render_template('index.html',data=data)

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000, debug=True)
 