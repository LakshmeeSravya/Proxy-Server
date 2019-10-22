## Proxy Server

### Instructions
1) Run the Proxy_Server.py file in Proxy_Server directory.  
   *python proxy.py*  
   It will always run proxy on port 12345.  

2) Run the server.py file in server directory.  
   *python server.py*  
   It will run proxy on port 20000.  


- The proxy server receives the request from client and pass it to the server after parsing the data.

- The requested file is cached. All the cached files can be seen in the 'Cache' directory.

- Cache has a limited size of 3. So if the cache is full and another file needs to be cached then the least recently used file is deleted.

- If a file present in the cache is modified at the server side, the file is replaced in the cache when requested again. Else, the cached file is sent to the client.
