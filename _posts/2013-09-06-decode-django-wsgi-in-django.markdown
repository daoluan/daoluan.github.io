---
title: 'Django 源码小剖: Django 中的 WSGI'
date: 2013-09-06 14:08:36 Z
categories:
- 学习总结
tags:
- Django
- 源代码
author: daoluan
comments: true
layout: post
wordpress_id: 1944
---

Django 其内部已经自带了一个方便本地测试的小服务器, 所以在刚开始学习 Django 的时候并不需搭建 apache 或者 nginx 服务器. Django 自带的服务器基于 python wsgiref 模块实现的, 其百分之七八十的代码都是 wsgiref 中的代码, 只重写了一部分, 所以 Django 自带的服务器测试写个 helloworld 就好了.

Django 内置服务器在 django.core.servers 和 django.core.handlers, 这两者共同来实现.先看看 django.core.servers. 下面是目录结构:

E:\DECODE-DJANGO\DJANGO-1.5.1\DJANGO\CORE\SERVERS
basehttp.py 重写 ServerHandler,WSGIServer,WSGIRequestHandler,定义 run() 函数
fastcgi.py
__init__.py

下面的代码足以说明「百分之七八十」:


    class ServerHandler(simple_server.ServerHandler, object):
    ...
    class WSGIServer(simple_server.WSGIServer, object):
    ...
    class WSGIRequestHandler(simple_server.WSGIRequestHandler, object):


具体内部做了一些变更:




  * 重写了 write 函数, 当传输数据过大的时候分段传输


  * 多了一些异常处理


  * 错误记录


都是无关痛痒, 不详细展开了.这里定义了一个很有意思的函数 run():


    def run(addr, port, wsgi_handler, ipv6=False, threading=False):
        server_address = (addr, port)

        if threading:
            httpd_cls = type(str('WSGIServer'), (socketserver.ThreadingMixIn, WSGIServer), {})
        else:
            httpd_cls = WSGIServer

        httpd = httpd_cls(server_address, WSGIRequestHandler, ipv6=ipv6)
        httpd.set_app(wsgi_handler)
        httpd.serve_forever() 永久运行


这和上一篇 if __name__ == '__main__': 中的代码效果类似, 实例化服务器类, 让它跑起来. 在 run() 函数中可以根据喜好配置:

add: 地址, 可传入 ip 地址, 一般是 127.0.0.1

port: 端口, 自定义端口

wsgi_handler: 上节提到的 application, 在 django.core.handlers 中定义

ipv6: 如果为 true, 会将协议地址族换成是 AF_INET6

threading: 如果为 true, 服务器会被强制成 type(str('WSGIServer'), (socketserver.ThreadingMixIn, WSGIServer), {})(这个我漏讲了, 但功能是这样), 能处理多线程处理请求.

所以, 调用这个函数可以让一个自定义服务器跑起来.

wsgi_handler 参数定义了 application, 而 application 必须是一个 start_response(status, response_headers, exc_info=None) 形式的函数或者定义了 __call__ 的类. 而 django.core.handlers 就用后一种方式实现了 application.

E:\DECODE-DJANGO\DJANGO-1.5.1\DJANGO\CORE\HANDLERS
base.py application 的基类 BaseHandler
wsgi.py 实现 WSGIHandler 类, 定义了 __call__, 这样就名正言顺的 WSGI 中的 application 了
__init__.py

事实上, 在 WSGI 中除了 application,server 外, 还有一个 middleware, 名曰中间件. 在上一篇中故意漏了, 因为没有涉及到.最后我疏离一下上边提到的类模块等等, 方便大家找源码, 整理如下:


<blockquote><p>C:\PYTHON27\LIB\WSGIREF<br>
handlers.py 定义了 BaseHandler,&nbsp;SimpleHandler 类<br>
headers.py<br>
simple_server.py&nbsp;定义了&nbsp;ServerHandler,&nbsp;WSGIRequestHandler 类, demo_app(), make_server()<br>
util.py<br>
validate.py<br>
__init__.py</p>
<p>E:\DECODE-DJANGO\DJANGO-1.5.1\DJANGO\CORE\SERVERS<br>
basehttp.py 重写 ServerHandler,WSGIServer,WSGIRequestHandler,定义 run() 函数<br>
fastcgi.py<br>
__init__.py</p>
<p>E:\DECODE-DJANGO\DJANGO-1.5.1\DJANGO\CORE\HANDLERS<br>
base.py application 的基类 BaseHandler<br>
wsgi.py 实现&nbsp;WSGIHandler 类, 定义了 __call__, 这样就名正言顺的 WSGI 中的 application 了<br>
__init__.py</p></blockquote>


ps: 目录根据实际情况会不同, 看具体情况.我已经在 github 备份了 Django 源码的注释: [Decode-Django](https://github.com/daoluan/Decode-Django), 有兴趣的童鞋 fork 吧.

Dylan  2013-9-6

[http://daoluan.net](http://daoluan.net/)
