<template>
  <div id="app">
    <draw/>
    <!--<draw2/>-->
  </div>
</template>

<script>
import Draw from "./components/Draw";
// import Draw2 from "./components/Draw2";

export default {
  name: 'app',
  components: {
      Draw,
      // Draw

  }
}
</script>

<style>
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  /*margin-top: 60px;*/
}
</style>
