from socket import *
from select import select
HOST="0.0.0.0"
PORT=8889
ADDR=(HOST,PORT)

tcp_sock=socket()
tcp_sock.bind(ADDR)
tcp_sock.listen(5)
tcp_sock.setblocking(False)

rlist=[tcp_sock]#客户端连接时，会生成tcp_sock的监听，返回值
#当客户端发送数据时会产生connfd的监听，返回值
wlist=[]
xlist=[]
while True:
    rs,ws,xs=select(rlist,wlist,xlist) #每次连接和发送信息都会产生监听
    for r in rs:
        if r is tcp_sock:
            connfd,addr=tcp_sock.accept()#如果tcp_sock准备就绪就创建connfd
            print("connect from",addr)
            connfd.setblocking(False)#设置connfd非阻塞
            rlist.append(connfd)
        else:
            data=r.recv(1024) #rlist列表中有tcp_sock也会有connfd，
            #使用for在rs中循环，如果是r等于socket则在上面执行，如果r是
            #connfd则在这里执行，此时r等于connfd
            if not data:
                rlist.remove(r)
                r.close()
                continue
            print(data.decode())
            r.send(b"ok")