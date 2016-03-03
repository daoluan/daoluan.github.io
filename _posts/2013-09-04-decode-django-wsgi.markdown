---
author: daoluan
comments: true
date: 2013-09-04 10:42:18+00:00
layout: post
slug: decode-django-wsgi
title: 'Django 源码小剖: 初探 WSGI'
wordpress_id: 1929
categories:
- 学习总结
tags:
- Django
- 源代码
---

python 作为一种脚本语言, 已经逐渐大量用于 web 后台开发中, 而基于 python 的 web 应用程序框架也越来越多, Bottle, Django, Flask 等等.

在一个 HTTP 请求到达服务器时, 服务器接收并调用 web 应用程序解析请求, 产生响应数据并返回给服务器. 这里涉及了两个方面的东西: 服务器(server)和应用程序(application). 势必要有一个合约要求服务器和应用程序都去遵守, 如此按照此合约开发的无论是服务器还是应用程序都会具有较大的普遍性. 而这就好像在计算机通信的早期, 各大公司都有属于自己的通信协议, 如此只会让市场杂乱无章, 宁愿只要一种通信协议.

而针对 python 的合约是 WSGI(Python Web Server Gateway Interface). 具体的规定见 [PEP 333](http://www.python.org/dev/peps/pep-0333/).

实习的时候一直使用 Django, 下面是结合 Django 学习 WSGI 的笔记.


### application/应用程序


在应用程序一方面, 必须提供下面的方法:

    
    def simple_app(environ, start_response):
        """可能是最简单的处理了"""
        status = '200 OK'
        response_headers = [('Content-type', 'text/plain')]
        start_response(status, response_headers)
        return ['Hello world!\n'] # 返回结果必须可迭代


除了方法以外, 还可以用实现了 __call__ 的类实现.

它会被服务器调用, 在这里 environ 是一个字典, 包含了环境变量, REQUEST_METHOD,SCRIPT_NAME,QUERY_STRING 等; start_response 是一个回调函数, 会在 simple_app 中被调用, 主要用来开始响应 HTTP. start_response 原型大概是这样:

    
    def start_response(status, response_headers, exc_info=None):
        ...
        return write # 返回这 write 函数 只是为了兼容之前的 web 框架, 新的框架根本用不到.


参数有 status 即状态码; response_headers HTTP 头, 可以修改; exc_info 是与错误相关的信息, 在产生相应数据过程中可能发生错误, 这时需要更新 HTTP 头部, 通过再次调用 start_response 可以实现. 因此更为详尽的实现写法可能是这种:

    
    def start_response(status, response_headers, exc_info=None):
        if exc_info:
             try:
                 # do stuff w/exc_info here
             finally:
                 exc_info = None    # Avoid circular ref.
        return write




### Server/服务器


在服务器方面, 可以想象最简单的工作就是调用 simple_app(), 然后向客户端发送数据:

    
    result = simple_app(environ, start_response) #名字不一定为 simple_app
    try:
        for data in result:
            if data:    # don't send headers until body appears
                write(data)
        if not headers_sent:
            write('')   # send headers now if body was empty
    finally:
        if hasattr(result, 'close'):
            result.close()


注意 WSGI 并没有事无巨细规定 web 应用程序和服务器内部的工作方式, 只是是规定了它们之间连接的标准.


### python wsgiref 模块


下面看看 Django 是如何实现 WSGI 的. Django 其内部已经自带了一个方便本地测试的小服务器, 所以在刚开始学习 Django 的时候并不需搭建 apache 或者 nginx 服务器. Django 自带的服务器基于 python wsgiref 模块实现, 它自带的测试代码:

    
    # demo_app() 是 application
    def demo_app(environ,start_response):
        from StringIO import StringIO
        stdout = StringIO()
        print >>stdout, "Hello world!"
        print >>stdout
        h = environ.items(); h.sort()
        for k,v in h:
            print >>stdout, k,'=', repr(v)
        start_response("200 OK", [('Content-Type','text/plain')])
        return [stdout.getvalue()]
    
    def make_server(
        host, port, app, server_class=WSGIServer, handler_class=WSGIRequestHandler
    ):
        """Create a new WSGI server listening on `host` and `port` for `app`"""
        server = server_class((host, port), handler_class)
        server.set_app(app)
        return server
    
    if __name__ == '__main__':
        httpd = make_server('', 8000, demo_app)
        sa = httpd.socket.getsockname()
        print "Serving HTTP on", sa[0], "port", sa[1], "..."
        import webbrowser
        webbrowser.open('http://localhost:8000/xyz?abc')
        httpd.handle_request()  # serve one request, then exit


python 的库有好多的工具, 这时可能因为需要的原因, 会生出好多的父类, 为了讲明, 根据 wsgiref 模块和它自带的测试用例得出下面的 UML 图(注意, 这只是 wsgiref, 没有涉及 Django):

[![python-wsgiref](http://daoluan.net/images/blog/2013/09/python-wsgiref.png)](http://daoluan.net/images/blog/2013/09/python-wsgiref.png)

我读完这些的时候已经晕了, 确实是里边的继承关系有些复杂. 因此, 简要的概括了测试代码的执行关系:



	
  * make_server() 中 WSGIServer 类已经作为服务器类, 负责接收请求, 调用 application 的处理, 返回相应;

	
  * WSGIRequestHandler 作为请求处理类, 并已经配置在 WSGIServer 中;

	
  * 接着还设置了 WSGIServer.application 属性(set_app(app));

	
  * 返回 server 实例.

	
  * 接着打开浏览器, 即发起请求. 服务器实例 WSGIServer httpd 调用自身 handle_request() 函数处理请求. handle_request() 的工作流程如下:请求-->WSGIServer 收到-->调用 WSGIServer.handle_request()-->调用 _handle_request_noblock()-->调用 process_request()-->调用 finish_request()-->finish_request() 中实例化 WSGIRequestHandler-->实例化过程中会调用 handle()-->handle() 中实例化 ServerHandler-->调用 ServerHandler.run()-->run() 调用 application() 这才是真正的逻辑.-->run() 中在调用 ServerHandler.finish_response() 返回数据-->回到 process_request() 中调用 WSGIServer.shutdown_request() 关闭请求(其实什么也没做)


ps: 明明 application 是 WSGIServer 的属性, 为什么会在 ServerHandler 中调用? 因为在实例化 WSGIRequestHandler 的时候 WSGIServer 把自己搭进去了, 所以在 WSGIRequestHandler 中实例化 ServerHandler 时候可以通过 WSGIRequestHandler.server.get_app() 得到真正的 application.


### 总结


从上面可以得到, 启动服务器的时候, 无论以什么方式都要给它传递一个 application(), 是一个函数也好, 一个实现了 __call__ 的类也好; 当请求到达服务器的时候, 服务器自会调用 application(), 从而得到相应数据. 至于, 对请求的数据如何相应, application() 中可以细化.

确实, 其中的调用链太过长, 这期间还没有加入 HTTP 头的分析(提取 Cookie等). 如果只为响应一个 "helloworld", 在 WSGIServer.finish_request() 中直接相应数据就好了, WSGIRequestHandler 和 ServerHandler 类可以直接省去, 而只需要你提供一个 application()! 但事实上, 并不只是相应 "helloworld" 那样简单...

关于 Django 中的 WSGI 如何, 下一节再说. Django 源码剖析从这里开始! 我已经在 github 备份了 Django 源码的注释: [Decode-Django](https://github.com/daoluan/Decode-Django), 有兴趣的童鞋 fork 吧. 本文结合 python wsgiref, BaseHTTPServer.py, SocketServer.py 模块源码看更好.

捣乱  2013-9-4

[http://daoluan.net](http://daoluan.net/)
