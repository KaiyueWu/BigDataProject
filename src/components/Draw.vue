<template>
  <div class="layout">
    <!--<div class="header">
      <div class="logo">
        <span>Drawing</span>
      </div>
    </div>-->
    <div class="content">

      <div class="content-right">
        <!--<img src="../assets/board.png" width="400" height="400" style="padding-top: 0px;padding-left: 0px;position: absolute">-->
        <div class="body" >
          <canvas id="canvas" style="border-radius: 15px;margin-top: 35px;margin-left: 35px" ref="canvas" :style="{cursor:curcursor,width:canvasSize.width+'px',height:canvasSize.height+'px'}"></canvas>
          <canvas id="canvas_bak" style="border-radius: 15px;margin-top: 35px;margin-left: 35px" ref="canvas_bak" :style="{cursor:curcursor,width:canvasSize.width+'px',height:canvasSize.height+'px'}"></canvas>
        </div>
        <div style="padding-top: 10px;padding-left: 80px;">
          <el-button @click="clearPlotData">Clear</el-button>
          <el-button @click="saveImageData">Submit</el-button>
        </div>
      </div>
      <div class="div-identify-result">
        <strong>Print：</strong>
        <span>{{this.identifyResult}}</span>
      </div>
    </div>
  </div>
</template>

<script>
    const axios = require('axios');
    export default {
        name: 'Draw',
        data () {
            return {
                canvasSize: {
                  width:300,
                  height:300
                },
                canvas: this.$refs.canvas,
                canvasTop: 67,
                canvasLeft: 0,
                context: null,
                canvas_bak: this.$refs.canvas_bak,
                context_bak: null,
                toolsToggle: false,
                color: {
                    hex: '#000000',
                    a: 1
                },
                penSize: 8,
                lineType: [0, 0],
                canDraw: false,
                curcursor: 'auto',
                tools: [{
                    name: '铅笔',
                    icon: 'mode_edit',
                    fun: 'pencil',
                    ischoose: false,
                }],
                identifyResult:"-"
            }
        },
        methods: {
            initCanvas () {
                this.canvas =  document.getElementById("canvas");
                this.canvas.width = this.canvasSize.width;
                this.canvas.height = this.canvasSize.height;
                this.context = this.canvas.getContext('2d');
                this.context.fillStyle='#FFFFFF';
                this.context.fillRect(0,0,this.canvasSize.width,this.canvasSize.height);
                this.canvas_bak =  document.getElementById("canvas_bak");
                this.canvas_bak.width = this.canvasSize.width;
                this.canvas_bak.height = this.canvasSize.height;
                this.context_bak = this.canvas_bak.getContext('2d');
                this.context_bak.fillStyle='#FFFFFF';
                this.context_bak.fillRect(0,0,this.canvasSize.width,this.canvasSize.height);
            },
            drawType (pen) {
                switch (pen.fun) {
                    case 'pencil':
                        this.curcursor = "url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAQAAABKfvVzAAAAZ0lEQVR4AdXOrQ2AMBRF4bMc/zOUOSrYoYI5cQQwpAieQDW3qQBO7Xebxx8bWAk5/CASmRHzRHtB+d0Bkw0W5ZiT0SYbFcl6u/2eeJHbxIHOhWO6Er6/y9syXpMul5PLefAGKZ1/rwtTimwbWLpiCgAAAABJRU5ErkJggg==') 3 24,  auto"
                        break;
                    default:
                        this.curcursor = 'auto';
                        break;
                }
                this.draw_graph(pen.fun);
                this.chooseImg(pen)
            },
            chooseImg(obj){
                for (let i = 0; i < this.tools.length; i++) {
                    this.tools[i].ischoose = false
                }
                obj.ischoose = true
            },
            draw_graph (graphType) {
                this.canvas_bak.style.zIndex = 1;
                this.canDraw = false;
                let startX,startY;
                let mousedown = (e) => {
                    this.context.strokeStyle = this.color.hex;
                    this.context_bak.strokeStyle = this.color.hex;
                    this.context_bak.lineWidth = this.penSize;
                    e=e||window.event;
                    startX = e.offsetX;
                    startY = e.offsetY;
                    this.context_bak.moveTo(startX, startY);
                    this.canDraw = true;
                    if(graphType == 'pencil'){
                        this.context_bak.beginPath()
                    }
                };
                let mouseup = (e) => {
                    e=e||window.event;
                    this.canDraw = false;
                    let image = new Image();

                    image.src = this.canvas_bak.toDataURL();
                    image.onload = () => {
                        this.context.drawImage(image, 0, 0, image.width, image.height, 0, 0, this.canvasSize.width, this.canvasSize.height);
                        this.clearContext();
                    };
                    let x = e.offsetX;
                    let y = e.offsetY;

                    this.context.beginPath();
                    this.context.moveTo(x, y);
                    this.context.lineTo(x + 2, y + 2);
                    this.context.stroke();
                };
                let mousemove = (e) => {
                    e=e||window.event;
                    this.context_bak.setLineDash(this.lineType);
                    console.log("Mouse move:",e.offsetX, e.offsetY);
                    if (graphType == 'pencil') {
                        if (this.canDraw) {
                            this.context_bak.lineTo(e.offsetX,e.offsetY);
                            this.context_bak.stroke()
                        }
                    }
                };
                let mouseout = () => {
                    if (graphType != 'handwriting') {
                        this.clearContext()
                    }
                };
                this.canvas_bak.onmousedown = () => mousedown();
                this.canvas_bak.onmousemove = () => mousemove();
                this.canvas_bak.onmouseup = () => mouseup();
                this.canvas_bak.onmouseout = () => mouseout();

            },
            clearContext (type) {
                if (!type) {
                    this.context_bak.clearRect(0, 0, this.canvasSize.width, this.canvasSize.height)
                } else {
                    this.context.clearRect(0, 0, this.canvasSize.width, this.canvasSize.height)
                    this.context_bak.clearRect(0, 0, this.canvasSize.width, this.canvasSize.height)
                }
            },
          saveImageData(){
              let data = this.canvas.toDataURL('image/jpeg','image/jpeg' );
              console.log("This:", this.axios);
              axios.post('/api/mnist/identify', {
                  data: data,
              })
              .then(function (response) {
                      console.log(response);
                      if(response.data !== undefined){
                          this.identifyResult = response.data.predict;
                      }
                  }.bind(this))
              .catch(function (error) {
                      console.log(error);
              });
              console.log('Data:',data);
          },
            addkeyBoardlistener () {
                document.onkeydown = (event) => {
                    let e = event || window.event || arguments.callee.caller.arguments[0]
                }
            },
          clearPlotData(){
              this.clearContext(true);

              this.context.fillStyle='#FFFFFF';
              this.context.fillRect(0,0,this.canvasSize.width,this.canvasSize.height);
              this.context_bak.fillStyle='#FFFFFF';
              this.context_bak.fillRect(0,0,this.canvasSize.width,this.canvasSize.height);
          }

        },
        components: {
        },
        mounted () {
            this.initCanvas();
            this.addkeyBoardlistener();
            this.drawType(this.tools[0]);
            this.canvas_bak.addEventListener('click', this.falseColor);
            window.addEventListener('resize', () => {
                this.canvasSize = {
                    // width: window.screen.availWidth,
                    // height: window.screen.availHeight
                }
            })
        }
    }
