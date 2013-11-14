---
author: daoluan
comments: true
date: 2012-07-30 02:47:06+00:00
layout: post
slug: vmwarelinuxputty%e7%8e%af%e5%a2%83%e9%85%8d%e7%bd%ae-2
title: vmware+Linux+putty环境配置
wordpress_id: 759
categories:
- Linux
tags:
- Linux
---

这里主要解决vmware虚拟机上的Linux与主机进行相互通信的问题，另外介绍[putty](http://zh.wikipedia.org/wiki/Putty)工具的使用。

接触Linux的时候，因为不习惯Linux的各种操作，所以选择了**vmware+Linux+[putty](http://zh.wikipedia.org/wiki/Putty)**。[**putty**](http://zh.wikipedia.org/wiki/Putty)相比Linux的命令行舒服许多。


### VMware+linux


Linux选择了ubuntu 12。一般装上ubuntu，选用NAT网络连接，即可联网（如果主机已经联网），笔者试了多次都可以，至少。但主机与虚拟机（以下简称Linux）暂时可能还无法通信。笔者采用设置静态IP来解决问题。

<!-- more -->



	
  1. 编辑->编辑虚拟网络->选择VMnet8->NAT设置，查看子网IP，掩码和网关IP
[![1\_thumb.png](http://daoluan.net/blog/wp-content/uploads/2012/07/1\_thumb.png)](http://daoluan.net/blog/wp-content/uploads/2012/07/1\_thumb.png)

	
  2. Linux设置静态IP
vim /etc/network/interfaces根据第一步得到的信息，文件末尾添加如下：
auto eth0
iface eth0 inet static
address 192.168.2.6（子网192.168.2.0）
gateway 192.168.2.2（网关192.168.2.2）
netmask 255.255.255.0（掩码）
[![2\_thumb.png](http://daoluan.net/blog/wp-content/uploads/2012/07/2\_thumb.png)](http://daoluan.net/blog/wp-content/uploads/2012/07/2\_thumb.png)
reboot下，确保上述设置生效

	
  3. 设置Linux的DNS地址
vim /etc/resolv.conf（指明dns地址）
nameserver 192.168.2.2（第一步中查询到的网关）
[![3\_thumb.png](http://daoluan.net/blog/wp-content/uploads/2012/07/3\_thumb.png)](http://daoluan.net/blog/wp-content/uploads/2012/07/3\_thumb.png)

	
  4. 设置主机本地连接的静态IP
如果你的主机直连路由器，那么主机本地连接的静态IP可以和Linux不在同一个子网内；但如果没有，那么必须设置在同一个子网内，这样才能实现主机和Linux之间的通信。 此时主机和Linux可以相互ping通，而且Linux可以联网。上述环境有利于不熟悉Linux环境的初学者，熟练的话大可不必。
[![4\_thumb.png](http://daoluan.net/blog/wp-content/uploads/2012/07/4\_thumb.png)](http://daoluan.net/blog/wp-content/uploads/2012/07/4\_thumb.png)


**putty**

有了上述的基础，下面是putty工具的使用，上面也为putty铺垫。这里说的putty选用SSH登录Linux。所以Linux必须支持SSH。
#apt-get remove openssh-client
apt-get install openssh-client
apt-get install openssh-server
ps -A | grep ssh
用ps命令查看有sshd进程

[![5\_thumb.png](http://daoluan.net/blog/wp-content/uploads/2012/07/5\_thumb.png)](http://daoluan.net/blog/wp-content/uploads/2012/07/5\_thumb.png)

已经设置Linux的静态IP为192.168.2.9，此当然可作为putty登录Linux的IP Address。

[![6\_thumb.png](http://daoluan.net/blog/wp-content/uploads/2012/07/6\_thumb.png)](http://daoluan.net/blog/wp-content/uploads/2012/07/6\_thumb.png)

输入Linux帐号密码即可远程登录。这样非常方便一边在纯字符界面下编程或者调试，一边在win下查阅资料。笔者认为vmware+Linux+putty的环境很适合初学者。putty很容易将字符界面下的文字拷贝到win环境下，方便我们的查询。

个人putty配置建议：如果觉得putty本身默认的字体太过小而觉得不适合，可以在Window->Appearane中设置字体和字号。对笔者来说，偏好consola字体，写代码很舒服。另外，在vim中编辑代码的时候，「//」注释的颜色会变成ANSI BLUE，非常难看，一种方案便是修改vim的配置，从而需该注释的颜色；另一种是经过设置putty来实现，在Window->Color中，在「select a color to ajust:」列表中选择ANSI BLUE，把这个难看的颜色modify就好了。

更多关于putty的设置参看：[http://bbs.chinaunix.net/thread-949760-1-1.html](http://bbs.chinaunix.net/thread-949760-1-1.html)可以保存设置

本文完 2012-07-29

捣乱小子 [http://www.daoluan.net/blog/](http://www.daoluan.net/blog/)
