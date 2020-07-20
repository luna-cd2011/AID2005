2020年7月16日 day16

"""
2020年7月14日 ftp作业
"""
"""
ftp 文件服务 服务端
多线程并发模型训练
"""
from socket import *
from threading import Thread
import os, time

# 全局变量
HOST = '0.0.0.0'
PORT = 8888
ADDR = (HOST, PORT)  # 服务器地址

# 文件库
FTP = "/home/tarena/FTP/"


# 处理客户端请求
class FTPServer(Thread):
    def __init__(self, connfd):
        super().__init__()
        self.connfd = connfd

    def do_list(self):
        # 判断文件库是否为空
        file_list = os.listdir(FTP)
        if not file_list:
            self.connfd.send(b'FAIL')  # 列表为空
            return
        else:
            self.connfd.send(b'OK')
            time.sleep(0.1)
            data = "\n".join(file_list)
            self.connfd.send(data.encode())

    # 处理下载
    def do_get(self, filename):
        try:
            f = open(FTP + filename, 'rb')
        except:
            # 文件不存在报异常
            self.connfd.send(b"FAIL")
            return
        else:
            # 文件打开成功
            self.connfd.send(b"OK")
            time.sleep(0.1)
            # 发送文件
            while True:
                data = f.read(1024)
                if not data:
                    time.sleep(0.1)
                    self.connfd.send(b"##")  # 文件发送完毕
                    break
                self.connfd.send(data)
            f.close()

    # 处理上传
    def do_put(self, filename):
        if os.path.exists(FTP + filename):
            self.connfd.send(b"FAIL")
            return
        else:
            self.connfd.send(b"OK")
            # 接收文件
            f = open(FTP + filename, 'wb')
            while True:
                data = self.connfd.recv(1024)
                if data == b"##":
                    break
                f.write(data)
            f.close()

    # 作为一个线程内容处理某一个客户端的请求
    def run(self):
        # 总分模式
        while True:
            # 某个客户端所有的请求
            data = self.connfd.recv(1024).decode()
            print("Request:", data)  # 调试
            # 更具不同的请求做不同处理
            if not data or data == 'EXIT':
                self.connfd.close()
                return
            elif data == 'LIST':
                self.do_list()
            elif data[:4] == 'RETR':
                filename = data.split(' ')[-1]
                self.do_get(filename)
            elif data[:4] == 'STOR':
                filename = data.split(' ')[-1]
                self.do_put(filename)


def main():
    # tcp套接字创建
    sock = socket()
    sock.bind(ADDR)
    sock.listen(5)
    print("Listen the port %s" % PORT)

    # 循环连接客户端
    while True:
        try:
            connfd, addr = sock.accept()
            print("Connect from", addr)
        except KeyboardInterrupt:
            sock.close()
            return
        # 为连接进来的客户端创建单独的线程
        t = FTPServer(connfd)  # 使用自定义线程类创建线程
        t.setDaemon(True)  # 主线程退出，分之线程终止服务
        t.start()


if __name__ == '__main__':
    main()
"""
ftp文件服务-客户端
"""
from socket import *
import time
import sys

# 服务端地址
ADDR = ("127.0.0.1", 8888)


# 实现具体的请求功能
class FTPClient:
    def __init__(self, sock):
        self.sock = sock

    def do_list(self):
        self.sock.send(b"LIST")  # 发送请求
        result = self.sock.recv(128).decode()  # 回复 字符串
        # 根据回复分情况讨论
        if result == 'OK':
            # 接收文件列表
            file = self.sock.recv(1024 * 1024).decode()
            print(file)
        else:
            print("文件库为空")

    # 下载文件
    def do_get(self, filename):
        data = "RETR " + filename
        self.sock.send(data.encode())  # 发送请求
        # 等回复
        result = self.sock.recv(128).decode()
        if result == 'OK':
            # 接收文件
            f = open(filename, 'wb')
            while True:
                data = self.sock.recv(1024)
                if data == b"##":
                    break
                f.write(data)
            f.close()
        else:
            print("文件不存在")

    # 上传文件
    def do_put(self, filename):
        # 本地判断，防止文件路径写错
        try:
            f = open(filename, 'rb')
        except:
            print("该文件不存在")
            return
        # 上传 put 后可能是路径/home/tarena/abc,提取真正的文件名
        filename = filename.split('/')[-1]

        data = "STOR " + filename
        self.sock.send(data.encode())  # 发送请求
        # 等回复
        result = self.sock.recv(128).decode()
        if result == 'OK':
            # 发送文件
            while True:
                data = f.read(1024)
                if not data:
                    time.sleep(0.1)
                    self.sock.send(b"##")  # 文件发送完毕
                    break
                self.sock.send(data)
            f.close()
        else:
            print("文件已经存在")

    # 退出
    def do_exit(self):
        self.sock.send(b"EXIT")
        self.sock.close()
        sys.exit("谢谢使用")


