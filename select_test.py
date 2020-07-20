from socket import *
from select import  select
from time import sleep
#
# f=open("my.log","rb")

tcp_sock=socket()
tcp_sock.bind(("0.0.0.0",8888))
tcp_sock.listen(5)
connfd,addr=tcp_sock.accept()

# udp_sock=socket(AF_INET,SOCK_DGRAM)
# udp_sock.bind(("0.0.0.0",8866))
print("监控IO")
sleep(5)
# rs,ws,xs=select([tcp_sock],[f,udp_sock,connfd],[])
rs,ws,xs=select([tcp_sock,connfd],[],[])
print("rs",rs)
print("ws",ws)
print("xs",xs)