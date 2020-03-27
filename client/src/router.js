import Vue from 'vue';
import Router from 'vue-router';
import Ping from './components/Ping.vue';
import Order from './components/Order.vue';
import OrderComplete from './components/OrderComplete.vue';
import Register from './components/Register.vue';
import Products from './components/Products.vue';
import Cart from './components/Cart.vue';

Vue.use(Router);

export default new Router({
  mode: 'history',
  base: process.env.BASE_URL,
  routes: [
    {
      path: '/',
      name: 'Register',
      component: Register,
    },
    {
      path: '/products/:distributor_id',
      name: 'Products',
      component: Products,
    },
    {
      path: '/cart/',
      name: 'Cart',
      component: Cart,
    },
    {
      path: '/order/:id',
      name: 'Order',
      component: Order,
    },
    {
      path: '/complete/:id',
      name: 'OrderComplete',
      component: OrderComplete,
    },
    {
      path: '/ping',
      name: 'Ping',
      component: Ping,
    },
  ],
});
