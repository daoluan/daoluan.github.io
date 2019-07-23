---
title: 初探libevent网络库
date: 2012-09-25 14:43:10 Z
categories:
- cplusplus
- linux
tags:
- GTD项目实录
- libevent
author: daoluan
comments: true
layout: post
wordpress_id: 1089
---

libevent官网：[http://libevent.org/](http://libevent.org/)

libevent是基于消息事件的网络库。当指定一个文件描述符（可以是socket fd）可读事件或可写事件的时候，libevent API提供执行回调函数的机制。再者，libevent也提供信号或超时的回调。libevent用事件来驱动网络服务。一个应用只需要调用event_dispathc()函数并且在不修改事件驱动的情况下动态添加或者删除事件。libevent支持很多系统，诸如熟悉的Linux，Windows。

但libevent不提供线程安全保障，每一个现场都必须初始化一个event_base。当然，可以对libevent进行拓展，通过每一个现场都初始化一个event_base，又或者通过加锁来访问全局共享的event_base。

<!-- more -->

一个简单的基于tcp协议的服务器，比如接下来给出的echo服务器，通过libevent可以很容易实现单线程，非阻塞IO模型。



	
  * 声明并定义套接字可读/可写/出错回调函数，在符合条件的情况，会触发调用相应的函数。

	
  * 准备监听套接字绑定并开始监听。

	
  * 设置接受连接（accept）事件并加入时间驱动中。


下面给出示例程序。

    
    #include <event.h>
    #include <sys/types.h>
    #include <sys/socket.h>
    #include <netinet/in.h>
    #include <arpa/inet.h>
    #include <string.h>
    #include <stdlib.h>
    #include <fcntl.h>
    #include <unistd.h>
    
    #define SERVER_PORT 8080
    int debug = 0;
    
    struct client
    {
    	int fd;
    	struct bufferevent * buf_ev;
    };
    
    int setnonblock(int fd)
    {
    	int flags;
    
    	flags = fcntl(fd,F_GETFL);
    	flags |= O_NONBLOCK;
    	fcntl(fd,F_SETFL,flags);
    }
    
    /*read callback function .*/
    void buf_read_callback(struct bufferevent *incoming,
    					   void *arg)
    {
    	printf("this is called in buf_read_callback\n");
    	struct evbuffer * evreturn;
    	char *req;
    
    	req = evbuffer_readline(incoming->input);
    
    	printf("req is %s\n",req);
    	if(req == NULL)
    		return;
    
    	evreturn = evbuffer_new();
    	evbuffer_add_printf(evreturn,"YOU SAID %s\n",req);
    	bufferevent_write_buffer(incoming,evreturn);
    	evbuffer_free(evreturn);
    	free(req);
    }
    
    /*write callback function.*/
    void buf_write_callback(struct bufferevent *bev,
    						void *arg)
    {
    	printf("this is called in buf_write_callback\n");
    }
    
    /*error callback function.*/
    void buf_error_callback(struct bufferevent *bev,    
    						short what,void *arg)
    {
    	struct client *client = (struct client*)arg;
    	bufferevent_free(client->buf_ev);
    	close(client->fd);
    	free(client);
    }
    
    /*accept callback function.*/
    void accept_callback(int fd,
    					 short ev,void *arg)
    {
    	int client_fd;
    	struct sockaddr_in client_addr;
    	socklen_t client_len = sizeof(client_addr);
    	struct client *client;
    
    	client_fd = accept(fd,
    		(struct sockaddr*)&client_addr,
    		&client_len);
    
    	if(client_fd < 0)
    	{
    		printf("Client:accept() faild\n");
    		return;
    	}
    
    	/*set socket fd to none block.*/
    	setnonblock(client_fd);
    
    	/*new a struct client.*/
    	client = calloc(1,sizeof(*client));
    	if(client == NULL)
    	{
    		printf("calloc error\n");
    		return;
    	}// if
    	client->fd = client_fd;
    
    	client->buf_ev = bufferevent_new(client_fd,
    		buf_read_callback,
    		buf_write_callback,
    		buf_error_callback,
    		client);
    
    	bufferevent_enable(client->buf_ev,EV_READ);
    }
    
    int main(int argc,
    		 char **argv)
    {
    	int socketlisten;
    	struct sockaddr_in addresslisten;
    	struct event accept_event;
    	int reuse = 1;
    
    	/*initialize the event_base in this thread and if this is single-thread application,there is no need for saving the event_base.*/
    	event_init();
    
    	socketlisten = socket(AF_INET, SOCK_STREAM, 0);
    
    	if (socketlisten < 0)
    	{
    		fprintf(stderr,"Failed to create listen socket");
    		return 1;
    	}
    
    	memset(&addresslisten, 0, sizeof(addresslisten));
    
    	addresslisten.sin_family = AF_INET;
    	addresslisten.sin_addr.s_addr = INADDR_ANY;
    	addresslisten.sin_port = htons(SERVER_PORT);
    
    	if (bind(socketlisten,
    		(struct sockaddr *)&addresslisten,
    		sizeof(addresslisten)) < 0)
    	{
    		fprintf(stderr,"Failed to bind");
    		return 1;
    	}
    
    	if (listen(socketlisten, 5) < 0)
    	{
    		fprintf(stderr,"Failed to listen to socket");
    		return 1;
    	}
    
    	setsockopt(socketlisten,
    		SOL_SOCKET,
    		SO_REUSEADDR,
    		&reuse,
    		sizeof(reuse));
    
    	setnonblock(socketlisten);
    
    	/*set accept callback function including read/write/error callback function.
    	  EV_READ:Wait for a socket or FD to become readable  
    	  EV_WRITE:Wait for a socket or FD to become writeable 
    	*/
    	event_set(&accept_event,
    		socketlisten,
    		EV_READ|EV_PERSIST,
    		accept_callback,
    		NULL);
    
    	/*add an event to the set of pending events.*/
    	event_add(&accept_event,
    		NULL);
    
    	/*Loop to process events.*/
    	event_dispatch();
    
    	close(socketlisten);
    	return 0;
    }


用telnet测试echo服务器。在使用telnet的时候指明IP地址和端口号便可以连接相应的服务程序。

服务端：

    
    daoluan@daoluan:~$ telnet 192.168.128.99 8080


客户端：

    
    root@daoluan:~# telnet 192.168.128.99 8080
    Trying 192.168.128.99...
    Connected to 192.168.128.99.
    Escape character is '^]'.
    hello world.
    YOU SAID hello world.


libevent的事件驱动机制是在是太妙了，应该是借助了系统的信号处理功能，当检测可读或者可写的时候，通知并调用事先注册好的回调函数。当然libevent没有那么简单！YY下，既然每个线程都必须有唯一的event_base，那么多线程就需要多个event_base，这又存在很多线程间通信的问题，数据同步等等。但如果说一个工作线程服务一个客户连接的话，即可能不存在线程间的数据同步等问题，那么用libevent实现多线程思路也不会太复杂。

而上述的echo是重复型服务器，而非并发型服务器。所以当多个连接请求时，只能“先到先服务”。

下面是有用的链接：



	
  * [http://www.wangafu.net/~nickm/libevent-2.0/doxygen/html/index.html](http://www.wangafu.net/~nickm/libevent-2.0/doxygen/html/index.html)

	
  * [http://www.csdn.net/article/2011-02-11/291656](http://www.csdn.net/article/2011-02-11/291656)

	
  * [http://www.cnblogs.com/Seapeak/archive/2010/04/08/1707807.html](http://www.cnblogs.com/Seapeak/archive/2010/04/08/1707807.html)

	
  * [http://gonggeng.org/mediawiki/index.php/Libevent-bufferevent](http://gonggeng.org/mediawiki/index.php/Libevent-bufferevent)


本文完 2012-09-25

捣乱小子 [http://www.daoluan.net/](http://www.daoluan.net/blog/)
