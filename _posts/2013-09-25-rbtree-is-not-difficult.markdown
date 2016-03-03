---
author: daoluan
comments: true
date: 2013-09-25 12:54:53+00:00
layout: post
slug: rbtree-is-not-difficult
title: 红黑树并没有我们想象的那么难(上)
wordpress_id: 2057
categories:
- 数据结构
- 算法
tags:
- 《STL源码剖析》
- 红黑树
---

<红黑树并没有我们想象的那么难> 上、下两篇已经完成, 希望能帮助到大家.




  * 红黑树并没有我们想象的那么难(上): [http://daoluan.net/blog/rbtree-is-not-difficult/](http://daoluan.net/blog/rbtree-is-not-difficult/)


  * 红黑树并没有我们想象的那么难(下): [http://daoluan.net/blog/rbtree-is-not-difficult-2/](http://daoluan.net/blog/rbtree-is-not-difficult-2/)


红黑树并没有想象的那么难, 初学者觉得晦涩难读可能是因为情况太多. 红黑树的情况可以通过归结, 通过合并来得到更少的情况, 如此可以加深对红黑树的理解. 网络上的大部分红黑树的讲解因为没有「合并」. 红黑树的五个性质:

[![](http://upload.wikimedia.org/wikipedia/commons/thumb/6/66/Red-black_tree_example.svg/450px-Red-black_tree_example.svg.png)](http://zh.wikipedia.org/wiki/File:Red-black_tree_example.svg)


