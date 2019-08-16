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
