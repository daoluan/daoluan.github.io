---
author: daoluan
comments: true
date: 2013-08-25 03:37:03+00:00
layout: post
slug: urllib-source-decode
title: urllib 源码小剖
wordpress_id: 1904
categories:
- 编程小记
- 网络编程
tags:
- urllib
- urllib2
- 源代码
- 爬虫
---

两篇小剖已经完成：



	
  * [urllib 源码小剖](http://daoluan.net/blog/urllib-source-decode/)

	
  * [urllib2 源码小剖](http://daoluan.net/blog/urllib2-source-decode/)


urllib 是 python 内置的网络爬虫模块，如果熟悉 python 一定能很快上手使用 urllib。

写这篇文章的目的是因为用到了它，但因为用的次数较多，又或者是具体的需求，有必要深入去理解内部的工作方式。

[![urllib](http://daoluan.net/blog/wp-content/uploads/2013/08/urllib.gif)](http://daoluan.net/blog/wp-content/uploads/2013/08/urllib.gif)


### 最简单的使用


urllib 最简单的使用，我也从下面的语句中开始：

    
    import urllib
    params = urllib.urlencode(\{'spam': 1, 'eggs': 2, 'bacon': 0\})
    f = urllib.urlopen("http://www.musi-cal.com/cgi-bin/query?%s" % params)
    print f.read()


urllib 是模块，urlopen 是模块中的一个方法，它应该属于最高层的封装了，对于传入的任意 url 都能够处理，不管是 http还是https,还是 ftp 还是 file（本地文件）.
它返回一个文件对象的包装类，里面除了文件对象，还有 HTTP response 的头和状态码，url 等；根据网络环境或者服务响应速度，会延迟一些时间。

注意，在这个时候，网络上的资源已经读取到了本地，被放在一个文件中。

接下来，f.read 从文件对象中读取数据。

下面是 urlopen 的源码：

    
    def urlopen(url, data=None, proxies=None):
    	......
        global \_urlopener
        if proxies is not None:
            opener = FancyURLopener(proxies=proxies)
        elif not \_urlopener:
            opener = FancyURLopener()
            \_urlopener = opener
        else:
            opener = \_urlopener
        if data is None:
            return opener.open(url)
        else:
            return opener.open(url, data)


其中，我们可以得到的讯息是，它创建了类 FancyURLopener 对象，并调用了它的 open方法，而类 FancyURLopener 就是 urllib 的核心。


### FancyURLopener


FancyURLopener 其实是 URLopener 的子类，所以从 URLopener 开始说起。

**\_\_tempfiles** 是一个 list，用来存储从网络爬取到本地的本地文件名，你可以单独调用这个方法
**addheader** 添加 HTTP 头，得到了一个 URLopener 对象，就可以使用此函数添加额外的 HTTP 头

**open** 上面已经提到的，它相当于一个工程老板，会根据不同的 url 来为不同的部门派发不同任务，比如，提供的是 http://baidu.com 就会调用 open\_http
**open\_unknown** 无法解析的 url就会调用它，抛出异常
**retrieve** 爬取网络资源，存储在本地文件，返回一个本地文件的文件名和 HTTP 的response 头
**open\_http** 上面提到过，很综合的处理函数，可以提供 HTTP 基本访问认证，proxy 认证等功能，调用 httplib库的函数。在得到 HTTP response后，会根据 HTTP status 状态码返回爬取的结果或者调用 error 处理函数 http\_error

**http\_error** 它其实也是个老板，会根据不同的状态码，为不同的部门分发不同的任务，比如，302 状态码就会调用 http\_error\_302 方法，302 是资源被临时迁移了，所以会发起再次的请求。
**http\_error\_default** 抛出异常，当懒得理那些毛毛小小的错误，就会使用这样的函数

**open\_https** 提供 https 的爬取，和 open\_http 差不多
**open\_file** 爬取 ftp 或者直接读取本地文件
**open\_local\_file** open\_file 当需要直接读取本地文件时候会调用此函数
**open\_ftp** open\_file 当 ftp 资源时候会调用此函数
**open\_data** 好似官方没怎么介绍，应该可以忽略它

**FancyURLopener** 是 urlopener 的子类，主要提供了更详细的错误处理
**http\_error\_302** 302 状态码的处理
**redirect\_internal** 302 里边调用这个

**http\_error\_301** 直接调用302
**http\_error\_303** 直接调用302
**http\_error\_307** 当是 POST 的时候，调用直接调用 http\_error\_default；其他调用 http\_error\_default

**http\_error\_401** 是认证处理
**http\_error\_407** 是认证处理，但需要 proxy 代理
**retry\_proxy\_http\_basic\_auth** 代理重新认证 401 的时候会用到
**retry\_proxy\_https\_basic\_auth** 同上
**retry\_http\_basic\_auth** 访问认证
**retry\_https\_basic\_auth** 同上
**prompt\_user\_passwd** 认证的时候需要账号密码，控制台输入

关于 HTTP 协议的基本认证，推荐阅读：HTTP://www.cnblogs.com/TankXiao/archive/2012/09/26/2695955.html 简单明了

从上面可以看出，无论是 urlopener 还是 FancyURLopener 都没有涉及具体的 ftp 操作，因为在 urllib 中有为 ftp 提供封装：class ftpwrapper 在 open\_ftp 中会直接创建 ftpwrapper 对象，然后执行其内部操作，具体不叙述了。

下面提到的三个类是 opener.open() 返回的对象：

class **addbase** 主要包装对文件对象的操作 read close 等
class **addinfo** addbase 的子类，添加了返回 HTTP response 头方法
class **addinfourl** addinfo 的子类，添加返回 url 方法

print f.read() 这一句调用其实就是 文件对象的 read，但它是 addinfourl 对象
接下来就是一些实用的工具函数了，主要处理各式各样的 url，譬如提取url里面的 host，port等。源码里有各种实用方法的效果图：

    
    # Utilities to parse URLs (most of these return None for missing parts):
    # unwrap('<URL:type://host/path>') --> 'type://host/path'
    # splittype('type:opaquestring') --> 'type', 'opaquestring'
    # splithost('//host[:port]/path') --> 'host[:port]', '/path'
    # splituser('user[:passwd]@host[:port]') --> 'user[:passwd]', 'host[:port]'
    # splitpasswd('user:passwd') -> 'user', 'passwd'
    # splitport('host:port') --> 'host', 'port'
    # splitquery('/path?query') --> '/path', 'query'
    # splittag('/path#tag') --> '/path', 'tag'
    # splitattr('/path;attr1=value1;attr2=value2;...') ->
    # '/path', ['attr1=value1', 'attr2=value2', ...]
    # splitvalue('attr=value') --> 'attr', 'value'
    # unquote('abc%20def') -> 'abc def'
    # quote('abc def') -> 'abc%20def')


最后总结，urlopen 是最高层的封装，简单的一句话就可以爬取 WWW 很简单；其内部是通由 FancyURLopener 实现，FancyURLopener 是 URLopener 的父类：URLopener 实现了爬取方法，但未定义对应具体状态码的 error handlers，这些由 FancyURLopener 定义。

捣乱  2013-08-25

[http://daoluan.net](http://daoluan.net/)
