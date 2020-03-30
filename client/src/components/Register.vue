<template>
  <div class="container">
    <div class="row">
      <div class="col-sm-10">
        <h1>Ready to buy?</h1>
        <hr>
        <router-link to="/" class="btn btn-primary">
          Back Home
        </router-link>
        <br><br><br>
        <div class="row">
          <div class="col-sm-12">
            <h3>Register</h3>
            <br>
            <form>
              <div class="form-group">
                <label>Name</label>
                <input type="text"
                       class="form-control"
                       placeholder=""
                       v-model="reg.fllname"
                       required>
              </div>
              <div class="form-group">
                <label>Email</label>
                <input type="text"
                       class="form-control"
                       placeholder=""
                       v-model="reg.email"
                       required>

              </div>
              <div class="form-group">
                <label>Zipcode</label>
                <input type="text"
                       class="form-control"
                       placeholder=""
                       v-model="reg.zipcode"
                       required>
              </div>
              <button class="btn btn-primary btn-block"
                      @click.prevent="validate">
                  Submit
              </button>
            </form>
            <div v-show="errors">
              <br>
              <ol class="text-danger">
                <li v-for="(error, index) in errors" :key="index">
                  {{ error }}
                </li>
              </ol>
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
      reg: {
        fllname: '',
        email: '',
        zipcode: '',
      },
      errors: [],
    };
  },
  methods: {
    validate() {
      this.errors = [];
      let valid = true;
      if (!this.reg.fllname) {
        valid = false;
        this.errors.push('Full name is required.');
      }
      if (!this.reg.email) {
        valid = false;
        this.errors.push('Email is required');
      }
      if (!this.reg.zipcode) {
        valid = false;
        this.errors.push('Zipcode required');
      }
      if (valid) {
        this.register();
      }
    },
    register() {
      const payload = {
        reg: this.reg
      };
      const path = '/api/register';
      axios.post(path, payload)
        .then((res) => {
          // updates
            this.$router.push({ path: `/products/${res.data.distributor}` });
          // this.$router.push({ path: `/hello` });
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
        });
    }
  },
};
</script>

<style scoped>

</style>
