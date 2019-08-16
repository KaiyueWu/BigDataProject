import os
import argparse
from setuptools import Extension, Command, setup, find_packages

if __name__ == "__main__":
    setup(
        name='mnist_server',
        version='0.0.1',
        description='Mnist Service',
        author="Xin Luo",
        keywords='service',
        install_requires=[
            "flask_cors","flask", 'matplotlib','mxnet',"cassandra-driver"
        ],
        python_requires='>=3.6',
        packages=find_packages(),
        package_dir={'mnist_server': "mnist_server"},
        package_data={
            'mnist_server':['*.params']
        },
        entry_points={
            'console_scripts': [
                'mnist_server=mnist_server.web_service:run',
                'mnist_server_develop=mnist_server.web_service:run_develop',
                'mnist_server_init_db=mnist_server.web_service:init_db',
                'mnist_server_reset_db=mnist_server.web_service:reset_db'
            ]
        }
    )
