---
title: 玩转位图（bitmap）2
date: 2012-11-07 17:05:33 Z
categories:
- cplusplus
- mfc
tags:
- 开源应用
- 编程小记
author: daoluan
comments: true
layout: post
wordpress_id: 1445
---

2012年11月8日9:25:47 已上传源代码和可执行文件

2012年11月8日1:03:01 深夜断网，不能上传源码和可执行文件，明日早起补上。喜欢的童鞋们先收藏。

[![](http://daoluan.net/images/blog/2012/11/Maruko.jpg)](http://daoluan.net/blog/enjoy-bitmap2/maruko/) 小丸子

<!-- more -->

查看大图：[http://daoluan.net/images/blog/2012/11/Maruko.jpg](http://daoluan.net/images/blog/2012/11/Maruko.jpg)

接上篇：[http://daoluan.net/blog/enjoy-bitmap/](http://daoluan.net/blog/enjoy-bitmap/)

上篇中发布的程序中不支持png，jpg，gif等主流的图片格式的玩转，只支持24位位图。这一次对软件做以下更新：



	
  * 提供png，jpg（jpeg），tif（tiff）三种图片格式（抱歉gif尚未解决）的支持

	
  * 根据图片的大小适当调整字符字体大小，转换后图片视觉效果更佳

	
  * 优化代码


在图片格式的处理上，笔者借助codeproject上公布的CxImage工具，主要是开源。[http://www.codeproject.com/Articles/1300/CxImage](http://www.codeproject.com/Articles/1300/CxImage)

关于如何在工程中使用CxImage，笔者不复述，除了上面给出作者公布的贴以外，还有以下中文版的解说贴：

[http://blog.csdn.net/afterwards_/article/details/7997385](http://blog.csdn.net/afterwards_/article/details/7997385)

[http://blog.csdn.net/afterwards_/article/details/7997426](http://blog.csdn.net/afterwards_/article/details/7997426)

测试建议：转换过程涉及灰度深浅计算，图片**平均灰度**偏高或者偏低转换图片**效果不佳**，特别是纯白或者纯黑的图片；推荐使用宠物大头照等；图片的尺寸建议越大越好，长宽700+（Pixels），越大效果越好。

源代码，包含CxImage的库文件，比较大：[http://files.cnblogs.com/daoluanxiaozi/pic2_src.rar](http://files.cnblogs.com/daoluanxiaozi/pic2_src.rar)

可执行文件：[http://files.cnblogs.com/daoluanxiaozi/pic2.exe.rar](http://files.cnblogs.com/daoluanxiaozi/pic2.exe.rar)

本文完 2012-11-8

Dylan [http://www.daoluan.net/](http://www.daoluan.net/)