</script>
<style scoped>
  * {
    -webkit-user-select: none;
    -moz-user-select: none;
    -ms-user-select: none;
    user-select: none;
  }

  canvas {
    position: absolute;
    z-index : 0;
    left: 0;
    right: 0;
    width: 100%;
    height:100%;
  }

  .layout {
    height: 100%;
    /*background: url("../assets/background.gif") no-repeat;*/
    background: url("../assets/001.gif") no-repeat;
    background-size: 100% 100%;
  }

  .header {
    background-color: #2196f3;
    position: relative;
    display: flex;
    align-items: center;
  }

  .logo {
    display: flex;
    align-items: center;
    font-size: 24px;
    color: white;
    padding: 10px 20px;
  }


  .content {
    overflow: hidden;
    width: 100%;
    /*height: calc(100vh - 56px);*/
    height: calc(100vh - 0px);
    display: flex;
  }

  .content-right {
    background-color: rgba(0, 0, 0, 0);
    padding-top: calc(30vh);
    padding-left: calc(31vw );
    width: calc(23vw);
    height: calc(24vh);
  }
  .div-identify-result{
    padding-top: calc(40vh);
    padding-left: calc(15vw );
    font-size: 64px;
    font-family:"KaiTi",serif;

  }
  .body {
    position: relative;
    /*background-color: white;*/
    background: url("../assets/board.png") no-repeat;
    background-size: 380px 380px;
    /*border-radius: 5px;*/
    /*height:100%;*/
    margin: 0 auto;
    border-radius: 15px;
    width: 380px;
    height: 380px;
  }

</style>