def main():
    # 创建套接字
    sock = socket()
    sock.connect(ADDR)

    # 实例化功能类对象
    ftp = FTPClient(sock)

    while True:
        print("============ 命令选项==============")
        print("***           list           ***")
        print("***         get  file        ***")
        print("***         put  file        ***")
        print("***           exit           ***")
        print("==================================")

        cmd = input("请输入命令:")
        if cmd == "list":
            ftp.do_list()
        elif cmd[:3] == "get":
            filename = cmd.split(' ')[-1]  # 提取文件名
            ftp.do_get(filename)
        elif cmd[:3] == "put":
            filename = cmd.split(' ')[-1]  # 提取文件名
            ftp.do_put(filename)
        elif cmd == "exit":
            ftp.do_exit()
        else:
            print("请输入正确命令")


if __name__ == '__main__':
    main()


"""
IO 阻塞
"""
"""
非阻塞IO
套接字对象 --》 非阻塞
设置套接字非阻塞
1.通过修改IO属性行为，使原本阻塞的IO变为非阻塞的状态
套接字.setblocking(False) 
try。。
except BlockingIOError as e: 捕获BlockingIOError错误
----------------------------------------------------------
2.超时检测 ：设置一个最长阻塞时间，超过该时间后则不再阻塞等待
套接字.settimeout(3)
except timeout as e: 捕获timeout错误
"""
from socket import *
import time

# 打开日志文件
f = open("date.txt",'a+')

# 创建tcp套接字
sockfd = socket()
sockfd.bind(('0.0.0.0',8888))
sockfd.listen(5)

# 设置套接字的非阻塞
sockfd.setblocking(False)

# sockfd.settimeout(3)
while True:
    print("Waiting for connect")
    try:
        connfd,addr = sockfd.accept() # 阻塞等待
        print("Connect from",addr)
    except BlockingIOError as e:
        # 干点别的事
        msg = "%s : %s\n"%(time.ctime(),e)
        f.write(msg)
        time.sleep(2)
    except timeout as e:
        # 干点别的事
        msg = "%s : %s\n"%(time.ctime(),e)
        f.write(msg)
        time.sleep(2)

    else:
        # 正常有客户端连接
        data = connfd.recv(1024)
        print(data.decode())
#===================================================
# IO多路复用
# 同时监控多个IO事件，当哪个IO事件准备就绪就执行哪个IO事件。以
# 此形成可以同时处理多个IO的行为，避免一个IO阻塞造成其他IO均无法执行，提高了IO执行效率。
select 方法
"""
rs, ws, xs=select(rlist, wlist, xlist[, timeout])
功能: 监控IO事件，阻塞等待IO发生
参数：rlist  列表  读IO列表，添加等待发生的或者可读的IO事件
      wlist  列表  写IO列表，存放要可以主动处理的或者可写的IO事件
      xlist  列表 异常IO列表，存放出现异常要处理的IO事件
      timeout  超时时间

返回值： rs 列表  rlist中准备就绪的IO
        ws 列表  wlist中准备就绪的IO
	   xs 列表  xlist中准备就绪的IO
"""
from socket import *
from select import  select
from time import sleep

f=open("my.log","rb")

