---
title: 花钱买实在
date: 2016-07-03 21:02:59 Z
categories:
- 编程小记
tags:
- socks5
author: daoluan
comments: true
layout: post
wordpress_id: 2495
---

动手实现了一个代理。小工具基本能用，但无奈找不到一个合适的 vps，只能浏览图片比较少的网页，更不用说 yb 了，根本扛不住。在亚马逊 aws 上申请了东京和新加坡各开了一个实例，但无奈 ping 延时基本在 200~400 以上，一点都不顺畅。试了下自己买的 shadowsocks，时延居然 70ms 左右，至少和国内的网站在同一个数量级，所以还是得花钱买个实在，人家用的服务器资源比免费的优质多了。

整个代理全部用 golang 实现，golang 写起来还是相当顺手，而且非常适合用来写网络代理，goroutine 让代码写起来更顺畅，基本没有什么阻碍。使用的是 sock5 协议，RFC 文档里 sock5 的协议就一页，而且无鉴权模式下实现更加简单，在实现的时候简单抓几个包然后对着 RFC 文档来写，很快就可以把免鉴权功能搞定，剩下的就是转包了。

基本的实现框架是在本地(local)开启一个代理，这个代理用来处理 sock5 协议的处理以及浏览器的请求。在远程也开启一个代理，这个代理负责与实际的网站交互。本地的代理和远程的代理使用私有协议交互，目前使用的是 des 加密。

[![访问 G站](http://daoluan.github.io/images/blog/2016/google-page.png)](http://daoluan.github.io/images/blog/2016/google-page.png)

初步完成 2016年6月9日00:44:19

上一次完成放手了一段时间，后来发现有地方处理不对，又一次掉坑了。经过几个小时找 bug，借助 chrome 的调试器以及屏幕日志，发现了问题，基本的网页访问是没有问题；yb 还是不行，看起来一卡一卡的，体验很差，什么时候能找到好用的代理服务器，搭建起来就很好用了。已经上传 github：[gosocks](https://github.com/daoluan/gosocks)

debug 2016年7月3日20:07:23
