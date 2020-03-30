<template>
  <div class="container">
    <nav class="navbar navbar-expand-sm navbar-light bg-light">
  <a class="navbar-brand" href="#">Simple Door Delivery</a>
  <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarText" aria-controls="navbarText" aria-expanded="false" aria-label="Toggle navigation">
    <span class="navbar-toggler-icon"></span>
  </button>
  <div class="collapse navbar-collapse" id="navbarText">
    <ul class="navbar-nav mr-auto">

    </ul>
    <ul class="navbar-nav ">
<!--      <li class="nav-item active">-->
<!--        <a class="nav-link" href="#">Home <span class="sr-only">(current)</span></a>-->
<!--      </li>-->
      <li class="nav-item">
        <a class="nav-link" href="#">Contact</a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="#">About</a>
      </li>
    </ul>
    <span class="nav-item">
      <a class="nav-link" href="/cart">Cart({{count}})</a>
    </span>
  </div>
</nav>


    <div class="container">
      <div class="row">
        <div class="col-lg-6">
          <img :src="product.image"/>
        </div>
        <div class="col-lg-6">
          <div class="container">
            <div class="row">
              <div class="col-sm-12">
              <h2>{{product.name}}</h2>
              </div>
            </div>
            <div class="row">
              <div class="col-sm-12" style="margin-top: 20px;">
               <span style="color: #007bff; font-weight: bold;">{{product.display_price}}</span>
              </div>
            </div>
            <div class="row">
              <div class="col-sm-12" style="margin-top: 20px;" >
              <span style="margin-bottom: 20px;">{{product.description}}</span>
              </div>
            </div>
            <div class="row">
              <div class="col-sm-12" style="margin-top: 20px;">
              <span>Quantity:</span>
              </div>
            </div>
            <div class="row">
              <div class="col-sm-12" >
               <span><input v-model="qty" type="text" name="qty" style="padding: 24px;" size="4"/></span>
              </div>
            </div>
            <div class="row">
              <div class="btn-group col-sm-12" role="group" style="margin-top: 20px;">
                <button type="button"
                        class="btn btn-primary btn-block"
                        @click="addCart()">
                    Add
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      product: {
        "name": "",
        "description": "",
        "image": "",
        "price": 0,
        "display_price": "",
        "id": 0
      },
      qty: 1,
      user: {
        fllname: '',
        email: '',
        zipcode: '',
      },
      count: 0
    };
  },
  methods: {
    getProduct() {
      const path = `/api/product/${this.$route.params.product_id}`;
      axios.get(path)
        .then((res) => {
          this.product = res.data['product'];
          this.user = res.data['user'];
          this.count = res.data['count']
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
        });
    },
    addCart(){
      const path = `/api/cart`;
      const payload = {
        product_id: this.product.id,
        qty: this.qty
      };
      axios.post(path, payload)
        .then((res) => {
          this.count = res.data['count'];
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
        });
    }
  },
  created() {
    this.getProduct();
  },
};
</script>

<style scoped>
.navbar{
    margin-bottom: 50px;
  }
</style>
