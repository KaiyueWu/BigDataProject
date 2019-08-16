import base64
import io
import os
import mxnet as mx
from mxnet import nd, image
from mxnet.gluon import nn
import re
import numpy as np


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


class Predictor:
    def __init__(self):
        self._net = _init_cnn()

    def predict(self, data):
        data = re.sub('^data:image/.+;base64,', '', data)
        binary_data = base64.b64decode(data)

        # from PIL import Image
        # image_data = io.BytesIO(binary_data)
        # image = Image.open(image_data)
        # image.save('test.jpeg')

        img = mx.img.imdecode(binary_data)
        img = mx.img.imresize(img, 28, 28, interp=2)

        # import matplotlib.pyplot as plt
        # plt.imshow(img.asnumpy().astype(np.uint8))
        # plt.show()

        img = img[:, :, 1]
        img = 255 - img
        img = img.astype(np.float32) / 255
        img = img.reshape(1, 1, 28, 28)
        return int(nd.argmax(self._net(img),axis=1).asnumpy().astype(np.int)[0])


predictor = Predictor()

if __name__ == "__main__":
    res = predictor.predict(
        "data:image/jpeg;base64,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")
    print("Predict:", res)
