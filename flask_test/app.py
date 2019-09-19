from flask import Flask, render_template
from google.cloud import datastore
import datetime


datastore_client = datastore.Client()


app = Flask(__name__)

@app.route('/')
def root():
    products = datastore_client.query(kind="deal_product").fetch(limit=5)
    return render_template('index.html', products=products, num_products=5)

@app.route('/product_test_loop_put')
def product_test_loop_put():
	start = datetime.datetime.now()
	products = datastore_client.query(kind="deal_product").fetch(limit=100)
	display_products = []
	for product in products:
		product.update({'rel_6_34_backup_pricing_unit': 'ci'})
		datastore_client.put(product)
		display_products.append(product)
	delta = datetime.datetime.now() - start
	return render_template('index.html', products=display_products, microseconds=delta.microseconds, num_products=len(display_products))


if __name__ == "__main__":
  app.run(host='0.0.0.0', port=8080)

