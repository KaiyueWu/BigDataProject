#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 15 22:12:40 2019

@author: apple
"""

from cassandra.cluster import Cluster

if __name__ == "__main__":
    cluster = Cluster(contact_points=['127.0.0.1'], port=9042)
    session = cluster.connect()
    session.set_keyspace('mnistserver')
    result = session.execute("""
                    SELECT * from mnist_server;""")
    #print(dir(result))
    for row in result:
        print(row)
        break