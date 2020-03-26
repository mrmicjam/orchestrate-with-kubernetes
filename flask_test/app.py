from flask import Flask, render_template
from google.cloud import datastore
import datetime
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from models import Distributor, Zip, Product, RetailProduct
from session import db_session


datastore_client = datastore.Client()


app = Flask(__name__)
app.secret_key = 'yadsafkkd'
app.config['SESSION_TYPE'] = 'filesystem'

admin = Admin(app, name='simple123', template_mode='bootstrap3', url='/api/admin')



class ZipView(ModelView):
	column_searchable_list = ['zip_code']
	column_filters = ['distributor']
	can_create = False
	can_delete = False


class DistributorView(ModelView):
	form_excluded_columns = ['zips', ]

admin.add_view(DistributorView(Distributor, db_session))
admin.add_view(ModelView(Product, db_session))
admin.add_view(ModelView(RetailProduct, db_session))
admin.add_view(ZipView(Zip, db_session))


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
		delta_load=delta_load.total_seconds(), num_products=len(display_products),
		delta_save=delta_save.total_seconds()
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
		display_products.append([product, delta.total_seconds()])
	delta = datetime.datetime.now() - start
	return render_template('save_each.html', products=disaplay_products,
		microseconds=delta.total_seconds(), num_products=len(display_products),
		project=datastore_client.project
		)


if __name__ == "__main__":
  app.run(host='0.0.0.0', port=8081)

