---
title: 老调重弹--双缓冲
date: 2012-08-29 15:19:54 Z
categories:
- cplusplus
- mfc
author: daoluan
comments: true
layout: post
wordpress_id: 914
---

MFC中双缓冲技术比较常用，主要是为了避免因绘图过程的缓慢而闪烁。

一般把绘图的工作都直接在前台的DC（设备上下文）中进行，即绘图的全过程（一笔一画）都是用户可见的，如果绘图量过大，就会导致闪烁。

试着把前台的工作交给后台DC来完成，当后台完成绘图过后，再把后台DC中的内容复制到前台DC中（这一过程比前者快很多）。这就是双缓冲。

<!-- more -->

[![](http://daoluan.github.io/images/blog/2012/08/Double-cache.png)](http://daoluan.github.io/blog/archives/914/double-cache)

MFC中具体是这么做的：



	
  1. 声明后台DC和后台位图

    
    CDC m_memClose; 
    CBitmap memBmp;




	
  2. 将后台DC初始化为与前台DC相适应的DC
m_memClose.CreateCompatibleDC(GetDC());

	
  3. 将后台位图初始化为与前台位图相适应的位图
memBmp.CreateCompatibleBitmap(GetDC(),r.Width(),r.Height());

	
  4. 用后台DC选择后台位图对象
m_memClose.SelectObject(&memBmp);

	
  5. 之后便可将绘图工作交给后台DC，绘图完毕过后，再bilbit到前台的DC中。
m_memClose.BitBlt(0,0,r.Width(),r.Height(),GetDC(),0,0,SRCCOPY);


在这个基础上面，可以模拟按钮这一控件。

本文完 2012-08-29

Dylan [http://daoluan.github.io/blog/](http://daoluan.github.io/blog/)
