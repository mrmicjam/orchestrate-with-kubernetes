from flask import Flask, render_template
from google.cloud import datastore
import datetime


datastore_client = datastore.Client()


app = Flask(__name__)

@app.route('/')
def root():
    products = datastore_client.query(kind="deal_product").fetch(limit=5)
    return render_template('index.html', products=products, num_products=5)

@app.route('/product_test')
def product_test():
	start = datetime.datetime.now()

	products = datastore_client.query(kind="social_socialagg").fetch(limit=100)
	display_products = []
	for product in products:
		display_products.append(product)
	delta_load = datetime.datetime.now() - start

	start = datetime.datetime.now()
	batch = datastore_client.batch()
	with batch:
		for product in display_products:
			product.update({'rel_6_34_backup_pricing_unit': 'ci'})
			batch.put(product)
	delta_save = datetime.datetime.now() - start	

	return render_template('load_save_delta.html', products=display_products, 
		delta_load=delta_load.microseconds, num_products=len(display_products),
		delta_save=delta_save.microseconds
		)

@app.route('/product_test_loop_put')
def product_test_loop_put():
	start = datetime.datetime.now()
	products = datastore_client.query(kind="social_socialagg").fetch(limit=100)
	display_products = []
	delta_each = []
	for product in products:
		start_each = datetime.datetime.now()
		product.update({'rel_6_34_backup_pricing_unit': 'ci'})
		datastore_client.put(product)
		delta = datetime.datetime.now() - start_each
		display_products.append([product, delta.microseconds])
	delta = datetime.datetime.now() - start
	return render_template('save_each.html', products=display_products, 
		microseconds=delta.microseconds, num_products=len(display_products),
		project=datastore_client.project
		)


if __name__ == "__main__":
  app.run(host='0.0.0.0', port=8080)

