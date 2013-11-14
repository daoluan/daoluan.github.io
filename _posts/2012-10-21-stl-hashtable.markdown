---
author: daoluan
comments: true
date: 2012-10-21 04:12:56+00:00
layout: post
slug: stl-hashtable
title: 私房STL之Hashtable
wordpress_id: 1234
categories:
- C/C++
tags:
- C/C++
- 《STL源码剖析》
---

一句话之Hashtable：哈希表（散列表）能通过键值对数据进行访问的数据结构；其在C++0X标准中未出现，可能是考虑到哈希表效率低下，出于其广泛用于工程中，C++11将其纳入了标准库。C++11的新特性：[http://en.wikipedia.org/wiki/C%2B%2B11](http://en.wikipedia.org/wiki/C%2B%2B11)，C++11中哈希表的说明：[http://en.wikipedia.org/wiki/C%2B%2B11#Hash\_tables](http://en.wikipedia.org/wiki/C%2B%2B11#Hash\_tables)；我们知道，通过哈希表来索引目标是很高效的，但这样会出现碰撞问题（即对不同的关键字可能得到同一哈希地址）。常用的解决碰撞的方法有四：线性探测、二次探测、再散列和开链法。而STL中的哈希表所采用的是开链法（也叫链地址法）。

<!-- more -->

[caption id="" align="aligncenter" width="315"]![](http://upload.wikimedia.org/wikipedia/commons/thumb/7/7d/Hash\_table\_3\_1\_1\_0\_1\_0\_0\_SP.svg/315px-Hash\_table\_3\_1\_1\_0\_1\_0\_0\_SP.svg.png) 哈希表[/caption]


### Hashtable的查找，插入，删除


在通过给定的键值计算出元素在Hashtable中的位置（O(1)就可以完成）时，行为就与单链表一样了，查找，插入和删除操作的**平均**开销都为O(N/2)。


=============================================


剩下的内容没有对哈希表模拟实验之类的内容（互联网有很多作者给出了很详细的分析，推荐一个：[http://blog.csdn.net/morewindows/article/details/7330323](http://blog.csdn.net/morewindows/article/details/7330323)），只描述解决碰撞的方法和哈希表的效率问题。


### 哈希表碰撞问题


这样假设，哈希表大小为N，哈希函数为Hash(elem)，计算哈希表地址时，取模N，意即：elem在哈哈希表地址是Hash(elem) % N。

线性探测的做法：计算哈哈希表地址得出Hash(elem) % N，如果此地址未被占用，那么插入；否则，探测(Hash(elem) + 1)  % N 是否占用，如果未被占用，插入。否则继续探测下去。

二次探测的做法：同线性探测，计算哈希表地址得出Hash(elem) % N，如果此地址未被占用，那么插入；否则，探测(Hash(elem) + 1^2)  % N，如果未被占用，插入。否则继续探(Hash(elem) + 2^2)  % N。。。

再散列法：存在K个不同的哈希函数Hi = Hashi(elem) % M，k = 0,1,2,k-1。倘若第1个哈希函数不行，采用第2个，从而减少碰撞。

开链法的做法：属于（vector + single list）的模式，计算哈希表地址得出Hash(elem) % N，插入对应的单链表。


### 哈希表的效率


线性探测，1、需要表有足够大连续的空间，否则元素太多，就需要resize，效率不可观；2、在进行探测的空闲地址的时候，最坏的情况探测整个表，平均情况是整个表的一半，不可取。

二次探测，1、它同样需要有足够大的连续的空间；2、对线性探测的一种改进的地方，便是平方（二次方）探测，意即步长不再是n，而为n^2，这样能减少碰撞。

再散列法：1、它同样需要有足够大的连续的空间；2、增加计算量。

前三种都未能很好解决碰撞问题。

开链法，动态非连续空间（single list），不存在线性探测和二次探测的第一个问题；在确定地址过后，只需要对相应的single list作插入，删除，修改操作，这样碰撞的问题就转化为single list的寻访，速度可观。STL Hashtable就是采用开链法。

[caption id="attachment\_1238" align="aligncenter" width="236"][![](http://daoluan.net/blog/wp-content/uploads/2012/10/Hashtable\_with\_slist.jpg)](http://daoluan.net/blog/stl-hashtable/hashtable\_with\_slist/) 链地址法[/caption]

后来我们将看到，STL中的hash\_set和hash\_map皆由Hashtable作为底层容器。


### 哈希表的应用


在数据结构的课堂便有这样的实验：统计文本单词出现的频率。我们可以创建单词哈希表，Hasn(word)定义为word中每个字符的ASCII码之和，通过它来确定单词在哈希表地址，进而进行统计。

另外，初学程序设计的同学都有设计学生管理系统的经历，现有需求“以学生姓名为关键字，如何建立查找表，使得根据姓名可以直接找到相应记录呢？”，这也是哈希表的一个应用。

本文完 2012-10-21

捣乱小子 [http://www.daoluan.net/](http://www.daoluan.net/)
