---
author: daoluan
comments: true
date: 2012-10-28 05:15:20+00:00
layout: post
slug: stl-iterator
title: 私房STL之迭代器
wordpress_id: 1341
categories:
- cplusplus
tags:
- C/C++
- 《STL源码剖析》
---

STL表现的如此出色的，迭代器（iterator）做出了很大的贡献，功不可没。

一个数据元有多重表示方式，包括：实体（它自己），指针，引用；另外，还有两个与数据元属性相关的类型：间距（即两个数据元之间的关系）和其移动特性与施行方式的类型。迭代器中包含了这上述五种与数据元先关的描述，所以迭代器能够很充分的表示和操控一个数据元。迭代器本身只能表示操作数据元，但是它没有含括任何的数据元数据，就似电视机和遥控器之间的关系，遥控器（迭代器）只是能够切换不同的频道，但是它不含括电视机（数据元）。

<!-- more -->

这里不单独描述迭代器，它个单不是一独的个体，放在其所属的大框架中，更能体现它的作用和执行机制。

STL中会定义迭代器：

    
    template <class _Ty>		/*_Ty：节点元素类型。*/
    struct container_iterator
    {
    	/*五种与数据元先关的描述。*/
    	......
    	typedef container_iterator<_Ty> iterator;
    
    	typedef bidirectional_iterator_tag itetator_category;
    	typedef _Ty value_type;
    	typedef Node<_Ty>* link_type;
    	typedef size_t size_type;
    	typedef ptrdiff_t difference_type;
    
    	link_type node;
    
    	/*迭代器构造函数。*/
    	......
    	container_iterator(link_type x):node(x){}
    	...
    	......
    
    	/*迭代器行为*/
    	/*+,-,++,--,+=,-=,->,&,[]等运算符重载各取所需 */
    };


[caption id="attachment_1344" align="aligncenter" width="334"][![](http://daoluan.net/blog/wp-content/uploads/2012/10/iterator_op.jpg)](http://daoluan.net/blog/stl-iterator/iterator_op/) iterator_op[/caption]

从中看出，迭代器不包含数据实体，它只是能表现和操作数据实体。因为上述container_iterator操控的的实现，因此当手头有一container_iterator的时候，你可以“*ite”来获得数据元的引用，可以“ite->”获得数据元的指针，“++”可以另ite自动前进一步，“--”可以另ite后退一步。。。

通过模板，迭代器可以为任何数据元服务。一个有趣的地方便是迭代器的构造函数：

    
    container_iterator(link_type x):node(x){}


在container（以下展示）的元素操作当中，很多时候会直截返回指向数据元的指针，**这时可能此操作的函数可能需要返回的是container_iterator类型，**而不是返回一个指向数据元的指针（这种做法不上道，太龌龊），于是会临时构造（调用迭代器的构造函数）一个迭代器作为返回值。

意即：

    
    class Node  
    {  
    public:  
    	Node(int nAge = 0)  
    	{  
    		m_nAge = nAge;  
    	}  
    	......
    private:  
    	int m_nAge;  
    };  
    
    Node foo(int i)
    {
    	return i;	/*直截返回一个int，但Node有Node(int)构造函数，因此会临时构造一个Node对象返回。*/
    }
    
    int main()
    {	
    	Node i = foo(2);
    	return 0;
    }


下面是container：

    
    template <class _Ty,class alloc>		/*T：节点元素类型。*/
    class container
    {
    	/*container数据结构*/
    	typedef container_iterator<_Ty> iterator;
    	typedef const container_iterator<_Ty> const_iterator;
    
    	typedef Node<_Ty>* link_type;
    
    	typedef _Ty value_type;
    	typedef Node<_Ty>* link_type;
    	typedef size_t size_type;
    	typedef ptrdiff_t difference_type;
    
    private:
    	link_type head;		/*头指针。*/
    	link_type tail;		/*为指针。*/
    
    	iterator begin();
    	iterator end();
    
    	bool empty();
    	size_type size()const ;
    	......
    
    	/*元素的操作。push_front,push_back,pop_front,pop_back,insert,earse等根据容器的不同各取所需。*/
    	iterator insert(const _Ty& x);
    	iterator earse(iterator position);
    	void push_back(const _Ty& x);
    	void push_front(const _Ty& x);
    	void pop_back();
    	void pop_front();
    	......
    };


container内部实现的大多数是元素的操作函数，它们有充分利用container_iterator，包括container_iterator内部实现的各种元素的操控（++，--，*，->等等）。

container和container_iterator就是这样结合起来的。还剩下一STL中的镇库之宝：算法。**通用的的算法中，**少不了迭代器。如何能做到通用？不同的容器对应不同的迭代器，那是否对于一个算法，要实现多个迭代器的版本？不，不需要，这就是**泛化编程**的好处，根据传入的迭代器（一般的STL算法会以迭代器作为参数）来推导出相应的迭代器类型。以最为简单的find()算法为例：会通过_InIt _First来推导出迭代器的类型，推导出迭代器的类型，也就推导出了相应的容器。

    
    /*摘自c++ standard library。*/
    template<class _InIt, class _Ty>
    inline
    _InIt find(_InIt _First, _InIt _Last, const _Ty& _Val)
    {	// find first matching _Val
    	_ASSIGN_FROM_BASE(_First,
    		_Find(_CHECKED_BASE(_First), _CHECKED_BASE(_Last), _Val));
    	return (_First);
    }
    
    template<class _InIt, class _Ty>
    inline
    _InIt _Find(_InIt _First, _InIt _Last, const _Ty& _Val)
    {	// find first matching _Val
    	_DEBUG_RANGE(_First, _Last);
    	for (; _First != _Last; ++_First)
    		if (*_First == _Val)
    			break;
    	return (_First);
    }


我们看到，迭代器在算法中的表现，++，--，==。。。。

故迭代器和算法模块结合了。STL中迭代器，容器，算法三足鼎立，整体上通力合作，细微之处不乏各司其职。妙哉！妙哉！

本文完 2012-10-28

捣乱小子 [http://www.daoluan.net/](http://www.daoluan.net/)
