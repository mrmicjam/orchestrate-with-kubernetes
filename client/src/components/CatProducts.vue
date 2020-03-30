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
<!--    <div @click="$router.go(-2)">back</div>-->

    <div class="container">
      <div class="col-lg-12" style="text-align: center; margin: auto;">
        <ul style="padding: 0;">
          <li style="display: inline; padding: 20px;" v-for="cat in cats">
            <span v-if="current_cat === cat" style="text-decoration: underline;">{{ cat }}</span>
            <span v-else><a style="text-decoration: none; color: #000;" href="#" @click="loadCat(cat)">{{ cat }}</a></span>
          </li>
        </ul>
      </div>
    </div>

    <div class="container">
      <div class="row" v-for="chunk in productChunks">
        <div class="col-sm" v-for="product in chunk" style="margin-top: 20px;">
          <router-link :event="product.can_order ? 'click' : ''" :to="'/product/' + product.id" style="text-decoration: none; color: #000;">
            <img style="padding-bottom: 20px;" :src="product.image"/><br/>
            <span style="padding-bottom-top: 10px; font-weight: bold;">{{ product.name }}</span><br/>
            <span style="padding-bottom-top: 10px;">{{ product.display_price }}</span>
          </router-link>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import axios from 'axios';
import _ from 'lodash';

export default {
  data() {
    return {
      products: [],
      current_cat: "All",
      cats: ["All", "Dairy"],
      user: {
        fllname: '',
        email: '',
        zipcode: '',
      },
      count: 0
    };
  },
  computed: {
      productChunks(){
          return _.chunk(Object.values(this.products), 3);
      }
    },
  methods: {
    loadCat(cat) {
      const path = `/api/products/${this.$route.params.distributor_id}?cat=${cat}`;
      axios.get(path)
        .then((res) => {
          this.products = res.data['products'];
          this.user = res.data['user'];
          this.count = res.data['count'];
          this.current_cat = cat;
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
        });
    },
  },
  created() {
    this.loadCat("All");
  },
};
</script>

<style scoped>
  .navbar{
    margin-bottom: 50px;
  }
</style>
