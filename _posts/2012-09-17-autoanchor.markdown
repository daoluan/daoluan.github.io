---
author: daoluan
comments: true
date: 2012-09-17 11:27:55+00:00
layout: post
slug: autoanchor
title: 『AA』AutoAnchor自动猫
wordpress_id: 1049
categories:
- 学习总结
---

2012-09-17 19:40:31：嘿嘿，给自己出了道编程题，难度不大（YY都可以）， 大家有兴趣可以自己去实现下。


### 文章目录





	
  * 引子

	
  * 思路

	
  * 用法

	
  * 标bug

	
  * 源代码 & 可执行文件




<!-- more -->





### 引子


一篇博文如果太长的话，为博文标题添加锚链接可以给众多的读者导航，提高文章的易读性。我也喜欢上了锚链接。但博客后台编辑器的“锚链接工具”我不会用，于是AutoAnchor 自动猫的灵感就来了。




### 思路


这道编程题不难，YY都可以得到一个解决方法。每次搜寻到<h3>标签就自动在其前面添加<a name="%d"></a>，处理好html文件之后，再在文章的头部添加：

    
    <h3>文章目录</h3>
    <ul>
    	<li><a href="#0">标题0</a></li>
    	<li><a href="#1">标题1</a></li>
    	<li><a href="#2">标题2</a></li>
    	<li><a href="#3">标题3</a></li>
    </ul>





### 用法





	
  * 从博客后台编辑器中获取博文html文本，存档为index.html

	
  * 在AutoAnchor目录下放置所要添加锚链接的index.html

	
  * 运行AutoAnchor目录下的AutoAnchor.exe文件即可得到ret.html

	
  * 把ret.html中的html文本复制到博客编辑器中





### bug


产生的带锚链接的文章开始，**需要自己重命名标题**，因为时间关系，没有设计抓取<h3></h3>之间的标题文本。文章末尾有源代码，有兴趣的同学可以帮我升级下，抠门的细节太多了~~

[![](http://daoluan.net/blog/wp-content/uploads/2012/09/AutoAnchor\_bug.jpg)](http://daoluan.net/blog/archives/1049/autoanchor\_bug)

缺陷：除非修改源代码，不然只支持<h3>的标题检测，就是说只能为<h3>标题添加锚链接。




### 源代码 & 可执行文件


[http://files.cnblogs.com/daoluanxiaozi/AutoAnchor.rar](http://files.cnblogs.com/daoluanxiaozi/AutoAnchor.rar)

喜欢就赞一个呗。

本文完 2012-09-17

捣乱小子 [http://www.daoluan.net/blog/](http://www.daoluan.net/blog/)
