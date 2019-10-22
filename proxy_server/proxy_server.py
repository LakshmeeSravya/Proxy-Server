import socket
import threading
import signal
import sys
import os
import glob
import time
CRLF = "\r\n\r\n"

class Proxy_Server:

    def __init__(self):
        os.chdir("Cache")
        signal.signal(signal.SIGINT, self.shutdown)     # Shutdown on Ctrl+C
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)       # Create a TCP socket
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)    # Re-use the socket
        self.server_sock.bind(("localhost", 12345)) # bind the socket
        self.server_sock.listen(10)    # become a server socket


    def accept_conn(self):
        i=1
        while True:
            client_sock, client_address = self.server_sock.accept()   # Accept the connection
            d = threading.Thread(name="Client"+str(i), target=self.requests, args=(client_sock, client_address))
            d.setDaemon(True)
            d.start()
            i += 1
        self.shutdown(0, 0)


    def requests(self, conn, client_addr):
        request = conn.recv(1000)        # get the request from browser
        print request
        first_line = request.split('\n')[0]      # parse the first line
        url = first_line.split(' ')[1]           # get url

        http_pos = url.find("://")          # find pos of ://
        if (http_pos==-1):
            temp = url
        else:
            temp = url[(http_pos+3):]       # get the rest of url

        port_pos = temp.find(":")           # find the port pos

        webserver_pos = temp.find("/")
        filename = temp[webserver_pos+1:]

        if webserver_pos == -1:
            webserver_pos = len(temp)

        webserver = ""
        port = -1
        if (port_pos==-1 or webserver_pos < port_pos):      # default port
            port = 80
            webserver = temp[:webserver_pos]
        else:                                               # specific port
            port = int((temp[(port_pos+1):])[:webserver_pos-port_pos-1])
            webserver = temp[:port_pos]

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create a socket to connect to the web server
            s.settimeout(5)
            s.connect((webserver, port))

            filename = filename.strip("/")
            flag =  os.path.isfile(filename)

            if not flag:
                s.send("GET /%s HTTP/1.1\r\nHOST: %s%s" % (filename, webserver,CRLF))  #send request to the server
            else:
                t = time.ctime(os.path.getmtime(filename))
                s.send("GET /%s HTTP/1.1\r\nHOST: %s\r\nIf-Modified-Since: %s%s" % (filename, webserver, t, CRLF))

            temp_data = ""
            while True:
                data = s.recv(256)
                temp_data += data
                if (len(data) <= 0):
                    break
            print temp_data
            if "304 Not Modified" in temp_data and flag:  # if the file is present and is not modified
                 f = open(filename, 'rb')
                 chunk = f.read(256)
                 while chunk:
                     conn.send(chunk)
                     chunk = f.read(256)
                 f.close()

            elif "200 OK" in temp_data and flag: # if the file is present and is modified
                f = open(filename, 'w+')
                temp2 = temp_data.splitlines()
                l = 0
                for k in temp2:
                    if l > 7:
                        f.write(k + "\n")
                        conn.send(k + "\n")
                    l += 1
                f.close()

            elif not flag:
                 num_files = len(os.listdir('.'))  # get the number of files in current directory

                 if num_files < 3:  # if the file is not present and the cache is not full
                     f = open(filename, 'w+')
                     temp2 = temp_data.splitlines()
                     l = 0
                     for k in temp2:
                         if l > 7:
                             f.write(k + "\n")
                             conn.send(k + "\n")
                         l += 1
                     f.close()

                 elif num_files == 3: # if the file is not present and the cache is full
                     fnames = glob.glob("*")
                     fnames.sort(key=os.path.getmtime)

                     os.remove(fnames[0])

                     f = open(filename, 'w+')
                     temp2 = temp_data.splitlines()
                     l = 0
                     for k in temp2:
                         if l > 7:
                             f.write(k + "\n")
                             conn.send(k + "\n")
                         l += 1
                     f.close()

            s.close()
            conn.close()
        except socket.error as error_msg:
            print 'ERROR: ',client_addr,error_msg
            if s:
                s.close()
            if conn:
                conn.close()


    def shutdown(self, signum, frame):
        self.server_sock.close()
        sys.exit(0)


if __name__ == "__main__":
    server = Proxy_Server()
    server.accept_conn()
