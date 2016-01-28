---
author: daoluan
comments: true
date: 2012-08-06 12:31:31+00:00
layout: post
slug: tcp-network-programming-02
title: 基于TCP的C/S初级网络编程2
wordpress_id: 787
categories:
- linux
tags:
- apue 学习总结
- linux
---

# 导读




<blockquote>本篇文章对[http://www.daoluan.net/blog/?p=774](http://www.daoluan.net/blog/?p=774)中的“计算器”进行改进，与大家分享。</blockquote>


上面那篇中的服务端属重复型，即一个时刻只处理一客户的请求，处理期间不搭理其他客户。此篇对上篇的“计算器”进行小小的改进——能够接受多个客户的请求。

<!-- more -->

改进细则：



	
  1. 独立bind，listen，accept，serve（即calc过程）功能模块；

	
  2. 所有错误成功提示提取至各功能模块（函数）之外，错误/成功根据各函数的返回值判断（这更符合UNIX编程风范）；

	
  3. 客户的服务过程由产生的子进程负责。


缺陷：由子进程来负责serve的部分。服务器主进程（父进程）不负责等待子进程结束，资源由内核回收（这一要非必要）。

[![](http://md.daoluan.net/images/2012/08/fork.png)](http://daoluan.net/blog/archives/787/fork)


# 上实验结果图片解解馋


服务器启动

[![](http://md.daoluan.net/images/2012/08/1_thumb1.png)](http://daoluan.net/blog/archives/787/1_thumb1)

客户端方面，将client1、client2和client3（编译链接自同一个代码）写进脚本。运行

[![](http://md.daoluan.net/images/2012/08/2_thumb1.png)](http://daoluan.net/blog/archives/787/2_thumb1)

服务端服务多个客户请求

[![](http://md.daoluan.net/images/2012/08/3_thumb1.png)](http://daoluan.net/blog/archives/787/3_thumb1)

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
    
        if((sockfd = initserver(SOCK_STREAM,(struct sockaddr *)&server,sizeof(server),1)) < 0)
        {
            printf("initserver error\n");
            return 0;
        }// if
    
    //prepare server
        while(1)
        {
            pid_t pid;
            if(pid = fork() < 0)    //  fork error
            {
                close(sockfd);
                return -1;
            }
            else if(pid == 0)
            {
                printf("serving\n");
                serve(sockfd);
                break;
            }// if
        }// while
    
    //serve
        close(sockfd);
        return 0;
    }


test.sh

    
    #!/bin/bash
    
    ./client1 1 2 +
    ./client2 2 3 +
    ./client3 3 4 +


本文完 2012-08-06

捣乱小子 [http://www.daoluan.net/blog/](http://www.daoluan.net/blog/)
