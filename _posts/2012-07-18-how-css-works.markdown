---
author: daoluan
comments: true
date: 2012-07-18 05:46:00+00:00
layout: post
slug: how-css-works
title: CSS的工作原理
wordpress_id: 678
categories:
- 学习总结
tags:
- CSS
---

层叠样式表（英语：Cascading Style Sheets，简写CSS），又称串样式列表，由W3C定义和维护的标准，一种用来为结构化文档（如HTML文档或XML应用）添加样式（字体、间距和颜色等）的计算机语言。维基百科如是说。所以，接触过HTML，对CSS也相对容易理解。

    
    <!--HTML-->
    <body bgcolor=#FF0000>daoluan</body>
    
    /*CSS*/
    body{background-color:#FF0000;}


CSS中包括三个部分：样式名（标准说是“选择器”），属性名和属性值。那CSS的代码应该放在哪里？最为常用的方法就是把css代码独立于一个外部的.css文件中，跟其他文件一样，样式表文件放在Web服务器上或者本地硬盘上；

<!-- more -->![“style.css”被存放在文件夹“style”里](http://daoluan.net/blog/wp-content/uploads/2012/07/css.jpg)

同时在html文档的头部，即header部分，<head></head>之间，显示声明一个指向外部样式表文件的链接。

    
    <link rel="stylesheet" type="text/css" href="style/style.css" />


这个链接告诉浏览器（.css的解析器就是浏览器）：在显示该HTML文件时，应使用给出的CSS文件进行布局。`这样以来多个HTML文档就可以引用同一个css，很大程度上简化了网页的设计。当对当前的样式提出改进的时候，只修改.css就OK了。`

`测试：`

`在桌面新建default.html和style.css两个文件，用记事本进行编辑：`

    
    <!--default.html-->
    <html> 
          <head> 
        <title>daoluan.net/blog</title> 
            <link rel="stylesheet" type="text/css" href="style.css" /> 
          </head> 
          <body> 
        <h1>daoluan.net/blog</h1> 
          </body> 
    </html>



    
    /*style.css*/
    body { 
          background-color: #00FFEE; 
          font-size: 25px; 
          font-family: "微软雅黑"; 
    }


style.css文件里的body内的属性还有很多是可以自定义的，比如字体颜色，背景图片等等（这些交给字典吧！）。

效果图：

[![image_thumb.png](http://daoluan.net/blog/wp-content/uploads/2012/07/image_thumb3.png)](http://daoluan.net/blog/wp-content/uploads/2012/07/image_thumb3.png)

CSS支持非常灵活的样式组合，如果样式名（选择器）为非内置（body，h1等是内置的），比如自定义mystyle样式（它被定义在.css文件里）。比如，同样在桌面新建default.html和style.css两个文件，用记事本进行编辑：

    
    <!--default.html同上-->
    <html> 
          <head> 
        <title>daoluan.net/blog</title> 
            <link rel="stylesheet" type="text/css" href="style.css" /> 
          </head> 
          <body> 
        <h1>daoluan.net/blog</h1> 
          </body> 
    </html>



    
    /*style.css，添加mystyle*/
    body {
    	background-color: #00FFEE;
    	font-size: 25px;
    	font-family: "微软雅黑";
    }
    /*点作为前缀*/
    .mystyle	{
    	color: #FF0000;
    };


效果图：

[![image_thumb.png](http://daoluan.net/blog/wp-content/uploads/2012/07/image_thumb4.png)](http://daoluan.net/blog/wp-content/uploads/2012/07/image_thumb4.png)


本文完 2012-07-15

捣乱小子 [http://www.daoluan.net/blog/](http://www.daoluan.net/blog/)
