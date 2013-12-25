---
author: daoluan
comments: true
date: 2012-07-13 06:28:33+00:00
layout: post
slug: linux-background-process
title: Unix/Linux 那些系统启动后的进程
wordpress_id: 649
categories:
- linux
tags:
- apue 学习总结
- linux
---

# 闲扯




> 什么时候开始有“UNIX/LINIX”这一词汇，我忘了？只知道它是一个操作系统，跟dos一个级别的？！也就停留在这个概念的层次上，所以很多对我来说都是迷。UNIX也走过了40多个年头的路程，而它的每一个组织不断得到改进；21世纪开源势头正猛，前进的步伐更快了！




# 正文


**眼过千边，不如收过一遍！**以下结论来自apue、互联网或者些许自己的理解，实践环境：Linux 2.6。

当内核加载完成之后，会创建init进程，它是系统的第一个进程init。init进程ID为1，也因此它是之后所有进程的“祖宗”！init进程是系统进入了多用户的状态，允许多个终端设备登录（tty1，tty2...）。对于每一个终端设备，init进程调用一次fork生成一个子进程，紧接着调用exec执行getty程序。


> 下面的文件是/ect/init/tty1.conf，这足以说明init的动作。
> 
> [![image_thumb.png](http://daoluan.net/blog/wp-content/uploads/2012/07/image_thumb.png)](http://daoluan.net/blog/wp-content/uploads/2012/07/image_thumb.png)


getty进程所要做的：



	
  1. open：调用open打开输入输出（fd为0，1，2的文件）；

	
  2. read：输出“hostname login：”提示信息，接着读取用户输入的用户名；

	
  3. exec：根据用户名和从文件中读入的初始环境调用exec，实际上是execle。


现在，getty完成它的使命，把现场交给（exec）login进程。login做的事情可多啦：

	
  1. 提示用户输入密码兵营验证密码；如果验证多次不成功，又把现在交给init，init知道子进程被XX了，接下来的事情跟上面的一样；

	
  2. 验证成功的话，设置当前工作目录

	
  3. 更改终端所有者

	
  4. 对终端的权限改为读与写

	
  5. 设置进程组ID

	
  6. 设置起始目录（HOME），shell（SHELL），用户名（USER和LOGNAME），系统默认路径（PATH）


login已完成使命（主要是以上步骤），shell登场（exec）。

	
  1. 登录shell的文件描述符0、1、2设置为终端设备

	
  2. 读取用户启动文件（我用的是ubuntu 12，内核是Linux，用的GNU bash，它用的启动文件是起始目录下的.profile），执行初始化操作

	
  3. 等待用户键入命令


根据上面的第二条：

[![image_thumb.png](http://daoluan.net/blog/wp-content/uploads/2012/07/image_thumb1.png)](http://daoluan.net/blog/wp-content/uploads/2012/07/image_thumb1.png)

我在.profile第九行添加“Daoluan Logins In Succeed!”，在进入命令提示符的前一行，就有显示这一字符串，说明这是初始化的必经之地。经常我们需要自定义我们的工作环境的时候，通常要在工作目录下的.bashrc（在.profile文件里有一个行执行.bashrc的代码），从而达到自定义环境的目的。


> 用apue上一幅图来结束这篇学习总结！
> 
> [![image_thumb.png](http://daoluan.net/blog/wp-content/uploads/2012/07/image_thumb2.png)](http://daoluan.net/blog/wp-content/uploads/2012/07/image_thumb2.png)

上面是终端登录的过程；网络登录的话，会有伪终端设备驱动程序，配合talnet来对终端进行仿真。


欢迎斧正！

本文完 2012-07-13

捣乱小子 [http://www.daoluan.net/blog/](http://www.daoluan.net/blog/)
