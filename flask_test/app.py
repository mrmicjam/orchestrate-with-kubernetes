from flask import Flask, render_template, jsonify, request, session, Blueprint, redirect, flash
from flask_restful import reqparse, abort, Api, Resource
from flask_login import login_required, logout_user, current_user, login_user, LoginManager
from google.cloud import datastore
import datetime
from flask_admin import Admin
from flask_sqlalchemy import SQLAlchemy

from flask_admin.contrib.sqla import ModelView
from flask_marshmallow import Marshmallow
from flask_session import Session
import stripe
import decimal
import os
from forms import LoginForm


from models import Distributor, Zip, Product, RetailProduct, Base, User, ProductCategory, Order, OrderItem
from session import db_session, engine
from sqlalchemy.pool import SingletonThreadPool

datastore_client = datastore.Client()


app = Flask(__name__)
app.secret_key = 'yadsafkkd'
app.config['SESSION_TYPE'] = 'sqlalchemy'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///orders.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

admin = Admin(app, name='simple123', template_mode='bootstrap3', url='/api/admin')
api = Api(app)
ma = Marshmallow(app)
sess = Session(app)
db = SQLAlchemy()
login_manager = LoginManager(app)

sess.app.session_interface.db.create_all()

Base.metadata.create_all(engine)


@login_manager.user_loader
def load_user(user_id):
	"""Check if user is logged-in on every page load."""
	if user_id is not None:
		return db_session.query(User).filter(User.id==user_id).first()
	return None


@login_manager.unauthorized_handler
def unauthorized():
	"""Redirect unauthorized users to Login page."""
	flash('You must be logged in to view that page.')
	return redirect('/api/login')


class BaseAdminView(ModelView):
	def is_accessible(self):
		return current_user.is_authenticated

	def inaccessible_callback(self, name, **kwargs):
		# redirect to login page if user doesn't have access
		return redirect('/api/login')


class ZipView(BaseAdminView):
	column_searchable_list = ['zip_code']
	column_filters = ['distributor']
	can_create = False
	can_delete = False


class DistributorView(BaseAdminView):
	form_excluded_columns = ['zips', ]


class ProductCategoryView(BaseAdminView):
	form_columns = ('name',)
	list_columns = ('name',)


class ProductView(BaseAdminView):
	form_columns = ('name', 'description', 'base_price', 'product_category', 'image')



admin.add_view(DistributorView(Distributor, db_session))
admin.add_view(ProductView(Product, db_session))
admin.add_view(ProductCategoryView(ProductCategory, db_session))
admin.add_view(BaseAdminView(RetailProduct, db_session))
admin.add_view(BaseAdminView(Order, db_session))
admin.add_view(BaseAdminView(OrderItem, db_session))
admin.add_view(ZipView(Zip, db_session))

parser = reqparse.RequestParser()
parser.add_argument('reg')


@app.route('/api/login', methods=['GET', 'POST'])
def login():
    """
    User login page.

    GET: Serve Log-in page.
    POST: If form is valid and new user creation succeeds, redirect user to the logged-in homepage.
    """
    if current_user.is_authenticated:
        return redirect('/api/admin')  # Bypass if user is logged in

    login_form = LoginForm()
    if request.method == 'POST':
        if login_form.validate_on_submit():
            email = login_form.data.get('email')
            password = login_form.data.get('password')
            user = db_session.query(User).filter(User.email==email).first()  # Validate Login Attempt
            if user and user.check_password(password=password):
                login_user(user)
                next_page = request.args.get('next')
                return redirect(next_page or '/api/admin')
        flash('Invalid username/password combination')
        return redirect('/api/login')

    return render_template('login.html',
                           form=login_form,
                           title='Log in.',
                           template='login-page',
                           body="Log in with your User account.")

class Register(Resource):
	def post(self):
		zipcode = request.json['reg']['zipcode']
		zip = db_session.query(Zip).filter(Zip.zip_code==zipcode).first()
		if not zip:
			return {}, 404
		session["user"] = request.json['reg']
		resp = {'distributor': zip.distributor_id}
		return resp, 201

api.add_resource(Register, '/api/register')


class CartItemSchema(ma.Schema):
	class Meta:
		fields = ("name", "price", "qty", "total")


cart_item_schema = CartItemSchema()
cart_items_schema = CartItemSchema(many=True)

class Cart(Resource):
	def post(self):
		product_id = request.json.get('product_id')
		qty = int(request.json.get('qty'))

		current_cart = session.get("cart", {})
		prod_cnt = current_cart.get(product_id, 0)
		current_cart[product_id] = prod_cnt + qty

		session["cart"] = current_cart

		resp = {'cart': product_id, 'count': len(session.get("cart", {}))}
		return resp, 201

	def get(self):
		current_cart = session.get("cart", {})
		products = db_session.query(RetailProduct).join(Product).filter(RetailProduct.id.in_(current_cart.keys()))
		id_to_prod = {}
		cart_items = []
		for product in products:
			id_to_prod[product.id] = product
		grand_total = 0
		for prod_id, qty in current_cart.items():
			retail_prod = id_to_prod[prod_id]
			price = (decimal.Decimal(retail_prod.price) / decimal.Decimal("100.0")).quantize(decimal.Decimal('0.00'))
			cart_items.append({
				"name": retail_prod.name,
				"price": '${}'.format(price),
				"qty": qty,
				"total": '${}'.format(price * qty)
			})
			grand_total += price * qty

		return {'cart': cart_items, 'user': session.get('user'),
				'count': len(current_cart), 'total': '${}'.format(grand_total)}


