---
author: daoluan
comments: true
date: 2012-10-24 16:06:26+00:00
layout: post
slug: stl-function-object
title: 私房STL之函数对象
wordpress_id: 1301
categories:
- cplusplus
tags:
- C/C++
- 《STL源码剖析》
---

一句话之函数对象：函数对象（又称仿函数）的秘密不足以让你吃惊，它是重载“()”操作符的类（结构体）的对象；实现简单：声明一个类（结构体），重载“()”操作符，即可。

PS：你也知道了函数对象的定义，下面的内容函数对象有时候指的就是函数对象，有时候指的是函数对象对应的类（结构体）。

STL存在内建的函数对象，比如算术类函数对象（+，-等），关系运算类函数对象（==，！、等），逻辑运算类函数对象（&&，||等），详见；[http://cplusplus.com/reference/std/functional/](http://cplusplus.com/reference/std/functional/)，但编程无止境，可能这些还不够用，我们可以轻而易举的自定义函数对象。

<!-- more -->


### 函数对象的使用


函数对象直接应用的地方较少，但了为了配合接下来配接器（下一篇博文）的内容，简单测试下：

    
    cout << "10 + 10 = " << plus<int>()(10,10) << endl;
    cout << "10 - 10 = " << minus<int>()(10,10) << endl;
    cout << "10 == 10 ? " << equal_to<int>()(10,10) << endl;




<blockquote>10 + 10 = 20
10 - 10 = 0
10 == 10 ? 1
请按任意键继续. . .</blockquote>


plus<int>()(10,10)；中，第一个括号是为了产生struct plus的临时对象，第二个括号调用struct plus内部重载的“()”函数。上面是优雅的写法，也可以通俗点：

    
    plus<float> opplus;
    cout << "10.0 + 10.1 = " << opplus(10.0,10.1) << endl;


一下是struct plus的全貌，它很单纯：

    
    template<class _Ty>
    	struct plus
    		: public binary_function<_Ty, _Ty, _Ty>
    	{	// functor for operator+
    	_Ty operator()(const _Ty& _Left, const _Ty& _Right) const
    		{	// apply operator+ to operands
    		return (_Left + _Right);
    		}
    	};




### 自定义函数对象


有些情况内建的函数对象不能满足我们的要求，需要我们自定义一个函数对象来对付当下的问题。STL规定：所有可配接的一元函数都应该继承[unary_function](http://cplusplus.com/reference/std/functional/unary_function/)（unary：一元），所有可配接的二元函数都应该继承[binary_function](http://cplusplus.com/reference/std/functional/binary_function/)（binary：二元）。譬如，我们定义一个平方算术类函数对象，很easy，照猫画虎plus的做法，修改其内部执行即可：

    
    template<class _Ty>
    struct square
    	: public unary_function<_Ty, _Ty>
    {	
    	_Ty operator()(const _Ty& Arg) const
    	{	
    		return (Arg * Arg);
    	}
    };
    
    ......
    cout << "10^2 = " << square<int>()(10) << endl;
    ......




<blockquote>10^2 = 100
请按任意键继续. . .</blockquote>


本文完 2012-10-25

捣乱小子 [http://www.daoluan.net/](http://www.daoluan.net/)
