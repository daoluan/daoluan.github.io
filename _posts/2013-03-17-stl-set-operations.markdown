---
title: STL求交集、并集、差集和对称差集
date: 2013-03-17 11:52:04 Z
categories:
- cplusplus
- linux
tags:
- C/C++
- GTD项目实录
author: daoluan
comments: true
layout: post
wordpress_id: 1608
---

STL算法提供求两个容器中的数据的交集、并集、差集和对称差集，分别是set_intersection，set_union，set_difference，set_symmetric_difference。

四个函数用法一样，详情可以参考C++ Reference：

[http://www.cplusplus.com/reference/algorithm/set_intersection/](http://www.cplusplus.com/reference/algorithm/set_intersection/)

[http://www.cplusplus.com/reference/algorithm/set_union/](http://www.cplusplus.com/reference/algorithm/set_union/)

[http://www.cplusplus.com/reference/algorithm/set_difference/](http://www.cplusplus.com/reference/algorithm/set_difference/)

[http://www.cplusplus.com/reference/algorithm/set_symmetric_difference/](http://www.cplusplus.com/reference/algorithm/set_symmetric_difference/)

或者参看其他网友的一些讲解：[stl set求交集 并集 差集](http://blog.chinaunix.net/uid-9950859-id-99130.html)[
](http://blog.chinaunix.net/uid-9950859-id-99130.html)

以set_union为例，实现算法不难：

    
    template <class InputIterator1, class InputIterator2, class OutputIterator>
      OutputIterator set_union (InputIterator1 first1, InputIterator1 last1,
                                InputIterator2 first2, InputIterator2 last2,
                                OutputIterator result)
    {
      while (true)
      {
        if (first1==last1) return std::copy(first2,last2,result);
        if (first2==last2) return std::copy(first1,last1,result);
    
        if (*first1<*first2) { *result = *first1; ++first1; }
        else if (*first2<*first1) { *result = *first2; ++first2; }
        else { *result = *first1; ++first1; ++first2; }
        ++result;
      }
    }


细心就会发现，在set_union中有「*first1<*first2」，也就是要求，iterator所对应的的数据必须实现运算符重载「operator <」。C++内置类型比如int，char，long等都可以直接进行比较，但实际需求可能要求必须有更为复杂的数据类型，譬如：

    
    struct datastruct_t
    {
    	int nID;
    	string name;
    };


此时调用set_union不能通过编译！

    
    set_union(a.begin(),a.end(),b,begin(),b.end(),c.begin);


本文有待补充。

捣乱 2013-3-17

[http://daoluan.net](http://daoluan.net)
