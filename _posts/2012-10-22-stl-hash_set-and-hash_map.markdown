---
author: daoluan
comments: true
date: 2012-10-22 16:29:25+00:00
layout: post
slug: stl-hash_set-and-hash_map
title: 私房STL之hash_set和hash_map
wordpress_id: 1271
categories:
- C/C++
tags:
- C/C++
- 《STL源码剖析》
---

一句话hash_set和hash_map：它们皆由Hashtable（Standard C++ Library未公开，只作为底层部件）作为底层容器， 所有的操作也都由Hashtable提供；咋看起来，好似与set和map有很大的关联，其实不大，只不过hash_set和hash_map有着“set键值就是实值，实值就是键值，map键值就是键值，实值就是实值”特征，姑且让set和map挂挂名:-)；

由此，hash_set内部元素也是未经排序的（从Hashtable的实现可知），而hash_map可以经由键值索引其对应实值（其重载了“[]”操作符）；由Hashtable的底层实现可知：hash_set和hash_map的查找效率和插入操作的平均时间开销都为O(N/2)。

<!-- more -->


### hash_set和hash_map的创建与遍历


hash_set只需指定键值的类型，hash_map需指定键值和实值的类型。它们都可以像大多数的容器一样，通过迭代器，寻访元素。

    
    ......
    hash_set<int> ihs; 
    
    ihs.insert(1);
    ihs.insert(5);
    ihs.insert(6);
    ihs.insert(4);
    ihs.insert(3);
    ihs.insert(3);
    ihs.insert(100);
    
    ihs.insert(200);		/*故意的*/
    
    hash_set<int>::iterator beg = ihs.begin(),
    	end = ihs.end(),ite;
    
    for(ite = beg; ite != end; ite++)
    	cout << *ite << " ";
    cout << endl;
    ......




> 200 1 3 4 100 5 6


可证见hash_set拒绝插入重复元素（与set性质相同），未排序（违反set性质）。

    
    ......
    hash_map<int,int> ihm;
    
    ihm.insert(pair<int,int>(1,100));
    ihm.insert(pair<int,int>(2,200));
    ihm.insert(pair<int,int>(3,300));
    ihm.insert(pair<int,int>(4,400));
    ihm.insert(pair<int,int>(5,500));
    
    hash_map<int,int>::iterator beg = ihm.begin(),
    	end = ihm.end(),ite;
    
    for(ite = beg; ite != end; ite++)
    	cout << "<" << ite->first << "," << ite->second << ">" << " ";
    cout << endl;
    
    cout << "ihm[1] = " << ihm[1] << endl;		/*可以通过键值索引*/
    ......




> <1,100> <2,200> <3,300> <4,400> <5,500>
ihm[1] = 100




### hash_set和hash_map的查找


有Hashtable的实现可知，hash_set和hash_map的平均查找效率一样很高，各自内部有实现find()查找函数，无需使用从头至尾遍历的STL <algorithm>find()函数。Standard C++ Library中的实例：[http://msdn.microsoft.com/en-US/library/ea54hzhb(v=vs.80).aspx](http://msdn.microsoft.com/en-US/library/ea54hzhb(v=vs.80).aspx)


### 建议


hash_set和hash_map还实现很多函数，给出参考链接：[http://msdn.microsoft.com/en-US/library/y49kh4ha(v=vs.80).aspx](http://msdn.microsoft.com/en-US/library/y49kh4ha(v=vs.80).aspx)

外链[MoreWindows](http://blog.csdn.net/morewindows/)同学的文章：[http://blog.csdn.net/morewindows/article/details/7330323](http://blog.csdn.net/morewindows/article/details/7330323)，里头的亮点便是C++里头语法的细节问题。

本文完 2012-10-23

捣乱小子 [http://www.daoluan.net/](http://www.daoluan.net/)
