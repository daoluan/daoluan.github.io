---
author: daoluan
comments: true
date: 2013-09-11 07:21:21+00:00
layout: post
slug: decode-django-wsgihandler
title: 'Django 源码小剖: 应用程序入口 WSGIHandler'
wordpress_id: 1954
categories:
- 学习总结
tags:
- Django
- 源代码
---

WSGI 有三个部分, 分别为服务器(server), 应用程序(application) 和中间件(middleware). 已经知道, 服务器方面会调用应用程序来处理请求, 在应用程序中有真正的处理逻辑, 在这里面几乎可以做任何事情, 其中的中间件就会在里面展开.


### Django 中的应用程序


任何的 WSGI 应用程序,  都必须是一个 start_response(status, response_headers, exc_info=None) 形式的函数或者定义了 __call__ 的类. 而 django.core.handlers 就用后一种方式实现了应用程序: WSGIHandler.  在这之前, Django 是如何指定自己的 application 的, 在一个具体的 Django 项目中, 它的方式如下:

在 mysite.settings.py 中能找到如下设置:

    
    # Python dotted path to the WSGI application used by Django's runserver.
    WSGI_APPLICATION = 'tomato.wsgi.application'


如你所见, WSGI_APPLICATION 就指定了应用程序. 而按图索骥下去, 找到项目中的 wsgi.py, 已经除去了所有的注释:

    
    import os
    
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tomato.settings")
    
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()


因此, WSGI_APPLICATION 所指定的即为 wsgi.py 中的全局变量 application. 故伎重演, 继续找下去. 在 django.core 模块中的 wsgi.py 中找到 get_wsgi_application() 函数的实现:

    
    from django.core.handlers.wsgi import WSGIHandler
    
    def get_wsgi_application():
        """
        The public interface to Django's WSGI support. Should return a WSGI
        callable.
    
        Allows us to avoid making django.core.handlers.WSGIHandler public API, in
        case the internal WSGI implementation changes or moves in the future.
    
        """
        """
        # 继承, 但只实现了 __call__ 方法, 方便使用
        class WSGIHandler(base.BaseHandler):
        """
        return WSGIHandler()


在 get_wsgi_application() 中实例化了 WSGIHandler, 并无其他操作.


### WSGIHandler


紧接着在 django.core.handler 的 base.py 中找到 WSGIHandler 的实现.

    
    # 继承, 但只实现了 __call__ 方法, 方便使用
    class WSGIHandler(base.BaseHandler):
        initLock = Lock()
    
        # 关于此, 日后展开, 可以将其视为一个代表 http 请求的类
        request_class = WSGIRequest
    
        # WSGIHandler 也可以作为函数来调用
        def __call__(self, environ, start_response):
            # Set up middleware if needed. We couldn't do this earlier, because
            # settings weren't available.
    
            # 这里的检测: 因为 self._request_middleware 是最后才设定的, 所以如果为空,
            # 很可能是因为 self.load_middleware() 没有调用成功.
            if self._request_middleware is None:
                with self.initLock:
                    try:
                        # Check that middleware is still uninitialised.
                        if self._request_middleware is None:
                            因为 load_middleware() 可能没有调用, 调用一次.
                            self.load_middleware()
                    except:
                        # Unload whatever middleware we got
                        self._request_middleware = None
                        raise
    
            set_script_prefix(base.get_script_name(environ))
            signls.request_started.send(sender=self.__class__) # __class__ 代表自己的类
    
            try:
                # 实例化 request_class = WSGIRequest, 将在日后文章中展开, 可以将其视为一个代表 http 请求的类
                request = self.request_class(environ)
    
            except UnicodeDecodeError:
                logger.warning('Bad Request (UnicodeDecodeError)',
                    exc_info=sys.exc_info(),
                    extra=\{
                        'status_code': 400,
                    \}
                )
                response = http.HttpResponseBadRequest()
            else:
                # 调用 self.get_response(), 将会返回一个相应对象 response
                ############# 关键的操作, self.response() 可以获取响应数据.          
                response = self.get_response(request)
    
            # 将 self 挂钩到 response 对象
            response._handler_class = self.__class__
    
            try:
                status_text = STATUS_CODE_TEXT[response.status_code]
            except KeyError:
                status_text = 'UNKNOWN STATUS CODE'
    
             # 状态码
            status = '%s %s' % (response.status_code, status_text)
    
            response_headers = [(str(k), str(v)) for k, v in response.items()]
    
            # 对于每个一个 cookie, 都在 header 中设置: Set-cookie xxx=yyy
            for c in response.cookies.values():
                response_headers.append((str('Set-Cookie'), str(c.output(header=''))))
    
            # start_response() 操作已经在上节中介绍了
            start_response(force_str(status), response_headers)
    
            # 成功返回相应对象
            return response


WSGIHandler 类只实现了 def __call__(self, environ, start_response), 使它本身能够成为 WSGI 中的应用程序, 并且实现 __call__ 能让类的行为跟函数一样, 详见 python __call__ 方法.

** def __call__(self, environ, start_response) 方法中调用了 WSGIHandler.get_response() 方法以获取响应数据对象 response.** 从 WSGIHandler 的实现来看, 它并不是最为底层的: WSGIHandler 继承自 base.BaseHandler, 在 django.core.handler 的 base.py 中可以找到: class BaseHandler(object):...

这一节服务器部分已经结束, 接下来的便是中间件和应用程序了, 相关内容会在下节的 BaseHandler 中展开. 我已经在 github 备份了 Django 源码的注释: [Decode-Django](https://github.com/daoluan/Decode-Django), 有兴趣的童鞋 fork 吧.

近来准备校园招聘, 生产效率较低, 九月份的空气注定不安分 ;)

捣乱 2013-9-11

[http://daoluan.net](http://daoluan.net)
