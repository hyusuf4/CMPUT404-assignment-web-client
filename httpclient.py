#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def get_host_port(self,url):
        url_object=urllib.parse.urlparse(url)
        host_name=url_object.hostname
        if url_object.port==None:
            port=80
        else:
            port=url_object.port
        return (host_name,port)
    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return self.socket

    def get_code(self, data):
        return int(data.split()[1])

    def get_headers(self,data):
        return data.split('\r\n\r\n')[0]

    def get_body(self, data):
        return data.split('\r\n\r\n')[1]

    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))

    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        (host,port)=self.get_host_port(url)
        self.connect(host,port)
        url_object=urllib.parse.urlparse(url)
        if(not url_object.path):
            path='/'
        else:
            path=url_object.path

        get_request='GET {} HTTP/1.1\r\n'.format(path)
        get_request+='Host: {}\r\n'.format(url_object.hostname)
        get_request+='Content-type: application/x-www-form-urlencoded\r\n'
        get_request+='Connection: close\r\n\r\n'
        self.sendall(get_request)
        data=self.recvall(self.socket)
        self.close()
        code=self.get_code(str(data))
        body = self.get_body(str(data))
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        (host,port)=self.get_host_port(url)
        self.connect(host,port)
        url_object=urllib.parse.urlparse(url)
        if(not url_object.path):
            path='/'
        else:
            path=url_object.path
        if args== None:
            post=''
        else:
            post=urllib.parse.urlencode(args)
        post_request='POST {} HTTP/1.1\r\n'.format(path)
        post_request+='Host: {}\r\n'.format(url_object.hostname)
        post_request+='Content-type: application/x-www-form-urlencoded\r\n'
        post_request+='Content-Length: {}\r\n'.format(len(post))
        post_request+='Connection: close\r\n\r\n'
        post_request+=post
        self.sendall(post_request)
        data=self.recvall(self.socket)
        self.close()
        code=self.get_code(str(data))
        body = self.get_body(str(data))
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )

if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
