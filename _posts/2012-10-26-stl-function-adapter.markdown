---
title: 私房STL之函数配接器
date: 2012-10-26 05:30:37 Z
categories:
- cplusplus
tags:
- C/C++
- "《STL源码剖析》"
author: daoluan
comments: true
layout: post
wordpress_id: 1312
---

本文只通过简单的例子介绍函数配接器是如何工作的。

函数对象直接应用的地方较少，它配合实现一些算法（作为算法的参数），于是便有函数配接器。因为通过函数对象，几乎可以实现我们所要的表达式，那么某些算法也确实可以通过函数对象，来得到我们所预期（把预期放在表达式中）的结果。

<!-- more -->

展示一段代码：


    /*摘自C++ standard STL。*/

    ......
    int ia[] = {11,12,13,1,2,3,4,5,6,7};
    vector<int> iv(ia,ia+10);
    cout << count_if(iv.begin(),iv.end(),bind2nd(less<int>(),10)) << endl;
    ......




<blockquote><p>7<br>
请按任意键继续. . .</p></blockquote>


我们可以试着一步一步展开count_if()函数，


    /*摘自C++ standard STL。*/
    template<class _InIt,
    	class _Pr> inline
    	typename iterator_traits<_InIt>::difference_type
    		count_if(_InIt _First, _InIt _Last, _Pr _Pred)/*这里。*/
    	{	// count elements satisfying _Pred
    	return _Count_if(_CHECKED_BASE(_First), _CHECKED_BASE(_Last), _Pred);
    	}
    /*count_if()的底层函数。*/
    template<class _InIt,
    	class _Pr> inline
    	typename iterator_traits<_InIt>::difference_type
    		_Count_if(_InIt _First, _InIt _Last, _Pr _Pred)
    	{	// count elements satisfying _Pred
    	_DEBUG_RANGE(_First, _Last);
    	_DEBUG_POINTER(_Pred);
    	typename iterator_traits<_InIt>::difference_type _Count = 0;

    	for (; _First != _Last; ++_First)
    		if (_Pred(*_First))
    			++_Count;
    	return (_Count);
    	}


其中，_Pred就是函数对象binder2nd，它在return (std::binder2nd<_Fn2>(_Func, _Val));语句中，被构造出来，同时它重载了“()”操作符，再来看看bind2nd和binder2nd：


    /*摘自C++ standard STL。*/
    		// TEMPLATE CLASS binder2nd
    template<class _Fn2>
    	class binder2nd
    		: public unary_function<typename _Fn2::first_argument_type,
    			typename _Fn2::result_type>
    	{	// functor adapter _Func(left, stored)
    public:
    	typedef unary_function<typename _Fn2::first_argument_type,
    		typename _Fn2::result_type> _Base;
    	typedef typename _Base::argument_type argument_type;
    	typedef typename _Base::result_type result_type;

    	binder2nd(const _Fn2& _Func,
    		const typename _Fn2::second_argument_type& _Right)
    		: op(_Func), value(_Right)
    		{	// construct from functor and right operand
    		}

    	result_type operator()(const argument_type& _Left) const
    		{	// apply functor to operands
    		return (op(_Left, value));
    		}

    	result_type operator()(argument_type& _Left) const
    		{	// apply functor to operands
    		return (op(_Left, value));
    		}

    protected:
    	_Fn2 op;	// the functor to apply
    	typename _Fn2::second_argument_type value;	// the right operand
    	};

    		// TEMPLATE FUNCTION bind2nd
    template<class _Fn2,
    	class _Ty> inline
    	binder2nd<_Fn2> bind2nd(const _Fn2& _Func, const _Ty& _Right)
    	{	// return a binder2nd functor adapter
    	typename _Fn2::second_argument_type _Val(_Right);
    	return (std::binder2nd<_Fn2>(_Func, _Val));
    	}


bind2nd()是**辅助函数**，为的是使用binder2nd（真正的主角）更为方便。

count_if(iv.begin(),iv.end(),bind2nd(less<int>(),10))；中less<int>()在binder12函数对象的构造函数中被作为其内部操作成员（它是一个函数对象）_Fn2 op;

count_if()函数在处理每一个元素的时候，实际调用binder2nd的“()”运算符重载函数，而这个函数当中有调用了其内部操作成员op（其又是一个函数对象less<int>）的“()”运算符重载函数。如此一来，配接成功了。其它的函数配接器做法类似。

**总结就是count_if()调用bind2nd()函数，bind2nd()函数实际产生binder2nd函数对象，返回给count_if()做为参数，count_if()再调用更为底层的函数_Count_if()函数。**

我们从count_if()的源代码可以得知，count_if(iv.begin(),iv.end(),bind2nd(less<int>(),10))；还可以被改写成，


    bool less10(int i)
    {
    	if(i<10)
    		return true;
    	return false;
    }
    ......
    int ia[] = {11,12,13,1,2,3,4,5,6,7};
    vector<int> iv(ia,ia+10);
    cout << count_if(iv.begin(),iv.end(),less10) << endl;
    ......


此时，count_if()中的_Pred就是一函数指针了。所以，函数对象还是可以用一般函数指针替换的。

STL实现的函数配接器：[http://www.cplusplus.com/reference/std/functional/](http://www.cplusplus.com/reference/std/functional/)

本文完 2012-10-26

Dylan [http://daoluan.github.io/](http://daoluan.github.io/)
