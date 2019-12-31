---
title: 数据结构利器之私房STL
date: 2012-12-01 16:06:57 Z
categories:
- cplusplus
- 学习总结
- 算法
tags:
- C/C++
- "《STL源码剖析》"
author: daoluan
comments: true
layout: post
wordpress_id: 1508
---

**此系列的文章适合初学有意剖析STL和欲复习STL的同学们**。都是原创！

学过c++的同学相信都有或多或少接触过STL。STL不仅仅是c++中很好的编程工具（这个词可能有点歧义，用类库更恰当），还是学习数据结构的好教材。它实现了包括可边长数组，链表，栈，队列，散列，映射等等，这些都是计算机专业同学在数据结构这门核心课程当中需要学习的。

在深入一个工具之前，首先要熟练使用它。STL也一样。在剖析STL之前，可以先动手使用STL，比如其中的vector，list，stack等，热热身，而使用比剖析简单的多，何乐而不为呢。网上很多仁人志士都推荐[《C++标准程序库》](http://book.douban.com/subject/1110941/)，这本书好！但如果是新手，又急于了解如何使用STL，那么我更倾向于选择一般的c++书籍（里面有简单的STL使用范例）。另外，还推荐c++ reference站点：[http://www.cplusplus.com/](http://www.cplusplus.com/)，[google](https://www.google.com/)更不在话下。注意，如果你已经通读[《C++标准程序库》](http://book.douban.com/subject/1110941/)，那么至多是熟练使用STL而已，但不能说精通STL。**欲精通STL，必剖之。**

工欲善其事，必先利其器，剖析STL你需要做什么？剖析STL可能需要熟悉c++的基本的语法，了解泛型编程等。最后是[《STL源码剖析》](http://book.douban.com/subject/1110934/)。

此系列的文章无意巨细分析STL内部具体实现，因为互联网上有很多大牛（@[July](http://blog.csdn.net/v_JULY_v) @[MoreWindows](http://blog.csdn.net/MoreWindows) 待补充，他们的文章链接会在对应的文章中给出）的作品，STL内的一些算法和实现都已经解释的很详细了，不再班门弄斧。相反，此系列意在为STL中的每一部件作**简要**的总结说明，并穿插其中实现的技巧**。**



	
  1. [私房STL之vector](http://daoluan.net/blog/?p=1149)

	
  2. [私房STL之list](http://daoluan.net/blog/?p=1159)

	
  3. [私房STL之deque](http://daoluan.net/blog/?p=1170)

	
  4. [私房STL之stack与queue](http://daoluan.net/blog/?p=1187)

	
  5. [私房STL之一分钟的heap](http://daoluan.net/blog/?p=1196)

	
  6. [私房STL之map和set](http://daoluan.net/blog/?p=1218)

	
  7. [私房STL之Hashtable](http://daoluan.net/blog/?p=1234)

	
  8. [私房STL算法之全排列](http://daoluan.net/blog/?p=1247)

	
  9. [私房STL算法之快速幂](http://daoluan.net/blog/?p=1265)

	
  10. [私房STL之hash_set和hash_map](http://daoluan.net/blog/?p=1271)

	
  11. [私房STL之左值和右值](http://daoluan.net/blog/?p=1285)

	
  12. [私房STL之函数对象](http://daoluan.net/blog/?p=1301)

	
  13. [私房STL之函数配接器](http://daoluan.net/blog/?p=1312)

	
  14. [私房STL之迭代器](http://daoluan.net/blog/?p=1341)


STL是很实用的工具，用好了就宝贝，对工程有很大的帮助。

ps：取名『私房STL』有点霸道，不过最后还是厚颜斗胆为此系列选用此名。

本文完 2012-12-1

Dylan [http://www.daoluan.net/](http://www.daoluan.net/)
