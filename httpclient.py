#!/usr/bin/env python
# coding: utf-8
# Copyright 2016 Abram Hindle, Jinzhu Li, https://github.com/tywtyw2002, and https://github.com/treedust
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
import urllib

def help():
    print "httpclient.py [GET/POST] [URL]\n"

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def get_host_port(self,url):
        # Example HTTP URL from slides http://[username:password@]hostname[:port]/path/to/resource/resource.html
        url = url.strip('http://')
        #print url
        temp = url.split('/')[0]
        # split hostname, port and path
        if "@" in url:
            port = int(temp.split(':')[2])
            hostname = temp.split('@')[1].split(':')[0]
        elif len(temp.split(':')) == 2:
            port = int(temp.split(':')[1])
            hostname = temp.split(':')[0]
        else:
            port = 80
            hostname = temp
        if len(url.split('/')) >= 2:
            # missing fisrt '/' causing error
            path = '/' + url.split('/',1)[1]
        else:
            path = '/'

        #print "host: " + hostname
        #print "port: " + str(port)
        #print "path: " + path
        return hostname, port, path

    def connect(self, host, port):
        # use sockets!
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.connect((host, port))
        return clientSocket

    def get_code(self, data):
        code = int(data.split(' ')[1])
        return code

    def get_headers(self,data):
        headers = data.split('\r\n\r\n')[0]
        return headers

    def get_body(self, data):
        body = data.split('\r\n\r\n')[1]
        return body

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
        return str(buffer)

    def GET(self, url, args=None):
        code = 500
        body = ""
        host, port, path = self.get_host_port(url)
        socket = self.connect(host, port)
        # first time forgot \r\n cause program cannot stop
        header = "GET %s HTTP/1.1\r\n" % path + \
                "Host: %s:%d\r\n" % (host, port) + \
                "Connection: close\r\n\r\n"
        socket.sendall(header)
        data = self.recvall(socket)
        socket.close()
        #print "--DATA: \r\n" + data
        print header
        code = self.get_code(data)
        body = self.get_body(data)
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""
        # reference: https://docs.python.org/2/library/urllib.html#examples
        if args is not None:
            query = urllib.urlencode(args)
            length = len(query)
        else:
            query = ''
            length = 0
        host, port, path = self.get_host_port(url)
        socket = self.connect(host, port)
        header = "POST %s HTTP/1.1\r\n" % path + \
                "Host: %s:%d\r\n" % (host, port) + \
                "Content-Type: application/x-www-form-urlencoded\r\n" + \
                "Content-Length: %d\r\n" % length + \
                "Connection: close\r\n\r\n"
        # query in the body in POST, without query in body dose not work
        socket.sendall(header + query + "\r\n")
        data = self.recvall(socket)
        socket.close()
        #print "--DATA: \r\n" + data
        print header
        code = self.get_code(data)
        body = self.get_body(data)
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
        print client.command( sys.argv[2], sys.argv[1] )
    else:
        print client.command( sys.argv[1] )
