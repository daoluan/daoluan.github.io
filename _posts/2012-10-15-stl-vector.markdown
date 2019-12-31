---
title: 私房STL之vector
date: 2012-10-15 16:24:18 Z
categories:
- cplusplus
tags:
- C/C++
- "《STL源码剖析》"
author: daoluan
comments: true
layout: post
wordpress_id: 1149
---

一句话vector：vector的空间可扩充，支持随机存取访问，是一段连续线性的空间。所以它是动态空间，与之对比的array是静态的空间，不可扩充。简单来说，vector是数组的增强版。


### vector创建与遍历


vector提供了几个版本的构造函数。详见：[http://www.cplusplus.com/reference/stl/vector](http://www.cplusplus.com/reference/stl/vector/)

比如：


    vector<int> iv(3,3);	/*3,3,3*/


<!-- more -->

又或：


    ......
    vector<int>::iterator beg = iv.begin(),
    end = iv.end();
    cout << *beg << endl;
    ......




### vector删除


在经常需要删除操作earse()（插入操作也一样insert()）的地方，不建议使用vector容器，因为删除元素会导致内存的复制，无疑增加系统开销。最为极端的情况，删除vector首部的元素：


<blockquote><p><span style="color: #ff0000;">a</span> b c d <span style="color: #000000;">e</span> f g h<br>
<span style="color: #00ccff;">b c d e&nbsp;f g h </span><span style="color: #000000;">h<br>
</span>b c d e&nbsp;f g h</p></blockquote>


当然，有更好的做法，为了避免内存复制，在删除的时候，将需要删除的目标与vector尾端的元素交换，然后才执行删除操作，但这无疑也增加了一个指向vector尾端元素的空间开销。


<blockquote><p><span style="color: #ff0000;">a</span>&nbsp;b c d&nbsp;e&nbsp;f g h<br>
<span style="color: #00ccff;">h</span> b c d&nbsp;e&nbsp;f g <span style="color: #00ccff;">a</span><br>
<span style="color: #00ccff;">h</span> b c d&nbsp;e&nbsp;f g</p></blockquote>




### vector陷阱


需要注意的是，vector备用空间是有限的，当发现备用空间不够用的时候，vector是另外新分配一个比原有更大的空间（原有空间*2），然后把原有的内容倒腾到新的空间上去，接着释放原有的空间。所以迭代器的使用就要特别小心了，在插入元素之后，很可能之前声明定义的迭代器都失效了。


    ......
    vector<int> iv(3,3);

    iv.push_back(10);	/*3,3,3,10*/

    vector<int>::iterator beg = iv.begin(),
    	end = --iv.end();

    cout << iv.size() << " " << *beg << " " << *end << endl;	/*4 3 10*/

    iv.push_back(20);
    cout << iv.size() << " " << *beg << " " << *end << endl;	/*bomb.invalid iterator.*/
    ......


[![](http://daoluan.net/images/blog/2012/10/vector_bomb.gif)](http://daoluan.net/blog/stl-vector/vector_bomb/) bomb！！！


### vector元素排序




    #include <iostream>
    #include <vector>
    #include <algorithm>
    using namespace std;

    int main()
    {
    	vector<int> iv(3,3);
    	unsigned int i;

    	/*add new elem.*/
    	iv.push_back(10);
    	iv.push_back(9);
    	iv.push_back(0);

    	vector<int>::iterator beg = iv.begin(),
    		end = iv.end();

    	/*print.*/
    	for(i=0; i<iv.size(); i++)
    		cout << iv[i] << " ";
    	cout << endl;

    	/*sort.*/
    	sort(beg,end);

    	/*print.*/
    	for(i=0; i<iv.size(); i++)
    		cout << iv[i] << " ";
    	cout << endl;

    	return 0;
    }




<blockquote><p>3 3 3 10 9 0<br>
0 3 3 3 9 10<br>
请按任意键继续. . .</p></blockquote>




### vector查找


按上述遍历元素的方法查找，复杂度为O(n)。STL算法实现了find()，可以在指定的迭代器始末寻找指定的元素。


    ......
    vector<int> iv(3,3);
    unsigned int i;

    /*add new elem.*/
    iv.push_back(10);
    iv.push_back(9);
    iv.push_back(0);

    vector<int>::iterator beg = iv.begin(),
    	end = iv.end(),
    	ret;

    ret = find(beg,end,10);

    cout << *ret << endl;
    ......




### 建议


之于array，vector虽略胜一筹，但有它的硬伤，那就是它动态增大的时候，空间操作耗费大，特别是当vector内的元素很多的时候。

vector还提供insert，earse，clear等元素的操作，不一一复述。最后是很不错的vector文档：[http://www.cplusplus.com/reference/stl/vector/](http://www.cplusplus.com/reference/stl/vector/)

本文完 2012-10-16

Dylan [http://www.daoluan.net/](http://www.daoluan.net/blog/)
