---
author: daoluan
comments: true
date: 2012-11-01 02:49:56+00:00
layout: post
slug: enjoy-bitmap
title: 玩转位图（bitmap）
wordpress_id: 1350
categories:
- cplusplus
- mfc
---

[![](http://md.daoluan.net/blog/images/2012/11/enjoy_bitmap_jobs.jpg)](http://daoluan.net/blog/enjoy-bitmap/enjoy_bitmap_jobs/) 乔帮主

年前加入一个项目小组，只要是做图像处理的软件，组内分配第一个任务便是熟悉位图。[http://www.cnblogs.com/daoluanxiaozi/tag/MFC%E5%B0%8F%E9%A1%B9%E7%9B%AE/](http://www.cnblogs.com/daoluanxiaozi/tag/MFC%E5%B0%8F%E9%A1%B9%E7%9B%AE/)，但后来不知道为什么，没有呆下去。

大三刚开学的时候，@杨海坡 换了个QQ头像，大致的效果如下（原图见about页面）：图片中有小小的方块，每个方块内对应一个字符。YY下，结合对位图的了解，可以动手实现，“这个可以有”。

<!-- more -->

[![](http://md.daoluan.net/blog/images/2012/11/enjoy_bitmap_sample.jpg)](http://daoluan.net/blog/enjoy-bitma/enjoy_bitmap_sample/) 大致效果

png，jpg，gif等都不懂，所以从位图下手，来实现图片的处理。

思路：



	
  1. 读bmp文件

	
  2. 读取**一个方块所有rgb值**，然后通过[YUV 与 RGB 的转换公式](http://zh.wikipedia.org/wiki/YUV)得到此方块的灰度值

	
  3. 根据对应的灰度值，绘对应的字符（灰度值越大，字符点阵的覆盖密度越小）

	
  4. 保存文件


图片在处理过后，在缩小的情况下视觉效果好，但不尽人意。程序未对所有的位图格式都有设定特定的处理方法，只实现了24位位图的处理，所以需要测试的话，可以用mspaint（附件里头的绘图或美图秀秀等）转换下格式。

可执行文件：[http://files.cnblogs.com/daoluanxiaozi/pic.exe.rar](http://files.cnblogs.com/daoluanxiaozi/pic.exe.rar)

软件用MFC实现，测试通过，下面是源代码：

[ http://files.cnblogs.com/daoluanxiaozi/pic.rar](http://files.cnblogs.com/daoluanxiaozi/pic.rar)

本文完 2012-11-1

捣乱小子 [http://www.daoluan.net/](http://www.daoluan.net/)
