from sqlalchemy import Column, ForeignKey, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func

import datetime
import decimal

Base = declarative_base()


class Distributor(Base):
   __tablename__ = 'distributors'

   id = Column(Integer, primary_key=True)
   branding = Column(String(250), nullable=True)
   title = Column(String(250), nullable=False)
   zips = relationship("Zip", backref=backref("distributor", uselist=False))
   retail_products = relationship("RetailProduct", backref=backref("distributor", uselist=False))

   def __repr__(self):
       return self.title



class Zip(Base):
    __tablename__ = 'zips'

    id = Column(Integer, primary_key=True)
    zip_code = Column(String(10), nullable=False)
    distributor_id = Column(Integer, ForeignKey('distributors.id'))

    def __repr__(self):
        return self.zip_code


class ProductCategory(Base):
    __tablename__ = 'product_categories'

    name = Column(String(500), primary_key=True)

    products = relationship("Product",  backref=backref("category", uselist=False))

    def __repr__(self):
        return self.name


class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    product_category = Column(String(500), ForeignKey('product_categories.name'))
    name = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    base_price = Column(Integer, nullable=False)
    retail_products = relationship("RetailProduct", backref=backref("product", uselist=False))
    image = Column(String(500), nullable=False)

    def __repr__(self):
        return self.name


class RetailProduct(Base):
    __tablename__ = 'retail_products'

    id = Column(Integer, primary_key=True)
    distributor_id = Column(Integer, ForeignKey('distributors.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    price = Column(Integer, nullable=False)
    distributor_daily_limit = Column(Integer, nullable=True)
    order_daily_limit = Column(Integer, nullable=True)
    order_items = relationship("OrderItem", backref=backref("retail_product", uselist=False))

    def __repr__(self):
        return "{} - {}".format(self.product.name, self.distributor.title)

    @property
    def name(self):
        return self.product.name

    @property
    def description(self):
        return self.product.description

    @property
    def image(self):
        return self.product.image

    @property
    def display_price(self):
        return "${}".format((decimal.Decimal(self.price) / decimal.Decimal("100.0")).quantize(decimal.Decimal('0.00')))

    @property
    def can_order(self):
        if self.distributor_daily_limit is None:
            return True
        # check if order limit for distributor reached
        from session import db_session
        total_orders = db_session.query(func.count(OrderItem.qty).label('total')).join(Order).filter(
            OrderItem.retail_product_id == self.id).filter(Order.created_at >= datetime.date.today()).first()[0]
        if total_orders >= self.distributor_daily_limit:
            return False
        return True


class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True)
    distributor_id = Column(Integer, ForeignKey('distributors.id'))
    address = Column(String(500), nullable=False)
    city = Column(String(250), nullable=False)
    state = Column(String(10), nullable=False)
    zip = Column(String(11), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.now)
    submitted_at = Column(DateTime, nullable=True)
    payed_at = Column(DateTime, nullable=True)
    name = Column(String(500), nullable=False)
    email = Column(String(500), nullable=False)
    phone = Column(String(100), nullable=True)

    def __repr__(self):
        return "{} -  {}, {}, {}".format(self.id, self.name, self.city, self.state)

class OrderItem(Base):
    __tablename__ = 'order_items'

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    purchase_price = Column(Integer, nullable=False)
    qty = Column(Integer, nullable=False)
    retail_product_id = Column(Integer, ForeignKey('retail_products.id'))

    def __repr__(self):
        return "{} -  {} {}X{}".format(self.order_id, self.retail_product_id, self.qty, self.purchase_price)


class User(UserMixin, Base):
    """Model for user accounts."""

    __tablename__ = 'flasklogin-users'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=False)
    email = Column(String(40), unique=True, nullable=False)
    password = Column(String(200), primary_key=False, unique=False, nullable=False)
    created_on = Column(DateTime, index=False, unique=False, nullable=True)
    last_login = Column(DateTime, index=False, unique=False,nullable=True)

    def set_password(self, password):
        """Create hashed password."""
        self.password = generate_password_hash(password, method='sha256')

    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password, password)

    def __repr__(self):
        return '<User {}>'.format(self.name)
