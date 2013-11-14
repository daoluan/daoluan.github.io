---
author: daoluan
comments: true
date: 2012-10-18 16:34:11+00:00
layout: post
slug: stl-stack-queue
title: 私房STL之stack与queue
wordpress_id: 1187
categories:
- C/C++
tags:
- C/C++
- 《STL源码剖析》
---

一句话stack和queue：相对于[deque](http://daoluan.net/blog/?p=1170  )，stack和queue没有那么底层，他们大部分底层的操作都由deque一手操办，特别的stack和queue是deque的子集（换句话说，stack、queue管deque叫老爹）；通过关闭或者限制deque的一些接口就可以轻易实现stack和queue（STL源码剖析中管这种机制叫“adapter”。）；由stack和queue的定义来看，它们的遍历动作是不被允许的，没有迭代器概念；有趣的是，通过修改list的接口，同样可以让[list](http://daoluan.net/blog/stl-list/)假冒stack和queue。

[caption id="attachment\_1188" align="aligncenter" width="200"][![](http://daoluan.net/blog/wp-content/uploads/2012/10/stack.png)](http://daoluan.net/blog/stl%e4%b9%8bstack%e4%b8%8equeue/stack/) stack[/caption]

<!-- more -->


==================




[caption id="attachment\_1189" align="aligncenter" width="240"][![](http://daoluan.net/blog/wp-content/uploads/2012/10/queue.jpg)](http://daoluan.net/blog/stl%e4%b9%8bstack%e4%b8%8equeue/queue/) queue[/caption]


### stack的创建与遍历


除了默认的构造函数，stack和其他很多容器一样，支持依据vector中元素创建stack。只给出默认版本：更多的资料：[http://www.cplusplus.com/reference/stl/stack/stack/](http://www.cplusplus.com/reference/stl/stack/stack/)

    
    .....
    stack<int> is;
    
    is.push(4);
    is.push(3);
    is.push(2);
    is.push(1);
    is.push(0);
    
    while(!is.empty())
    \{
    	cout << is.top() << " ";
    	is.pop();
    \}//	while	/*0 1 2 3 4*/
    .....


stack不允许遍历！


### queue的创建与遍历



    
    ......
    queue<int> iq;
    
    iq.push(4);
    iq.push(3);
    iq.push(2);
    iq.push(1);
    iq.push(0);
    
    cout << iq.back() << endl;	/*0*/
    
    while(!iq.empty())
    \{
    	cout << iq.front() << " ";
    	iq.pop();
    \}//	while	/*4 3 2 1 0*/
    ......


queue不允许遍历！


### stack/queue的查找和排序


stack/queue不允许遍历！


### 关于stack的top()和pop()


在数据结构的课程中，习惯将上面两个功能都整合到pop中去，但STL分开了，一个函数只做一件事情，在queue中也是这样做的。

    
    ......
    Sequence c;		//	底层容器
    ......
    reference top()	\{	return c.back();	\}
    void pop()	\{	c.pop\_back();	\}
    ......


从Sequence c的定义当中可以看出一些端倪，stack允许用户选定底层容器，所以list此时可以作为底层容器来实现stack/queue。

    
    ......
    stack<int,list<int>> is;
    
    is.push(4);
    is.push(3);
    is.push(2);
    is.push(1);
    is.push(0);
    
    while(!is.empty())
    \{
    	cout << is.top() << " ";
    	is.pop();
    \}//	while	/*0 1 2 3 4*/
    ......




### 建议


stack/queue在实际应用用的比较多，两者有很大的共性，因此queue被提取出来。嘿嘿，突然对STL肃然起敬。

关于更多的stack和queue请参看：[http://www.cplusplus.com/reference/stl/stack/](http://www.cplusplus.com/reference/stl/stack/)和[http://www.cplusplus.com/reference/stl/queue/](http://www.cplusplus.com/reference/stl/queue/)

本文完 2012-10-19

捣乱小子 [http://www.daoluan.net/](http://www.daoluan.net/blog/)
