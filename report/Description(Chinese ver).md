## 实现细节:
#### 1. CNN模型准备:
> 在这个项目中，我选择使用Mnist手写数字数据集，mxnet深度学习框架进行训练和预测。首先，我从官网中下载Mnist手写数字数据集合，其中包含了训练和检测数据集。然后使用了mxnet官网中提供的CNN模型进行训练，经过多次对训练次数进行尝试，最后确定训练次数为50次。训练结束后，我将训练得到的参数保存到文件中。
```
num_epochs = 10

for epoch in range(num_epochs):
    for inputs, labels in train_loader:
        inputs = inputs.as_in_context(ctx)
        labels = labels.as_in_context(ctx)

        with autograd.record():
            outputs = lenet(inputs)
            loss = loss_function(outputs, labels)

        loss.backward()
        metric.update(labels, outputs)

        trainer.step(batch_size=inputs.shape[0])

    name, acc = metric.get()
    print('After epoch {}: {} = {}'.format(epoch + 1, name, acc))
    metric.reset()

for inputs, labels in val_loader:
    inputs = inputs.as_in_context(ctx)
    labels = labels.as_in_context(ctx)
    metric.update(labels, lenet(inputs))
net.save_parame
```

#### 2. 设计后端识别接口:
> 由于系统最终会由用户通过web提交手写的图片到服务端进行识别，我使用轻量级、易用的Flask设计了后端识别检测的接口。我只设计了一个Web接口来完成相关工作，部分代码如下:
```
@app.route("/api/mnist/identify", methods=['POST'])
@cross_origin(supports_credentials=True)
def mnist_identify():
    params = json.loads(request.data)
    predict = predictor.predict(params['data'])
    db_helper.insert_data(params['data'], str(predict))
    return json.dumps({'predict': predict})
```
> 当用户将图片提交到服务端，我需要使用之前训练好的CNN模型，对其进行预测。首先，我基于mxnet的CNN进行建模，并使用之前训练好的参数进行初始化，代码如下:
```
def _init_cnn():
    net = nn.HybridSequential(prefix='LeNet_')
    with net.name_scope():
        net.add(
            nn.Conv2D(channels=20, kernel_size=(5, 5), activation='tanh'),
            nn.MaxPool2D(pool_size=(2, 2), strides=(2, 2)),
            nn.Conv2D(channels=50, kernel_size=(5, 5), activation='tanh'),
            nn.MaxPool2D(pool_size=(2, 2), strides=(2, 2)),
            nn.Flatten(),
            nn.Dense(500, activation='tanh'),
            nn.Dense(10, activation=None),
        )
    ctx = mx.cpu(0)
    net.initialize(mx.init.Xavier(), ctx=ctx)
    net.load_parameters(os.path.join(os.path.dirname(os.path.abspath(__file__)),'net.params'))
    return net
```
> 对于用户每次提交的图片,首先需要将图片进行压缩至(28x28)大小，然后进行归一化数据处理。最后，我使用模型对其进行预测，相关代码如下:
```
    def predict(self, data):
        data = re.sub('^data:image/.+;base64,', '', data)
        binary_data = base64.b64decode(data)

        img = mx.img.imdecode(binary_data)
        img = mx.img.imresize(img, 28, 28, interp=2)

        img = img[:, :, 1]
        img = 255 - img
        img = img.astype(np.float32) / 255
        img = img.reshape(1, 1, 28, 28)
        return int(nd.argmax(self._net(img),axis=1).asnumpy().astype(np.int)[0])
```
> 由于，系统需要对用户每次提交的图片以及识别的信息记录到数据库中，从而方便用户可以对数据进行后处理等。对此，我使用了开源分布式NoSql数据库-Cassandra，对于用户的每次提交，我将相关数据、结果保存到数据库中，相关代码如下：
```
    def insert_data(self, image, identify):
        try:
            self._session.execute("""
                      INSERT INTO mnist_server (id, image, time, identify) 
                      VALUES('{}', '{}', '{}', '{}');
                      """.format(str(uuid.uuid1()), image, int(datetime.datetime.utcnow().timestamp() * 1000),
                                 identify))

        except Exception as e:
            logger.error("Insert data failed, details;{}".format(e))
```
#### 3. 设计前端交互相关:
> 由于系统支持用户通过web书写数字进行识别，我选用了基于vue的前端框架进行开发。首先，我使用了html5的canvas绘制一个画板区域，使得用户可以在区域中书写数字，然后通过按钮将数据提交到服务端进行识别。关于提交部分，我使用了node的axios模块将请求异步发送到服务端。相关代码如下:
```
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
```
#### 4. Docker部署:
> Docker使得我可以将整个系统(包含前端与后端)进行整合，用户部署、使用会变得非常简单。首先，由于后端server基于Python Flask进行开发，我选择了将Docker基于Python3镜像进行开发。在Dokcerfile配置文件中，首先，我进行了基础环境依赖的安装(apt-utils、nginx等)，接着我通过pip命令安装server所依赖的相关python模块库，接着我将服务端程序进行了打包与安装。然后，进行了nginx代理相关配置。在Dockerfile中，我提供了环境变量参数，使得用户可以改变系统web端口、数据库连接地址及端口信息。相关代码如下:
```
FROM python:3
USER root
WORKDIR /usr/src/app
RUN mkdir -p /usr/webapps/mnist_server && mkdir -p /usr/webapps/server
ADD source/client/ /usr/webapps/mnist_server
ADD source/server/ /usr/webapps/server

ENV MNIST_SERVER_PORT 8888
ENV MNIST_SERVER_DB_ADDRESS 127.0.0.1
ENV MNIST_SERVER_DB_PORT 9042

RUN apt-get -y update && apt-get -y install apt-utils && apt-get -y install nginx && apt-get -y install vim \
&& pip install -r /usr/webapps/server/requirements.txt && cd /usr/webapps/server \
&& python setup.py clean --all && python setup.py bdist_wheel \
&& pip install /usr/webapps/server/dist/mnist_server-0.0.1-py3-none-any.whl \
&& rm -f /etc/nginx/nginx.conf
ADD nginx.conf /etc/nginx
ADD app.conf /etc/nginx/conf.d
ENTRYPOINT nginx -c /etc/nginx/nginx.conf && mnist_server $MNIST_SERVER_PORT $MNIST_SERVER_DB_ADDRESS $MNIST_SERVER_DB_PORT
```
#### 5. 环境配置:
> 由于Cassandra已经非常流行，我们可以直接通过Docker进行安装,示例代码如下:
```
docker run --name mnist-cassandra -p 9042:9042 -d cassandra:latest
```
> 接着，我们需要配置Docker网络，从而使得系统可以连接到Cassandra数据库中。相关代码如下:
```
    docker network create -d bridge --subnet 192.168.0.0/24 --gateway 192.168.0.1 dockernet

```