api.add_resource(Cart, '/api/cart')


class RetailProductSchema(ma.Schema):
	class Meta:
		fields = ("id", "distributor_id", "product_id", "price", "name", "description", "image", "display_price", "can_order")
product_schema = RetailProductSchema()
products_schema = RetailProductSchema(many=True)


class Products(Resource):
	def get(self, distributor_id):
		args = request.args

		products = db_session.query(RetailProduct).join(Product).filter(RetailProduct.distributor_id==distributor_id)

		if args.get("cat") and args.get("cat") != 'All':
			products = products.filter(Product.product_category == args.get("cat"))

		return {'products': products_schema.dump(products), 'user': session.get('user'),
				'count': len(session.get("cart", {}))}

api.add_resource(Products, '/api/products/<int:distributor_id>')


class ProductApi(Resource):
	def get(self, id):
		product = db_session.query(RetailProduct).filter(RetailProduct.id == id).first()
		if not product:
			return "Not found", 404
		return {'product': product_schema.dump(product), 'user': session.get('user'),
				'count': len(session.get("cart", {}))}

api.add_resource(ProductApi, '/api/product/<int:id>')

# @app.route('/api/register')
# def register():
# 	response_object = {'status': 'success'}
# 	if request.method == 'POST':
# 		post_data = request.get_json()
# 		response_object['message'] = 'registered!'
# 	else:
# 		response_object['message'] = "not registered"
# 	return jsonify(response_object)


@app.route('/api/charge', methods=['POST'])
def create_charge():
	post_data = request.get_json()
	amount = round(float(post_data.get('total').strip("$")) * 100)

	current_cart = session.get("cart", {})
	products = db_session.query(RetailProduct).join(Product).filter(RetailProduct.id.in_(current_cart.keys()))

	id_to_prod = {}
	distributor_id = None
	for product in products:
		if not distributor_id:
			distributor_id = product.distributor_id
		id_to_prod[product.id] = product
	grand_total = 0

	for prod_id, qty in current_cart.items():
		retail_prod = id_to_prod[prod_id]
		price = retail_prod.price
		grand_total += price * qty

	if grand_total != amount:
		return {"something went wrong"}, 400

	stripe.api_key = 'sk_test_ZIhkqTdUPX3vIAjGbvgKSBj900rIS9blAJ'
	charge = stripe.Charge.create(
		amount=amount,
		currency='usd',
		card=post_data.get('token'),
		description="order"
	)
	response_object = {
		'status': 'success',
		'charge': charge
	}
	user = session["user"]
	if charge.status == 'succeeded':
		order = Order(distributor_id=distributor_id, submitted_at=datetime.datetime.now(),
					  payed_at=datetime.datetime.now(),name=user['fllname'], email=user['email'], zip=user['zipcode'],
					  address='1 main', city='Spokane', state='WA', phone='44455566')

		db_session.add(order)
		db_session.commit()

		for prod_id, qty in current_cart.items():
			retail_prod = id_to_prod[prod_id]
			price = retail_prod.price
			oi = OrderItem(order_id=order.id, purchase_price=price, qty=qty, retail_product_id=prod_id)
			db_session.add(oi)
		db_session.commit()

		session["cart"] = {}

	return jsonify(response_object), 200


@app.route('/api/charge/<charge_id>')
def get_charge(charge_id):
    stripe.api_key = 'sk_test_ZIhkqTdUPX3vIAjGbvgKSBj900rIS9blAJ'
    response_object = {
        'status': 'success',
        'charge': stripe.Charge.retrieve(charge_id)
    }
    return jsonify(response_object), 200


@app.route('/')
def root():
    products = datastore_client.query(kind="deal_product").fetch(limit=5)
    return render_template('index.html', products=products, num_products=5)


# @app.route('/product_test')
# def product_test():
# 	start = datetime.datetime.now()
#
# 	products = datastore_client.query(kind="social_socialagg").fetch(limit=100)
# 	display_products = []
# 	for product in products:
# 		display_products.append(product)
# 	delta_load = datetime.datetime.now() - start
#
# 	start = datetime.datetime.now()
# 	batch = datastore_client.batch()
# 	with batch:
# 		for product in display_products:
# 			product.update({'rel_6_34_backup_pricing_unit': 'ci'})
# 			batch.put(product)
# 	delta_save = datetime.datetime.now() - start
#
# 	return render_template('load_save_delta.html', products=display_products,
# 		delta_load=delta_load.total_seconds(), num_products=len(display_products),
# 		delta_save=delta_save.total_seconds()
# 		)
#
# @app.route('/product_test_loop_put')
# def product_test_loop_put():
# 	start = datetime.datetime.now()
# 	products = datastore_client.query(kind="social_socialagg").fetch(limit=100)
# 	display_products = []
# 	delta_each = []
# 	for product in products:
# 		start_each = datetime.datetime.now()
# 		product.update({'rel_6_34_backup_pricing_unit': 'ci'})
# 		datastore_client.put(product)
# 		delta = datetime.datetime.now() - start_each
# 		display_products.append([product, delta.total_seconds()])
# 	delta = datetime.datetime.now() - start
# 	return render_template('save_each.html', products=disaplay_products,
# 		microseconds=delta.total_seconds(), num_products=len(display_products),
# 		project=datastore_client.project
# 		)


if __name__ == "__main__":
  app.run(host='0.0.0.0', port=8081)

