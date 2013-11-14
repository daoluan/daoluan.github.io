---
author: daoluan
comments: true
date: 2012-09-27 04:30:21+00:00
layout: post
slug: __file____line____function__
title: c++ __FILE__，__LINE__和__FUNCTION__的使用方法
wordpress_id: 1095
categories:
- C/C++
tags:
- C/C++
- GTD项目实录
---

在stackoverflow上看到一个有用的帖子，小试翻译一下。

原文链接：[http://stackoverflow.com/questions/597078/file-line-and-function-usage-in-c](http://stackoverflow.com/questions/597078/file-line-and-function-usage-in-c)

假设你的c++编译器支持__FILE__，__LINE__，__FUNCTION__ ，是否由理由不去用它们来记录调试错误？

我担心的主要是因为编译器性能的优化而导致给用户呈现错误的数据？！

从根本上说，我是否能一直放心使用__FILE__， __LINE__，和__FUNCTION__，而且得到正确的结果？

在C99标准中，__FUNCTION__并不是标准的__func__ ，而__FILE__, __LINE__则是。
这些宏会记录正确的文件名，行号和函数名。原因并不是编译器的优化，因为__FILE__，__LINE__，__FUNCTION__是编译内置的时间宏扩展。它们无论如何不会影响性能。

<!-- more -->


> 回复：__func__在c++中是有错的。c99标准在没有没有显示说明__func__的行为方式情况下，没有指明默认参数等等。

回复：回复：你说得对，我也很清楚__func__出现在c99中，而不是c++。不管怎么样，我认为c++中合理__func__的实现将导致命名混乱。


没错，__FILE__，__LINE__和__FUNCTION__在c++ 程序调试当中显得很重要，可以做适当的抽象写成一个适应项目工程的记录器或者调试机。下面只演示__FILE__，__LINE__和__FUNCTION__在c++程序中的效果。

源程序如下：

    
    #include <iostream>
    using namespace std;
    
    void foo()
    {
    	cout << __FUNCTION__ << endl;
    	cout << __LINE__ << endl;
    	cout << __FILE__ << endl;
    }
    
    int main()
    {
    	cout << __FUNCTION__ << endl;
    	cout << __LINE__ << endl;
    	cout << __FILE__ << endl;
    
    	foo();
    	return 0;
    }


下面是执行效果

[![](http://daoluan.net/blog/wp-content/uploads/2012/09/c++___FILE_____LINE__and__FUNCTION__.jpg)](http://daoluan.net/blog/archives/1095/c___file_____line__and__function__)

正如上所看到的，__FILE__，__LINE__和__FUNCTION__这三个宏由编译器处理返回对应的字符串，与真正代码逻辑不相关，所以算的上是编译调试利器。譬如，在可能出错的地方，做适当的文件记录（file log），程序崩溃或出错问题反馈或许可以在日志文件中找到。

本文完 2012-9-27

捣乱小子 [http://www.daoluan.net/](http://www.daoluan.net/blog/)