tcp_sock=socket()
tcp_sock.bind(("0.0.0.0",8888))
tcp_sock.listen(5)
connfd,addr=tcp_sock.accept()

udp_sock=socket(AF_INET,SOCK_DGRAM)
udp_sock.bind(("0.0.0.0",8866))
print("监控IO")
sleep(5)
rs,ws,xs=select([tcp_sock],[f,udp_sock,connfd],[])
print("rs",rs)
print("ws",ws)
print("xs",xs)
# 返回结果：
#rs []
# ws [<_io.BufferedReader name='my.log'>,
# <socket.socket fd=6, family=AddressFamily.AF_INET, type=SocketKin
# ---d.SOCK_DGRAM, proto=0, laddr=('0.0.0.0', 8866)>,
# <socket.socket fd=5, family=AddressFamily.AF_INET, type=SocketKind
# ---.SOCK_STREAM, proto=0, laddr=('127.0.0.1', 8888), raddr=('127.0.0.1'
# , 56214)>]
# xs []
"""
select 的IO并发模型
服务端
"""
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
"""
客户端
"""
"""
tcp循环模型客户端1
重点代码
"""

from socket import *
# 创建tcp套接字
tcp_socket = socket()
# 发起连接 连接服务端
tcp_socket.connect(("127.0.0.1",8889))
# 发送消息
while True:
    msg = input(">>")
    if not msg:
        break
    tcp_socket.send(msg.encode()) # 发送字节串
    data = tcp_socket.recv(1024)
    print(data.decode())
tcp_socket.close()

"""
poll io 多路复用
"""

from socket import *
from select import *
from time import sleep

# 创建三个对象，帮助监控
tcp_sock = socket()
tcp_sock.bind(('0.0.0.0',8888))
tcp_sock.listen(5)

udp_sock = socket(AF_INET,SOCK_DGRAM)
udp_sock.bind(('0.0.0.0',8866))

f = open("my.log",'rb')

# 开始监控这些IO
print("监控IO发生")

p = poll()
# 关注
p.register(tcp_sock,POLLIN)
p.register(f,POLLOUT)
p.register(udp_sock,POLLOUT|POLLIN)

print("tcp_sock:",tcp_sock.fileno())
print("udp_sock:",udp_sock.fileno())
print("file:",f.fileno())

# 准备工作
map = {
       tcp_sock.fileno():tcp_sock,
       udp_sock.fileno():udp_sock,
       f.fileno():f
       }

events = p.poll() # 进行监控
print(events)

p.unregister(f) # 取消关注

"""
基于epoll方法实现IO并发
重点代码 !
"""

from socket import *
from select import *

# 全局变量
HOST = "0.0.0.0"
PORT = 8889
ADDR = (HOST,PORT)

# 创建tcp套接字
tcp_socket = socket()
tcp_socket.bind(ADDR)
tcp_socket.listen(5)

# 设置为非阻塞
tcp_socket.setblocking(False)

p = epoll() # 建立epoll对象
p.register(tcp_socket,EPOLLIN) # 初始监听对象

# 准备工作，建立文件描述符 和 IO对象对应的字典  时刻与register的IO一致
map = {tcp_socket.fileno():tcp_socket}

# 循环监听
while True:
    # 对关注的IO进行监控
    events = p.poll()
    # events--> [(fileno,event),()....]
    for fd,event in events:
        # 分情况讨论
        if fd == tcp_socket.fileno():
            # 处理客户端连接
            connfd, addr = map[fd].accept()
            print("Connect from", addr)
            connfd.setblocking(False) # 设置非阻塞
            p.register(connfd,EPOLLIN|EPOLLERR) # 添加到监控
            map[connfd.fileno()] = connfd # 同时维护字典
        elif event & EPOLLIN: #包含EPOLLIN
            # 收消息
            data = map[fd].recv(1024)
            if not data:
                # 客户端退出
                p.unregister(fd) # 移除关注
                map[fd].close()
                del map[fd] # 从字典也移除
                continue
            print(data.decode())
            map[fd].send(b'OK')







