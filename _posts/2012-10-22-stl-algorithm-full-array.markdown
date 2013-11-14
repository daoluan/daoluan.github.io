---
author: daoluan
comments: true
date: 2012-10-22 00:50:05+00:00
layout: post
slug: stl-algorithm-full-array
title: 私房STL算法之全排列
wordpress_id: 1247
categories:
- C/C++
tags:
- C/C++
- 《STL源码剖析》
---

全排列问题：从n个不同元素中任取m（m≤n）个元素，按照一定的顺序排列起来，叫做从n个不同元素中取出m个元素的一个排列。当m＝n时所有的排列情况叫全排列。譬如，考虑\{a，b，c\}的全排列有abc，acb，bac，bca，cab，cba六（3！）种情况。

首先要声明，STL没有实现全排列的函数，但描述了全排列的核心算法，分别是[next\_permutation](http://www.cplusplus.com/reference/algorithm/next\_permutation/)和[prev\_permutation](http://www.cplusplus.com/reference/algorithm/prev\_permutation/)，两者实际上一样，只不过情况不同。全排列实现可以是递归和迭代两个版本。STL算法中的next\_permutation便也是全排列算法迭代版本的核心。

<!-- more -->


### 递归实现全排列


递归实现全排列是一个经典的算法。

    
    /*全排列递归版本*/
    void foo1(char *str,int k,int n)
    \{
    	if(k == n)	//	print str when it reaches the last character.
    	\{
    		cout << str << " ";
    		return;
    	\}//	if
    
    	for(int i=k; i<n; i++)
    	\{
    		swap(str[k],str[i]);
    		foo1(str,k+1,n);	//	next character.
    		swap(str[k],str[i]);
    	\}//	for
    \}




> abcd abdc acbd acdb adcb adbc bacd badc bcad bcda bdca bdac cbad cbda cabd cadb
cdab cdba dbca dbac dcba dcab dacb dabc 请按任意键继续. . .




### 迭代实现全排列


因为[next\_permutation](http://www.cplusplus.com/reference/algorithm/next\_permutation/)和[prev\_permutation](http://www.cplusplus.com/reference/algorithm/prev\_permutation/)实际上换汤不换药，因此只描述[next\_permutation](http://www.cplusplus.com/reference/algorithm/next\_permutation/)算法。在下笔之前，next\_permutation()函数的作用是取下一个排列组合。同样，考虑\{a，b，c\}的全排列：abc，acb，bac，bca，cab，cba，以“bac”作为参考，那么next\_permutation()所得到的下一个排列组合是bca，prev\_permutation()所得到的前一个排列组合是“acb”，之于“前一个”和“后一个”，是按字典进行排序的。

next\_permutation()算法描述：



	
  1. 从str的尾端开始逆着寻找相邻的元素，*i和*ii，满足*i<*ii；

	
  2. 接着，又从str的尾端开始逆着寻找一元素，*j，满足*i<*j（*i从步骤一中得到）；

	
  3. swap(*i,*j)；

	
  4. 将*ii之后（包括*ii）的所有元素逆转。


举个例子，需要找到“01324”的下一个排列，找到*i=2，*ii=4，*j=4，下一个排列即“01342”。再来找到“abfedc”的下一个排列，找到*i=b，*ii=f，*j=c，swap操作过后为“acfedb”，逆转操作过后为“acbdef”。

    
    /*全排列迭代归版本*/
    void reverse(char *str)
    \{
    	int len = strlen(str),i;
    	for(i=0; i<len/2; i++)
    		swap(*(str+i),*(str+len-1-i));
    \}
    
    /*阶乘*/
    int factorial(int n)
    \{
    	if(n == 1)	return 1;
    	return n * factorial(n-1);
    \}
    
    void foo2(char *p)
    \{
    	int len = strlen(p),cnt = 1;
    	char *i,*ii,*j;
    
    	cout << p << " ";
    
    	/*STL <algorithm> next\_permutation()函数的核心算法*/
    	while(++cnt <= factorial(len))
    	\{
    		i = p + len - 2,ii = p + len - 1,j = ii;
    		while(*i >= *ii)	i--,ii--;	/*find *i and *ii.*/
    		while(*i >= *j)	j--;			/*find *j.*/
    
    		swap(*i,*j);		/*swap.*/
    
    		reverse(ii);		/*reverse.*/
    		cout << p << " ";
    	\}//	while
    \}




> abcd abdc acbd acdb adbc adcb bacd badc bcad bcda bdac bdca cabd cadb cbad cbda
cdab cdba dabc dacb dbac dbca dcab dcba 请按任意键继续. . .


prev\_permutation()函数做法是一样的。

本文完 2012-10-22

捣乱小子 [http://www.daoluan.net/](http://www.daoluan.net/)
