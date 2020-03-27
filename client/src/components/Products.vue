<template>
  <div class="container">
  <h1> {{user.fllname}} - {{count}}</h1>
  <table class="table table-hover">

    <thead>
      <tr>
        <th scope="col">Name</th>
        <th scope="col">Description</th>
        <th scope="col">Image</th>
        <th scope="col">Price</th>
        <th></th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="(product, index) in products" :key="index">
        <td>{{ product.name }}</td>
        <td>{{ product.description }}</td>

        <td><img :src="product.image"/></td>
        <td>${{ product.price }}</td>
        <td>
          <div class="btn-group" role="group">
            <button type="button"
                    class="btn btn-sm"
                    @click="addCart(product)">
                Add
            </button>
          </div>
        </td>
      </tr>
    </tbody>
  </table>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      products: [],
      user: {
        fllname: '',
        email: '',
        zipcode: '',
      },
      count: 0
    };
  },
  methods: {
    getProducts() {
      const path = `/api/products/${this.$route.params.distributor_id}`;
      axios.get(path)
        .then((res) => {
          this.products = res.data['products'];
          this.user = res.data['user'];
          this.count = res.data['count']
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
        });
    },
    addCart(product){
      const path = `/api/cart`;
      const payload = {
        product_id: product.id,
        qty: 1
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
    this.getProducts();
  },
};
</script>

<style scoped>

</style>
