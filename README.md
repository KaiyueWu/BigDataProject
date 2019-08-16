### 1. Usage:
#### 1.1 Environment:
> 1. Docker desktop.

#### 1.2 Install Steps:
> 1. Install database, run command:
```/Users/apple
	docker run --name mnist-cassandra -p 9042:9042 -d cassandra:latest
```
> 2. Configure docker network:
```
	docker network create -d bridge --subnet 192.168.0.0/24 --gateway 192.168.0.1 dockernet
```
> 3. Launch program:
```
	docker run -it -e "MNIST_SERVER_DB_ADDRESS=192.168.0.1" --name=mnist_server -p 8080:80 -d 362213875/mnistserver:0.1
```
### 2. Build:
### 2.1 Build web:
> 1. Navigate to the project root directory.
> 1. Run command:
```
	npm install
	npm run build
```

### 2.2 Build server:
> 1. Navigate to server directory.
> 2. Run command:
```
	python setup.py bdist_wheel
```
### 2.3 Build docker:
> 1. Navigate to public/docker directory.
> 2. Run command:
```
	docker build -t mnistserver:0.1 .
```
###3.Run
###3.1 Open Safari
###3.2 print：
```
        localhost:8080
```
###4.View database
###4.1 Open Python
###4.2 Run file link.py