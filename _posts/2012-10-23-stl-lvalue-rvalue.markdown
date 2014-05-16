---
author: daoluan
comments: true
date: 2012-10-23 12:06:52+00:00
layout: post
slug: stl-lvalue-rvalue
title: 私房STL之左值和右值
wordpress_id: 1285
categories:
- cplusplus
tags:
- C/C++
- 《STL源码剖析》
---

左值和右值并不专属于STL里的内容，是在接触STL的过程发现了笔者C/C++的知识规则漏洞。


### 左值右值


左值（LValue）即等号左边的值，右值（RValue）即等号右边的值，右值必须放在等号右边，但左值既可以在左边也可以放在右边。那么数值（等式），字符串，常量，只能作为右值，右值决不能放置等号左边。


    100 = 60;		/*数值是右值，不合法*/
    'A' = 'a';		/*字符是右值，不合法*/
    const int a = 1;
    a = 100;		/*a为常量，属右值，不合法*/


<!-- more -->

变量，引用（reference）作为左值，既可以在等式左边，又可以在等式右边。


    int a,b;
    a = 2;		/*a左值，2右值。*/
    b = a;		/*b左值，a左值。*/
    int &c = a;	/*a左值，c左值。*/


特别的，自增有两种形式：i++和++i，但两者是有区别的，允许我用c将其操作展开：

i++的操作：


    {
    	int temp = i;
    	++i;
    	return temp;
    }


++i的操作：


    {
    	i = i + 1;
    	return i;
    }


因此i++ = 1是不合法的，因为i++返回的是临时值，不是i自己，为了消除歧义，i++坚决返回右值，也就是说它只能放置在等式右边。而++i = 1是合法的，从上面操作的展开来看，++i确实返回了它自己，因此它是一个左值，既能是在等式的左边，也能是右边。


### C++左值右值延伸


延伸至类的运算符重载的问题上。我们先假定一个类Node，


    class Node
    {
    public:
    	Node(int nAge = 0)
    	{
    		m_nAge = nAge;
    	}

    	int GetAge()const
    	{
    		return m_nAge;
    	}

    	Node operator ++ (int n)	/*i++*/
    	{
    		Node temp = *this;
    		m_nAge ++;
    		return temp;
    	}

    	Node& operator ++ ()		/*++i*//*你知道为什么要返回reference吗？*/
    	{
    		m_nAge ++;
    		return *this;
    	}

    	Node& operator = (int n)
    	{
    		m_nAge = n;
    		return *this;
    	}
    private:
    	int m_nAge;
    };


C++规定，Node& operator ++ ()是重载前缀自增运算符（++i），而Node operator ++ (int n)是重载后缀自增运算符（i++）。细心发现，重载前缀自增运算符返回的是reference引用，而重载后缀自增运算符返回的是临时变量。换句话说，如果有Node对象node，我希望++node（前缀）返回的是左值，node++（后缀）返回的右值。意即希望，注意是希望：


    ++node = 1;	/*合法，++node返回值作为左值*/
    node++ = 1;	/*不合法，node++返回值作为左值*/


但是，重载运算操作符本来就是为改变运算符的行为而来的，所以上述行为是编译器所允许的。但语法上没有问题，但逻辑上却有严重的漏洞。++node = 1;确实改变了node的内容，但node++ = 1;未能得逞，因为“=1”的操作被执行在temp上，故****node++ = 1;执行过后，node内容改变为以前的值+1，而不是等于1。


    ......
    Node node(23);	/*node.m_nAge初值为23。*/

    node ++ = 1;
    cout << "node ++ = 1;执行过后，node.m_nAge = " << node.GetAge() << endl;
    ++ node = 1;
    cout << "++ node = 1;执行过后，node.m_nAge = " << node.GetAge() << endl;
    ......




<blockquote><p>node ++ = 1;执行过后，node.m_nAge = 24<br>
++ node = 1;执行过后，node.m_nAge = 1<br>
请按任意键继续. . .</p></blockquote>


node++ = 1;执行过后，node没有被“=1”影响。那可不可以反其道而行呢？“我偏要让它返回左值”！当然行，没有问题，只要修改它的行为就好了。


    ......
    Node& operator ++ (int n)	/*i++*//*修改i++的行为，让它也返回左值*/
    {
    	//Node temp = *this;
    	//m_nAge ++;
    	//return temp;
    	m_nAge ++;
    	return *this;
    }
    ......



<blockquote><p>node ++ = 1;执行过后，node.m_nAge = 1<br>
++ node = 1;执行过后，node.m_nAge = 1<br>
请按任意键继续. . .</p></blockquote>


但还是建议不要这样做，因为会引起混淆。

总结下，左值可以出现在等式左边，又可以是右边；右值只能出现在右边。++i返回左值，i++返回右值，这样也就是为什么在重载前缀自增运算符时候，要返回reference（左值）了。

本文完 2012-10-23

捣乱小子 [http://www.daoluan.net/](http://www.daoluan.net/)
