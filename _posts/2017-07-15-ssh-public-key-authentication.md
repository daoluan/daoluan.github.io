---
title: ssh 免密登录过程
date: 2017-07-15 00:00:00 Z
categories:
- 学习总结
tags:
- ssh
author: daoluan
layout: post
---

rfc4252 规定，ssh 登录服务器是可以通过 pubkey 的方式登录的，这样省去了输入密码的过程，此方式生效的前提是服务器已经拥有了客户端生成的 pubkey，privkey 存在于客户端。

首先，客户端询问服务器是否接受 pubkey 方式登录，询问的格式如下：


![](http://daoluan.github.io/images/blog/2017/ssh-public-key-authentication_01.png)

服务器收到这个请求后，允许客户端使用 pubkey 的方式登录，格式如下：

![](http://daoluan.github.io/images/blog/2017/ssh-public-key-authentication_02.png)

客户端此时会发送一段数据以及用私钥对这个数据的签名，发给服务器，两部分的数据格式如下：

![](http://daoluan.github.io/images/blog/2017/ssh-public-key-authentication_03.png)

服务器因为有客户端的 pubkey，所以可以对签名进行校验，从而决定是否信任该客户端。ssh 登录的加 -vvv 选项，可以看到客户端侧的登录流程：

![](http://daoluan.github.io/images/blog/2017/ssh-public-key-authentication_04.png)

网上有“服务器用公钥加密，客户端用私钥解密，服务器看返回的数据是否为原始数据”这样的描述，但从 rfc文档来看， pubkey 登录过程并非这样。

    sshconnect2.c
    sign_and_send_pubkey
    input_userauth_pk_ok
    send_pubkey_test

对源码感兴趣的同学可以参看 openssl 的上面几个函数，基本从从客户端的角度描述了怎么使用 pubkey 登录服务器的过程。

reference：[https://www.ssh.com/a/rfc4252.txt](https://www.ssh.com/a/rfc4252.txt)