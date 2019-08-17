## Implementation:
#### 1. CNN model preparation:
> In this project, I chose to use Mnist handwritten digital data set and mxnet deep learning framework for training and prediction. First, I downloaded Mnist handwritten digital data set from the official website, which contains the training and testing data set. Then, the CNN model provided in the official website of mxnet was used for training. After several attempts on the training times, the training times were finally determined to be 50 times. After the training, I saved the parameters obtained from the training to a file.
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

#### 2. Design back-end identification interface:
> As the system will be eventually submitted by the user to the server for recognition through web handwritten pictures, I designed a back-end identification and detection interface using a lightweight and easy to use Flask. I only designed a Web interface to complete relevant work, and part of the code is as follows:
```
@app.route("/api/mnist/identify", methods=['POST'])
@cross_origin(supports_credentials=True)
def mnist_identify():
    params = json.loads(request.data)
    predict = predictor.predict(params['data'])
    db_helper.insert_data(params['data'], str(predict))
    return json.dumps({'predict': predict})
```
> When the user submits the image to the server, I need to use the previously trained CNN model to predict it. First of all, I modeled the CNN based on mxnet and initialized it with parameters trained before. The code is as follows:
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
> For each image submitted by the user, the image needs to be compressed to a size of (28x28), and then normalized data processing is carried out. Finally, I use the model to predict it, and the relevant codes are as follows:
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
> Since the system needs to record the pictures submitted by users and the identified information into the database, it is convenient for users to post-process the data. For this, I used Cassandra, an open-source distributed NoSql database. For each user's submission, I saved the relevant data and results to the database. The relevant code is as follows:
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
#### 3. Design front-end interaction related:
> Since the system supports users to identify by writing Numbers on the web, I chose the front-end framework based on vue for development. First, I used the html5 canvas to draw an artboard area, enabling users to write Numbers in the area, and then submit the data to the server for identification through the button. As for the submission part, I used node's axios module to send the request asynchronously to the server side. The relevant codes are as follows:
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
#### 4. Docker deployment:
> Docker enables me to integrate the whole system (including front-end and back-end), making it very easy for users to deploy and use. First, because the back-end server is developed based on Python Flask, I chose to develop Docker based on Python3 mirror. In the Dokcerfile configuration file, first I install the base environment dependencies (apt-utils, nginx, etc.), then I install the relevant python module libraries that the server depends on through the PIP command, and then I package and install the server program. Then, the nginx proxy is configured. In Dockerfile, I provide environment variable parameters that allow users to change the system web port, database connection address and port information. The relevant codes are as follows:

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
#### 5. Environment configuration:
> Since Cassandra is already very popular, we can install it directly through Docker. The sample code is as follows:
```
docker run --name mnist-cassandra -p 9042:9042 -d cassandra:latest
```
> Next, we need to configure the Docker network so that the system can connect to the Cassandra database. The relevant codes are as follows:
```
    docker network create -d bridge --subnet 192.168.0.0/24 --gateway 192.168.0.1 dockernet

```