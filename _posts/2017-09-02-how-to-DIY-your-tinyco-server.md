---
title: 如何使用 tinyco 定制你的服务
date: 2017-09-02 00:00:00 Z
categories:
- 编程小记
tags:
- tinyco
author: daoluan
layout: post
---

业务逻辑服务所做的事情可以总结为：在某个绑定端口上收到请求，需要做什么？如果需要使用 tinyco 实现业务服务，可细化为三个步骤：

1. 告诉 tinyco 绑定什么端口，使用什么协议（tcp、udp）
2. 实现业务逻辑类
3. 业务逻辑安装。当在某个端口收到请求后，需要执行哪个业务逻辑类

下面的这个配置文件，tinyco 将会在 eth1 这个地址上绑定 8080这个端口，tcp协议。

    {
      "tcp": [
        {
          "listen": "eth1:8080"
        }
      ]
    }

如果想使用 http服务，可以使用 tinyco 自带的 http业务逻辑基类：

    class MyHttpReqWork : public http::HttpSrvWork {
    public:
      virtual int Serve() {
        LOG("ready to reply");
        hrsp_.SetStatus(200);
        hrsp_.SetContent("hello world!");
        Reply();
        return 0;
      }
    };

上面是简单收到包后响应 http 200 的例子。

之后，你需要告诉 tinyco server，当在端口 8080上收到 http请求后，需要使用哪个业务逻辑类，因为你可能有多个 http 业务逻辑类实现，MyHttpReqWorkX, MyHttpReqWorkY...

这里只需要继承 Server类，并实现安装函数并返回需要的逻辑类就好了。

    class MyServer : public ServerImpl {
    public:
      virtual TcpReqWork *BuildStreamBusinessWork(uint32_t port) {
        LOG("my work builder: %d", port);
        if (8080 == port) return new MyHttpReqWork();
        return NULL;
      }
    };

最后 main 中 new 一个 MyServer，服务即可以跑起来了。

    int main() {
      std::shared_ptr<MyServer> srv(new MyServer);
      if (srv->Initialize() < 0) {
        LOG_ERROR("fail to initialize server");
        return -1;
      }
      srv->Run();
      return 0;
    }

以上简单的几个步骤，即可定制业务服务。