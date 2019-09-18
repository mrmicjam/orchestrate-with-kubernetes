from flask import Flask, render_template
from google.cloud import datastore


datastore_client = datastore.Client()


app = Flask(__name__)

@app.route('/')
def root():
    products = datastore_client.query(kind="deal_product").fetch(limit=5)
    return render_template('index.html', products=products)

if __name__ == "__main__":
  app.run(host='0.0.0.0', port=8080)

