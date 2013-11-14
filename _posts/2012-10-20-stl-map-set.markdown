---
author: daoluan
comments: true
date: 2012-10-20 12:24:04+00:00
layout: post
slug: stl-map-set
title: 私房STL之map和set
wordpress_id: 1218
categories:
- C/C++
tags:
- C/C++
- 《STL源码剖析》
---

一句话set：容器set底层是由RB_TREE实现的，它和（deque--->stack、queue）模式一样；色set的元素不允许重复；set中键值就是实值，实值就是键值，而键值是不可以更改的（但MS STL不这样做），所以set不允许对其中的元素进行更新；

一句话map：容器map底层也由RB_TREE实现，它和（deque--->stack、queue）模式一样；map中一个键值对应一个实值，不允许键值上的重复，内部是按键值来进行排序存储的，其中键值不允许被更改。

[caption id="" align="aligncenter" width="450"][![](http://upload.wikimedia.org/wikipedia/commons/thumb/6/66/Red-black_tree_example.svg/450px-Red-black_tree_example.svg.png)](http://zh.wikipedia.org/wiki/%E7%BA%A2%E9%BB%91%E6%A0%91) 红黑树[/caption]

<!-- more -->

网络上有关于红黑树详细的解说，特别是复杂的红黑树元素操作算法，推荐@[JULY](http://weibo.com/julyweibo?s=6cm7D0) 的文章：[http://blog.csdn.net/v_JULY_v/article/details/6105630](http://blog.csdn.net/v_JULY_v/article/details/6105630)。本文主要介绍STL set/map的用法和笔者对其在实现上技巧实现技法的摘录，欢迎斧正。


### **AVL 树和 RB 树区别**


AVL 从概念可以知道它是高度平衡的树，所以会涉及较多的调整步骤，导致在 insert 或者 erase 操作树的时候，效率不高。但 RB 树可以规避这个问题，有更高的效率， 也就是 RB 树并非高度平衡的树。


### set和map的创建与遍历


set和map都是由非线性空间来存储的，属于Bidrectional Iterator;测试添加元素的时候，故意添加已存在的键值，发现被拒绝，RB_TREE内部有insert_equal()和insert_unique()两个版本，set/map都调用后者。

set：

    
    ......
    set<int> is;
    
    is.insert(7);
    is.insert(5);
    is.insert(6);
    is.insert(4);
    is.insert(3);
    
    is.insert(3);	/*here.*/
    set<int>::iterator beg = is.begin(),
    	end = is.end(),ite;
    
    for(ite = beg; ite != end; ite++)
    	cout << *ite << " ";
    cout << endl;/*3 4 5 6 7*/
    ......


map：

    
    map<int,int> im;
    
    im.insert(pair<int,int>(7,700));
    im.insert(pair<int,int>(5,500));
    im.insert(pair<int,int>(6,600));
    im.insert(pair<int,int>(4,400));
    im.insert(pair<int,int>(3,300));
    
    im.insert(pair<int,int>(3,300));	/*here.*/
    
    map<int,int>::iterator beg = im.begin(),
    	end = im.end(),ite;
    
    for(ite = beg; ite != end; ite++)
    	cout << "<" <<ite->first << " " << ite->second << ">" << " ";
    cout << endl;	/*<3 300> <4 400> <5 500> <6 600> <7 700>*/




### set和map的查找


RB_TREE本身就是一个搜索树，加之它能时刻保持良好的平衡，所以查找效率高。set和map内部**已经实现**了find()查找。而STL <algorithm>find()效率低很多。


### 有趣的实现


在insert()函数中，会经常用到pair这个结构体，里头有两个元素：第一元素被作为键值，第二元素被作为实值。

    
    /*摘自MS STL。*/
    
    		// TEMPLATE STRUCT pair
    template<class _Ty1,
    	class _Ty2> struct pair
    	{	// store a pair of values
    	typedef pair<_Ty1, _Ty2> _Myt;
    	typedef _Ty1 first_type;
    	typedef _Ty2 second_type;
    
    	pair()
    		: first(_Ty1()), second(_Ty2())
    		{	// construct from defaults
    		}
    	......
    	_Ty1 first;	// the first stored value
    	_Ty2 second;	// the second stored value
    	};


有趣的地方是，它不仅仅用在insert()的参数中，还应用在insert()的返回值和map的“[]”运算符重载中。

    
    typedef pair<iterator, bool> _Pairib;
    ......
    _Pairib insert(const value_type& _Val);


所以在insert()过后，如果插入成功，_Pairib的iterator会指向元素插入的位置，bool被置为true；否则，iterator指向重复的元素的位置，且bool为false.所以，“[]”重载函数可以通过insert()间接实现的。但在MS STL中，它没有采用这种方法，其内部虽也通过insert()间接实现，但其采用以map<T1,T2>::iterator为返回值的insert()版本。

    
    mapped_type& operator[](const key_type& _Keyval)
    	{	// find element matching _Keyval or insert with default mapped
    	iterator _Where = this->lower_bound(_Keyval);
    	if (_Where == this->end()
    		|| this->comp(_Keyval, this->_Key(_Where._Mynode())))
    		_Where = this->insert(_Where,
    			value_type(_Keyval, mapped_type()));
    	return ((*_Where).second);
    	}




### 一个关于set的疑问


**set中键值就是实值，实值就是键值**。既然这样，set中的元素就不允许被修改，一个测试：**实践证明，set中的元素允许被改变，改变后，set内部对其视若无睹。**

    
    set<int> is;
    
    is.insert(7);
    is.insert(5);
    is.insert(6);
    is.insert(4);
    is.insert(3);
    
    is.insert(3);
    
    /*3 4 5 6 7*/
    
    set<int>::iterator beg = is.begin(),
    	end = is.end(),ite;
    
    *beg = 8;	
    
    for(ite = beg; ite != end; ite++)
    	cout << *ite << " ";
    cout << endl;	/*8 4 5 6 7*//*居然可以修改，吓shi了*/
    
    is.insert(100);
    
    for(ite = beg; ite != end; ite++)
    	cout << *ite << " ";
    cout << endl;	/*8 4 5 6 7 100*//*居然也不维护一下，吓shi了*/


原来是set的iterator迭代器被声明为一般的iterator，而不是const。

    
    /*摘自MS STL。*/
    typedef typename _Mybase::iterator iterator;


不仅如此，在set的模板声明中也可以看出端倪：

    
    /*摘自MS STL。*/
    template<class _Kty,
    	class _Pr = less<_Kty>,
    	class _Alloc = allocator<_Kty> >
    	class set
    		: public _Tree<_Tset_traits<_Kty, _Pr, _Alloc, false> >
    	{	// ordered red-black tree of key values, unique keys


所以如果需要禁止用户通过迭代器修改键值，那么可以将迭代器声明为const：（笔者认为这样可行的）

    
    typedef typename _Mybase::const_iterator iterator;


而map把关得很好，它强行将pair中的第一元素（注意，只是第一元素而已）定义为const：

    
    /*摘自MS STL。*/
    template<class _Kty,
    	class _Ty,
    	class _Pr = less<_Kty>,
    	class _Alloc = allocator<pair<const _Kty, _Ty> > >
    	class map
    		: public _Tree<_Tmap_traits<_Kty, _Ty, _Pr, _Alloc, false> >
    	{	// ordered red-black tree of {key, mapped} values, unique keys
    ......


本文的后部分需要对STL源码有一定的了解。

本文完 2012-10-16

捣乱小子 [http://www.daoluan.net/](http://www.daoluan.net/)
