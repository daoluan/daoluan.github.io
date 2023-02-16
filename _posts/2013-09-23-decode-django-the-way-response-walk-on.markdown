---
title: 'Django 源码小剖: 响应数据 response 的返回'
date: 2013-09-23 15:02:55 Z
categories:
- 学习总结
tags:
- Django
- 源代码
author: daoluan
comments: true
layout: post
wordpress_id: 2010
---

### 响应数据的返回


在 WSGIHandler.__call__(self, environ, start_response) 方法调用了 WSGIHandler.get_response() 方法, 由此得到响应数据对象 response. 如今所要做的, 便是将其返回给客户端. 在 [Django 源码小剖: 初探 WSGI](http://daoluan.github.io/blog/decode-django-wsgi/) 中, 简要的概括了请求到来时 django 自带服务器的执行关系, 摘抄如下:


<blockquote>
<ul>
<li>make_server() 中 WSGIServer 类已经作为服务器类, 负责接收请求, 调用 application 的处理, 返回相应;</li>
<li>WSGIRequestHandler 作为请求处理类, 并已经配置在 WSGIServer 中;</li>
<li>接着还设置了 WSGIServer.application 属性(set_app(app));</li>
<li>返回 server 实例.</li>
<li>接着打开浏览器, 即发起请求. 服务器实例 WSGIServer httpd 调用自身 handle_request() 函数处理请求. handle_request() 的工作流程如下:请求–&gt;WSGIServer 收到–&gt;调用 WSGIServer.handle_request()–&gt;调用 _handle_request_noblock()–&gt;调用 process_request()–&gt;调用 finish_request()–&gt;finish_request() 中实例化 WSGIRequestHandler–&gt;实例化过程中会调用 handle()–&gt;handle() 中实例化 ServerHandler–&gt;<strong>调用 ServerHandler.run()–&gt;run() 调用 application() 这才是真正的逻辑.–&gt;run() 中在调用 ServerHandler.finish_response() 返回数据–&gt;</strong>回到 process_request() 中调用 WSGIServer.shutdown_request() 关闭请求(其实什么也没做)</li>
</ul>
</blockquote>


事实上, WSGIServer 并没有负责将响应数据返回给客户端, 它将客户端的信息(如最重要的客户端 socket 套接字)交接给了 WSGIRequestHandler, WSGIRequestHandler 又将客户端的信息交接给了 ServerHandler, 所以 ServerHandler 产生响应数据对象后, 会直接返回给客户端.


### 代码剖析


从「调用 ServerHandler.run()-->run() 调用 application() 这才是真正的逻辑.-->run() 中在调用 ServerHandler.finish_response() 返回数据」开始说起, 下面是主要的代码解说:


    # 下面的函数都在 ServerHandler 的继承链上方法, 有些方法父类只定义了空方法, 具体逻辑交由子类实现. 有关继承链请参看: http://daoluan.github.io/blog/decode-django-wsgi/
    def run(self, application):
        """Invoke the application"""
        try:
            self.setup_environ()
            # application 在 django 中就是 WSGIHandler 类, 他实现了 __call__ 方法, 所以行为和函数一样.
            self.result = application(self.environ, self.start_response)
            self.finish_response()
        except:
            # handle error

    def finish_response(self):
        try:
            if not self.result_is_file() or not self.sendfile():
                for data in self.result:
                    # 向套接字写数据, 将数据返回给客户端
                    self.write(data)
                self.finish_content()
        finally:
            self.close()

    def write(self, data):
        """'write()' callable as specified by PEP 333"""

        # 必须是都是字符
        assert type(data) is StringType,"write() argument must be string"

        if not self.status:
            raise AssertionError("write() before start_response()")

        # 需要先发送 HTTP 头
        elif not self.headers_sent:
            # Before the first output, send the stored headers
            self.bytes_sent = len(data)    # make sure we know content-length
            self.send_headers()
        # 再发送实体
        else:
            self.bytes_sent += len(data)

        # XXX check Content-Length and truncate if too many bytes written?
        self._write(data)
        self._flush()

    def write(self, data):
        """'write()' callable as specified by PEP 3333"""

        assert isinstance(data, bytes), "write() argument must be bytestring"

        # 必须先调用 self.start_response() 设置状态码
        if not self.status:
            raise AssertionError("write() before start_response()")

        # 需要先发送 HTTP 头
        elif not self.headers_sent:
            # Before the first output, send the stored headers
            self.bytes_sent = len(data)    # make sure we know content-length
            self.send_headers()
        # 再发送实体
        else:
            self.bytes_sent += len(data)

        # XXX check Content-Length and truncate if too many bytes written? 是否需要分段发送过大的数据?

        # If data is too large, socket will choke, 窒息死掉 so write chunks no larger
        # than 32MB at a time.

        # 分片发送
        length = len(data)
        if length > 33554432:
            offset = 0
            while offset < length:
                chunk_size = min(33554432, length)
                self._write(data[offset:offset+chunk_size])
                self._flush()
                offset += chunk_size
        else:
            self._write(data)
            self._flush()

    def _write(self,data):
        # 如果是第一次调用, 则调用 stdout.write(), 理解为一个套接字对象
        self.stdout.write(data)

        # 第二次调用就是直接调用 stdout.write() 了
        self._write = self.stdout.write


接下来的事情, 就是回到 WSGIServer 关闭套接字, 清理现场, web 应用程序由此结束; 但服务器依旧在监听(WSGIServer 用 select 实现)是否有新的请求, 不展开了.


### 阶段性的总结


请求到来至数据相应的流程已经走了一遍, 包括 django 内部服务器是如何运作的, 请求到来是如何工作的, 响应数据对象是如何产生的, url 是如何调度的, views.py 中定义的方法是何时调用的, 响应数据是如何返回的...另外还提出了一个更好的 url 调度策略, 如果你有更好的方法, 不忘与大家分享.

我已经在 github 备份了 Django 源码的注释: [Decode-Django](https://github.com/daoluan/Decode-Django), 有兴趣的童鞋 fork 吧.

Dylan 2013-9-23

[http://daoluan.github.io](http://daoluan.github.io/)
