---
author: daoluan
comments: true
date: 2013-09-20 23:05:45+00:00
layout: post
slug: decode-django-more-efficient-url-dispatcher
title: 'Django 源码小剖: 更高效的 URL 调度器(URL dispatcher)'
wordpress_id: 2025
categories:
- 学习总结
tags:
- Django
- 源代码
---

### 效率问题


django 内部的 url 调度机制说白了就是给一张有关匹配信息的表, 这张表中有着 url -> action 的映射, 当请求到来的时候, 一个一个(遍历)去匹配. 中, 则调用 action, 产生相应数据返回; 不中, 则会产生 404 等的错误, 而 django 中有内置 404 等错误响应方法.

这种方法和 MFC 里 message map 差不多, 从项目实践(特别是配置 urls.py 文件)就可以猜到大概是这样一种工作模式.

注意上面关于 django url 调度机制的白话描述中的「一个一个」, 这里就有效率上的问题了. 倘若业务逻辑不复杂, 且访问量不高, 系统是没有问题的; 但如果业务逻辑太复杂(直观的表述是 urls.py 中的匹配条目繁杂), 如此加之高访问量, 会加重系统的负担, 试想最坏的情况是每一个请求都会从头到尾匹配一次, 让人感到不爽.


### 一种更好的解决方法


策略还是有的, 因为业务逻辑不会经常变更, 至少不会没几分钟就变更一次, 所以可以借助哈希表来达到快速匹配的目的. 有关哈希表可以参照之前写的一篇文章: [私房STL之hash\_set和hash\_map](http://daoluan.net/blog/stl-hash\_set-and-hash\_map/)


![](http://upload.wikimedia.org/wikipedia/commons/thumb/7/7d/Hash\_table\_3\_1\_1\_0\_1\_0\_0\_SP.svg/315px-Hash\_table\_3\_1\_1\_0\_1\_0\_0\_SP.svg.png)
    哈希表


一般的做法举例如下:


> http://example.com/aaaaa/
http://example.com/bbbbb/
http://example.com/ccccc/
http://example.com/ddddd/
http://example.com/eeeee/
abcde 表示 web 应用的功能模块.


为 aaaaa,bbbbb...都计算得到哈希值 hash(aaaaa),hash(bbbbb)...

当请求 http://example.com/aaaaa/ 到来时候, 提取 aaaaa, 计算哈希值直接在哈希表中定位匹配条目. 一般的做法是这样, 还可以顺着这样的思路继续改进. 譬如, 存在更为复杂的功能, 而且这个功能在 aaaaa 的基础上建立起来: http://example.com/aaaaa/xxxxx, 这时候, 也可以计算 hash(aaaaaxxxxx) 加入到哈希表中.

那是不是每个请求到来启动 web 应用程序的时候都要计算 urls.py 中的条目的哈希值? 并不需要, 可以新建一个 url 服务进程, 只专门维护哈希表, 从 urls.py 中计算哈希表; 通由内存映射技术, web 应用程序可以方便读取哈希表, 并且可以重复利用.

什么提到会调用 url 对应的 action, 并返回响应数据, django 是怎么返回的. 我已经在 github 备份了 Django 源码的注释: [Decode-Django](https://github.com/daoluan/Decode-Django), 有兴趣的童鞋 fork 吧.

捣乱 2013-9-18

[http://daoluan.net](http://daoluan.net/)
