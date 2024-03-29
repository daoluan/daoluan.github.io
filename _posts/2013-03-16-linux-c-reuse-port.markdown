---
title: Linux c端口复用
date: 2013-03-16 05:58:32 Z
categories:
- linux
- 网络编程
tags:
- C/C++
- GTD项目实录
- linux
author: daoluan
comments: true
layout: post
wordpress_id: 1604
---

在Linux c后台开发中， 经常需要修改一段服务器代码过后，编译连接然后重启服务器进程。

如果两次服务器启动间隔时间过短，系统将不允许。因为上一次启动服务器所使用端口的被占用了。即使上一次服务器进程已经被关闭，但系统处于安全考虑需要占用一段时间。但稍后该端口自动释放。除开修改端口来解决解决问题，那么还有一种一劳永逸，屡试不爽的方法。

一般的后台服务器进程大概这样：


[![fork](http://daoluan.github.io/images/blog/2012/08/fork.png)](http://daoluan.github.io/images/blog/2012/08/fork.png)


先socket()申请一个合法的套接字，这时如果直接bind、listen，就不能再短时间内重启服务器（因为端口被占用）。

Linux c中的setsockopt函数可以解决这个问题。在socket()得到套接字后，调用此函数即可：

    
    int sock_reusr = 1;
    setsockopt(*listenfd ,
        SOL_SOCKET,
        SO_REUSEADDR,
        (char *)&sock_reuse,
        sizeof(sock_reuse));


之前，没有接触这一函数，在后台开发上浪费了很多的时间。

Dylan 2013-3-16
