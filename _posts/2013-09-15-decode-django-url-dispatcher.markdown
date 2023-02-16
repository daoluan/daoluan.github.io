---
title: 'Django 源码小剖: URL 调度器(URL dispatcher)'
date: 2013-09-15 14:04:37 Z
categories:
- 学习总结
tags:
- Django
- 源代码
author: daoluan
comments: true
layout: post
wordpress_id: 1980
---

在刚开始接触 django 的时候, 我们尝试着从各种入门文档中创建一个自己的 django 项目, 需要在 mysite.urls.py 中配置 URL. 这是 django url 匹配处理机制的一小部分.


### URL 调度器详解


django url 匹配处理机制主要由一下模块实现: django.conf.urls 和 django.core.urlresolver.py. 有需要摘取上一节中的代码:

    
    # BaseHandler.get_response() 的定义
    # 处理请求的函数, 并返回 response
    def get_response(self, request):
        "Returns an HttpResponse object for the given HttpRequest"
        根据请求, 得到响应
    
        try:
            为该线程提供默认的 url 处理器
            # Setup default url resolver for this thread, this code is outside
            # the try/except so we don't get a spurious "unbound local
            # variable" exception in the event an exception is raised before
            # resolver is set
    
            #ROOT_URLCONF = 'mysite.urls'
            urlconf = settings.ROOT_URLCONF
    
            # set_urlconf() 会设置 url 配置即 settings.ROOT_URLCONF
            # 会设置一个线程共享变量, 存储 urlconf
            urlresolvers.set_urlconf(urlconf)
    
            # 实例化 RegexURLResolver, 暂且将其理解为一个 url 的匹配处理器, 下节展开
            resolver = urlresolvers.RegexURLResolver(r'^/', urlconf)
    
            try:
                response = None
    
                # Apply request middleware 调用请求中间件
                ......
    
                # 如果没有结果
                if response is None:
                    # 尝试 request 中是否有 urlconf, 一般没有, 可以忽略此段代码!!!
                    if hasattr(request, 'urlconf'):
                        # Reset url resolver with a custom urlconf. 自定义的 urlconf
                        urlconf = request.urlconf
                        urlresolvers.set_urlconf(urlconf)
                        resolver = urlresolvers.RegexURLResolver(r'^/', urlconf)
                    # 调用 RegexURLResolver.resolve(), 可以理解为启动匹配的函数; 返回 ResolverMatch 实例
                    resolver_match = resolver.resolve(request.path_info)
    
                    # resolver_match 对象中存储了有用的信息, 譬如 callback 就是我们在 views.py 中定义的函数.
                    callback, callback_args, callback_kwargs = resolver_match
    
                    # 将返回的 resolver_match 挂钩到 request
                    request.resolver_match = resolver_match
    
                    # Apply view middleware 调用视图中间件
                    ......


可以简单的理解为 get_response() 中构造了 RegexURLResolver 对象并调用了 RegexURLResolver.resolve(path) 启动解析. 从上面的代码中, 可以获知 urlconf 默认使用的是 mysite.settings.py 中的 ROOT_URLCONF, 而也确实可以在 mysite.settings.py 中找到对应的设置项, 并且做出修改.

从上, 至少可以知道, 真正发挥匹配作用的是 RegexURLResolver 对象, 并调用 RegexURLResolver.resolve() 启动了解析, 一切从这里开始. 从 urlresolver.py 中抽取主干部分, 可以得到下面的 UML 图:

