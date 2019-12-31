---
title: 基于TCP的C/S初级网络编程1
date: 2012-08-02 13:15:43 Z
categories:
- linux
tags:
- apue 学习总结
- linux
author: daoluan
comments: true
layout: post
wordpress_id: 774
---

# 导读




<blockquote>本篇实现C/S架构的“计算器”，与大家分享。</blockquote>


看了会网络编程，便不自觉YY了下：实现一个简单的计算器，客户端给出简单的运算，服务端负责运算。这一小项目做起来很有意思，而且难度不大，所以推荐初学者试着去做做。下面分享在实现上述“计算器”的过程。

简单的基于tcp协议的 C/S编程都离不开这几个函数：


<blockquote><p>服务端：socket,bind,listen,accept,recv,send<br>
客户端：socket,connect,recv,send</p></blockquote>


<!-- more -->

因为“计算器”还设计涉及客户端的阻塞（因为客户端提交了运算要求过后，服务端可能要等会才能回送计算结果，这时要求客户端阻塞等候），所以涉及select函数。select函数用途广泛，很容易实现阻塞功能。介绍一个文档，有兴趣可以参考一下：[http://wenku.baidu.com/view/0ea86ffdc8d376eeaeaa3198.html](http://wenku.baidu.com/view/0ea86ffdc8d376eeaeaa3198.html)


# 客观测试环境


可以在一个主机上同时进行服务端和客户端的测试，只要客户在connect的时候用回环地址（或者本地静态IP地址）连接服务端就可以。


# 实现细节


socket不成功怎么办，bind不成功怎么办，listen不成功怎么办...都有相应的出错处理，编程过程中养成这种“考虑周细”的习惯（考虑所有的情况，比如出错的时候打印错误信息），对调试很有帮助。

[http://www.gnu.org/software/libc/manual/html_node/Internet-Address-Formats.html](http://www.gnu.org/software/libc/manual/html_node/Internet-Address-Formats.html)


<blockquote><p>— Data Type: <strong>struct sockaddr_in</strong><var><a name="index-struct-sockaddr_005fin-1685"></a></var></p>
<p>This is the data type used to represent socket addresses in the Internet namespace. It has the following members:</p>
<dl>
<dt><code>sa_family_t sin_family</code></dt>
<dd>This identifies the address family or format of the socket address. You should store the value <code>AF_INET</code> in this member. See <a href="http://www.gnu.org/software/libc/manual/html_node/Socket-Addresses.html#Socket-Addresses">Socket Addresses</a>.</dd>
<dt><code>struct in_addr sin_addr</code></dt>
<dd>This is the Internet address of the host machine. See <a href="http://www.gnu.org/software/libc/manual/html_node/Host-Addresses.html#Host-Addresses">Host Addresses</a>, and <a href="http://www.gnu.org/software/libc/manual/html_node/Host-Names.html#Host-Names">Host Names</a>, for how to get a value to store here.</dd>
<dt><code>unsigned short int sin_port</code></dt>
<dd>This is the port number. See <a href="http://www.gnu.org/software/libc/manual/html_node/Ports.html#Ports">Ports</a>.</dd>
</dl>
</blockquote>


注：sockaddr_in此类型数据在使用之前请务必bzero

其中sin_addr是结构体，

[http://www.gnu.org/software/libc/manual/html_node/Host-Address-Data-Type.html](http://www.gnu.org/software/libc/manual/html_node/Host-Address-Data-Type.html)


<blockquote><p>— Data Type: <strong>struct in_addr</strong><var><a name="index-struct-in_005faddr-1694"></a></var></p>
<p>This data type is used in certain contexts to contain an IPv4 Internet host address. It has just one field, named <code>s_addr</code>, which records the host address number as an <code>uint32_t</code>.</p></blockquote>


inet_pton和inet—_ntop方便点分十进制IP地址字符串和uint32_t（IP地址是4字节，应为网络字节序）的转换。


# select


如上所述要求，“因为客户端提交了运算要求过后，服务端可能要等会才能回送计算结果，这时要求客户端阻塞等候”，select经常扮演阻塞的角色。
[http://www.gnu.org/software/libc/manual/html_node/Waiting-for-I_002fO.html（文档很详细）](http://www.gnu.org/software/libc/manual/html_node/Waiting-for-I_002fO.html（文档很详细）)
因此客户端提交运算要求之后，需要将其socket读功能阻塞，直到有数据（即服务端回送的结果）时才进行读取。如果用轮询的方法，很浪费CPU。


# 上实验结果图片解解馋


服务器启动

[![1_thumb.png](http://daoluan.net/images/blog/2012/08/1_thumb.png)](http://daoluan.net/images/blog/2012/08/1_thumb.png)

客户端启动，太快了，结果都出来了

[![2_thumb.png](http://daoluan.net/images/blog/2012/08/2_thumb.png)](http://daoluan.net/images/blog/2012/08/2_thumb.png)

服务器处理结束，退出

[![3_thumb.png](http://daoluan.net/images/blog/2012/08/3_thumb.png)](http://daoluan.net/images/blog/2012/08/3_thumb.png)

计算器要求：客户需要传递后缀表达式简单运算（如上图），服务器直接运行就即可。
缺陷：此计算器只服务于一个客户，其他不给予处理；此计算器进一步改进可以实现接受不只一个客户的请求。

client


    #include <stdio.h>
    #include <unistd.h>
    #include <sys/socket.h>
    #include <netinet/in.h>
    #include <netinet/ip.h>
    #include <arpa/inet.h>
    #include <string.h>
    #include <string.h>

    #define MAXSLEEP 1024

    int connect_retry(int sockfd,const struct sockaddr * addr,socklen_t alen)
    {
        int nsec;

        printf("connecting\n");
        for(nsec = 1; nsec <= MAXSLEEP; nsec<<=1)
        {
            if(connect(sockfd,addr,alen) == 0)
            {
                printf("connected\n");
                return 0;
            }// if
            if(nsec <= MAXSLEEP/2)//    delay
                sleep(nsec);
        }// for:
        return 0;
    }

    int main(int argc,char * argv[])
    {
        if(argc != 4)
        {
            printf("you must input 4 arg\n");
            return 1;
        }// if

        int fd;
        struct sockaddr_in si,server;
        char addr[20],buf[20],bufrecv[20];

        bzero(bufrecv,sizeof(bufrecv));
        sprintf(addr,"127.0.0.1");

        fd = socket(AF_INET,SOCK_STREAM,0);//   create socker fd;
        printf("socket ok\n");

    //prepare server addr
        bzero(&server,sizeof(server));
        server.sin_family = AF_INET;
        server.sin_port = htons(6000);
        inet_pton(AF_INET,addr,(void *)&server.sin_addr);
        printf("server ok\n");

    //prepare request data
        bzero(buf,sizeof(buf));
        sprintf(buf,"%c%c%c",argv[1][0],argv[2][0],argv[3][0]);

    //connect
        if(connect_retry(fd,(struct sockaddr *)&server,sizeof(server)) < 0)
        {
            printf("connect error\n");
            return 1;
        }// if

    //send
        if(send(fd,buf,20,0) < 0)
        {
            printf("client send error\n");
            return 1;
        }// if

    //select
        fd_set readfd;
        FD_ZERO(&readfd);
        FD_SET(fd,&readfd);
        int t;

        if((t = select(FD_SETSIZE,&readfd,NULL,NULL,NULL)) < 0)
        {
            printf("select error\n");
            return 1;
        }// if

    //recv
        bzero(bufrecv,sizeof(bufrecv));
        recv(fd,bufrecv,20,0);
        printf("%s\n",bufrecv);

        close(fd);
        return 0;
    }


server


    #include <stdio.h>
    #include <sys/socket.h>
    #include <netinet/in.h>
    #include <errno.h>
    #include <ctype.h>
    #include <arpa/inet.h>
    #include <unistd.h>
    #include <string.h>

    char bufret[20];

    int initserver(int type,const struct sockaddr * addr,socklen_t alen,int qlen)
    {
        int fd;
        int err = 0;

        if((fd = socket(addr->sa_family,type,0)) < 0)
            return -1;

        printf("binding\n");
        if(bind(fd,addr,alen) < 0)
        {
            err = errno;
            goto errout;
        }// if
        printf("bind succeed \n");

        if(type == SOCK_STREAM || type == SOCK_SEQPACKET)
        {
            printf("listening\n");
            if(listen(fd,1) < 0)
            {
                err = errno;
                printf("listen error\n");
                goto errout;
            }// if
        }// if
        printf("listened \n");
        return (fd);

    errout:
        close(fd);
        errno = err;
        return -1;
    }

    int serve(int sockfd)
    {
        int a,b;
        char op,buf[25];

        int ret,addrlen = sizeof(struct sockaddr_in),clfd;
        struct sockaddr_in client;

        bzero(&client,sizeof(client));

    //accept
        printf("accepting\n");
        clfd = accept(sockfd,(struct sockaddr *)&client,&addrlen);

    //recv
        printf("accepted\n");
        bzero(buf,sizeof(buf));
        recv(clfd,buf,20,0);
        printf("recived\n");

    //calculate
        a = buf[0] - '0';
        b = buf[1] - '0';
        op = buf[2];

        switch(op)
        {
            case '+':ret = a + b;break;
            case '-':ret = a - b;break;
            case '*':ret = a * b;break;
            case '/':ret = a / b;break;
        }// switch

        sprintf(bufret,"the result:%d",ret);

    //send
        printf("sending\n");
        if(send(clfd,bufret,20,0) < 0)
        {
            printf("server send error\n");
            return -1;
        }// if
        printf("sended,server end\n");
        return 0;
    }

    int main(int argc,char * argv[])
    {
        int sockfd;
        char addr[20];

        bzero(addr,sizeof(addr));
        sprintf(addr,"127.0.0.1");

        struct sockaddr_in server;
        bzero(&server,sizeof(server));
        server.sin_family = AF_INET;
        server.sin_port = htons(6000);
        //server.sin_addr.s_addr = htonl(INADDR_ANY);
        inet_pton(AF_INET,addr,(void *)&server.sin_addr);

    //prepare server
        if((sockfd = initserver(SOCK_STREAM,(struct sockaddr *)&server,sizeof(server),1)) < 0)
        {
            printf("initserver error\n");
            return 0;
        }// if

        printf("serving\n");

    //serve
        serve(sockfd);
        close(sockfd);
        return 0;
    }


以上纯属笔者YY后的作品，还存在很多的缺陷与不足；抛砖引玉，与广大朋友分享。欢迎创意建议提议。另，如有错误，欢迎斧正。

本文完 2012-08-02

Dylan [http://www.daoluan.net/blog/](http://www.daoluan.net/blog/)