[![url_dispatcher_uml](http://daoluan.github.io/images/blog/2013/09/url_dispatcher_uml.jpg)](http://daoluan.github.io/images/blog/2013/09/url_dispatcher_uml.jpg)

LocaleRegexProvider 类只为地区化而存在, 他持有 regex 属性, 但在 RegexURLResolver 和 RegexURLPattern 中发挥不同的作用:



	
  * RegexURLResolver: 过滤 url 的前缀, 譬如如果 regex 属性值为 people, 那么能将 people/daoluan/ 过滤为 daoluan/.

	
  * RegexURLPattern: 匹配整个 url.


在展开 ResolverMatch, RegexURLPattern, RegexURLResolver 三个类之前, 暂且将他们理解为:

	
  * ResolverMatch 当匹配成功时会实例化返回

	
  * RegexURLPattern, RegexURLResolver 匹配器, 但有不同.


然后需要先介绍三个函数: url(), include(), patterns(), 三者经常在 urls.py 中用到. 它们在 django.conf.urls 中定义. 摘抄和解析如下:

    
    # url 里面可以用 incude 函数
    def include(arg, namespace=None, app_name=None):
        if isinstance(arg, tuple):
            # callable returning a namespace hint
            if namespace:
                raise ImproperlyConfigured('Cannot override the namespace for a dynamic module that provides a namespace')
    
            # 获取 urlconf 模块文件, 应用名, 命名空间
            urlconf_module, app_name, namespace = arg
        else:
            # No namespace hint - use manually provided namespace
            urlconf_module = arg
    
        if isinstance(urlconf_module, six.string_types):
            # 尝试导入模块
            urlconf_module = import_module(urlconf_module)
    
        # 在 urlconf_module 中导入 urlpatterns
        # 在 urlconf_module 中肯定会有 urlpatterns 这个变量
        patterns = getattr(urlconf_module, 'urlpatterns', urlconf_module)
    
        # Make sure we can iterate through the patterns (without this, some
        # testcases will break).
        if isinstance(patterns, (list, tuple)):
            for url_pattern in patterns:
                # Test if the LocaleRegexURLResolver is used within the include;
                # this should throw an error since this is not allowed!
                if isinstance(url_pattern, LocaleRegexURLResolver):
                    raise ImproperlyConfigured(
                        'Using i18n_patterns in an included URLconf is not allowed.')
    
        # 返回模块, app 名 ,命名空间
        return (urlconf_module, app_name, namespace)
    
    def patterns(prefix, *args): 特意留一个 prefix
        pattern_list = []
        for t in args:
            if isinstance(t, (list, tuple)):
                t = url(prefix=prefix, *t) 自动转换
    
            elif isinstance(t, RegexURLPattern):
                t.add_prefix(prefix)
    
            pattern_list.append(t)
    
        # 返回 RegexURLResolver 或者 RegexURLPattern 对象的列表
        return pattern_list
    
    # url 函数
    def url(regex, view, kwargs=None, name=None, prefix=''):
        if isinstance(view, (list,tuple)): 如果是 list 或者 tuple
            # For include(...) processing. 处理包含 include(...)
            urlconf_module, app_name, namespace = view
    
            # 此处返回 RegexURLResolver, 区分下面返回 RegexURLPattern
            return RegexURLResolver(regex, urlconf_module, kwargs, app_name=app_name, namespace=namespace)
        else:
            if isinstance(view, six.string_types):
                if not view:
                    raise ImproperlyConfigured('Empty URL pattern view name not permitted (for pattern %r)' % regex)
                if prefix:
                    view = prefix + '.' + view
    
            # 返回 RegexURLPattern 的对象
            return RegexURLPattern(regex, view, kwargs, name)
        # 从上面可以获知, url 会返回 RegexURLResolver 或者 RegexURLPattern 对象


可以简单的理解为, url() 根据具体情况返回 RegexURLResolver 或者 RegexURLPattern 对象; patterns() 返回了包含有 RegexURLPattern 和 RegexURLResolver 对象的列表. 当在 urls.py 中出现:
每个 include() 的时候, 最终会产生一个 RegexURLResolver 对象;
否则为 RegexURLPattern 对象.

    
    回到那三个类, 摘取 RegexURLResolver 的主干函数作为讲解:
    # 最关键的函数
    def resolve(self, path):
    
        tried = []
    
        # regex 在 RegexURLResolver 中表示前缀
        match = self.regex.search(path)
    
        if match:
            # 去除前缀
            new_path = path[match.end():]
    
            for pattern in self.url_patterns: # 穷举所有的 url pattern
                # pattern 是 RegexURLPattern 实例
                try:
    
    """在 RegexURLResolver.resolve() 中的一句: sub_match = pattern.resolve(new_path) 最为关键.
    从上面 patterns() 函数的作用知道, pattern 可以是 RegexURLPattern 对象或者 RegexURLResolver 对象. 当为 RegexURLResolver 对象的时候, 就是启动子 url 匹配处理器, 于是又回到了上面.
    
    RegexURLPattern 和 RegexURLResolver 都有一个 resolve() 函数, 所以, 下面的一句 resolve() 调用, 可以是调用 RegexURLPattern.resolve() 或者 RegexURLResolver.resolve()"""
    
                    # 返回 ResolverMatch 实例
                    sub_match = pattern.resolve(new_path)
    
                except Resolver404 as e:
                    # 搜集已经尝试过的匹配器, 在出错的页面中会显示错误信息
                    sub_tried = e.args[0].get('tried')
    
                    if sub_tried is not None:
                        tried.extend([[pattern] + t for t in sub_tried])
                    else:
                        tried.append([pattern])
                else:
                    # 是否成功匹配
                    if sub_match:
                        # match.groupdict()
                        # Return a dictionary containing all the named subgroups of the match,
                        # keyed by the subgroup name.
    
                        # 如果在 urls.py 的正则表达式中使用了变量, match.groupdict() 返回即为变量和值.
                        sub_match_dict = dict(match.groupdict(), **self.default_kwargs)
    
                        sub_match_dict.update(sub_match.kwargs)
    
                        # 返回 ResolverMatch 对象, 如你所知, 得到此对象将可以执行真正的逻辑操作, 即 views.py 内定义的函数.
                        return ResolverMatch(sub_match.func,
                            sub_match.args, sub_match_dict,
                            sub_match.url_name, self.app_name or sub_match.app_name,
                            [self.namespace] + sub_match.namespaces)
    
                    tried.append([pattern])
    
            # 如果没有匹配成功的项目, 将异常
            raise Resolver404({'tried': tried, 'path': new_path})
    
        raise Resolver404({'path' : path})
    
    # 修饰 urlconf_module, 返回 self._urlconf_module, 即 urlpatterns 变量所在的文件
    @property
    def urlconf_module(self):
        try:
            return self._urlconf_module
        except AttributeError:
            self._urlconf_module = import_module(self.urlconf_name)
            return self._urlconf_module
    
    # 返回指定文件中的 urlpatterns 变量
    @property
    def url_patterns(self):
        patterns = getattr(self.urlconf_module, "urlpatterns", self.urlconf_module)
        try:
            iter(patterns) # 是否可以迭代
        except TypeError:
            raise ImproperlyConfigured("The included urlconf %s doesn't have any patterns in it" % self.urlconf_name)
    
        # patterns 实际上是 RegexURLPattern 对象和 RegexURLResolver 对象的集合
        return patterns
    
    摘取 RegexURLPattern 的主干函数作为讲解:
    
    # 执行正则匹配
    def resolve(self, path):
        match = self.regex.search(path) # 搜索
        if match:
            # If there are any named groups, use those as kwargs, ignoring
            # non-named groups. Otherwise, pass all non-named arguments as
            # positional arguments.
            # match.groupdict() 返回正则表达式中匹配的变量以及其值, 需要了解 python 中正则表达式的使用
            kwargs = match.groupdict()
            if kwargs:
                args = ()
            else:
                args = match.groups()
    
            # In both cases, pass any extra_kwargs as **kwargs.
            kwargs.update(self.default_args)
    
            # 成功, 返回匹配结果类; 否则返回 None
            return ResolverMatch(self.callback, args, kwargs, self.name)
    
    # 对 callback 进行修饰, 如果 self._callback 不是一个可调用的对象, 则可能还是一个字符串, 需要解析得到可调用的对象
    @property
    def callback(self):
        if self._callback is not None:
            return self._callback
    
        self._callback = get_callable(self._callback_str)
        return self._callback
    
    ResolverMatch 不贴代码了, 它包装了匹配成功所需要的信息, 如 views.py 中定义的函数.




### URL 调度过程实例


下面的具体例子将加深对 RegexURLResolver.reslove() 调用的理解. 假设工程名为 mysite, 并且创建了 app people.

    
    # mysite.urls.py
    from django.conf.urls import patterns, include, url
    
    urlpatterns = patterns('',
         url(r"^$","mysite.views.index"),
         url(r"^about/","mysite.views.about"),
         url(r"^people/",include(people.urls)),
         url(r"^contact/","mysite.views.contact"),
         url(r"^update/","mysite.views.update"),
    )
    
    # people.urls.py
    from django.conf.urls import patterns, include, url
    
    urlpatterns = patterns('',
         url(r"^daoluan/","people.views.daoluan"),
         url(r"^sam/","people.views.sam"),
         url(r"^jenny/","people.views.jenny"),
    )
    # people.views.py
    def daoluan(request):
        return HttpResponse("hello")


当访问 http://exapmle.com/people/daoluan/ 的时候 URL dispatcher 的调度过程(蓝色部分):


[![urldispatcher_example](http://daoluan.github.io/images/blog/2013/09/urldispatcher_example.gif)](http://daoluan.github.io/images/blog/2013/09/urldispatcher_example.gif)

对应上面的例子 url 调度器机制的具体工作过程如下, 从 BaseHandler.get_response() 开始说起:

1. BaseHandler.get_response() 中根据 settings.py 中的 ROOT_URLCONF 设置选项构造 RegexURLResolver 对象, 并调用 RegexURLResolver.resolve("/people/daoluan/") 启动解析, 其中 RegexURLResolver.regex = "^\", 也就是说它会过滤 "\", url 变为 "people/daoluan/";

2. resolve() 中调用 RegexURLResolver.url_patterns(), 加载了所有的匹配信息如下(和图中一样):



	
  * (类型)RegexURLPattern (正则匹配式)[^$]

	
  * RegexURLPattern [^about/]

	
  * RegexURLResolver [^people/]

	
  * RegexURLPattern [^contact/]

	
  * RegexURLPattern [^update/]


语句 for pattern in self.url_patterns: 开始依次匹配. 第一个因为是 RegexURLPattern 对象, 调用 resolve() 为 RegexURLPattern.resolve(): 它直接用 [^$] 去匹配 "people/daoluan/", 结果当然是不匹配.

3. 下一个 pattern 过程同上.

4. 第三个 pattern 因为是  RegexURLResolver 对象, 所以 resolve() 调用的是 RegexURLResolver.resolve(), 而非上面两个例子中的 RegexURLPattern.resolve().  因为第三个 pattern.regex = "^people/", 所以会将 "people/daoluan/" 过滤为 "daoluan/". pattern.resolve() 中会调用 RegexURLResolver.url_patterns(), 加载了所有的匹配信息如下(和图中一样):

	
  * RegexURLPattern [^daoluan$]

	
  * RegexURLPattern [^sam$]

	
  * RegexURLPattern [^jenny$]


语句 for pattern in self.url_patterns: 开始依次匹配. 第一个就中, 过程和刚开始的过程一样. 因此构造 ResolverMatch 对象返回. 于是 BaseHandler.get_response() 就顺利得到 ResolverMatch 对象, 其中记录了有用的信息. **在 BaseHandler.get_response() 中有足够的信息让你知道开发人员在 views.py 中定义的函数是 def daoluan(request): 在什么时候调用的:**

    
    # BaseHandler.get_response() 的定义
    # 处理请求的函数, 并返回 response
    def get_response(self, request):
        ......
    
        # 实例化 RegexURLResolver, 暂且将其理解为一个 url 的匹配处理器, 下节展开
        resolver = urlresolvers.RegexURLResolver(r'^/', urlconf)
        ......
    
        # 调用 RegexURLResolver.resolve(), 可以理解为启动匹配的函数; 返回 ResolverMatch 实例
        resolver_match = resolver.resolve(request.path_info)
        ......
    
        # resolver_match 对象中存储了有用的信息, 譬如 callback 就是我们在 views.py 中定义的函数.
        callback, callback_args, callback_kwargs = resolver_match
        ......
    
        # 这里调用的是真正的处理函数, 我们一般在 view.py 中定义这些函数
        response = callback(request, *callback_args, **callback_kwargs)
        ......
    
        return response




### 总结


从上面知道, url 调度器主要 RegexURLResolver, RegexURLPattern, ResolverMatch 和三个辅助函数 url(), include(), patterns() 完成. 可以发现, url 的调度顺序是根据 urls.py 中的声明顺序决定的, 意即遍历一张表而已, 有没有办法提高查找的效率?

我已经在 github 备份了 Django 源码的注释: [Decode-Django](https://github.com/daoluan/Decode-Django), 有兴趣的童鞋 fork 吧.

Dylan 2013-9-15

[http://daoluan.github.io](http://daoluan.github.io)
