---
title: 2012腾讯实习招聘笔试附加题
date: 2012-11-04 08:17:12 Z
categories:
- 编程小记
- 随笔
tags:
- 巴什博弈
- 编程小记
author: daoluan
comments: true
layout: post
wordpress_id: 1419
---

2012腾讯实习招聘笔试附加题1，问题描述大致如下：


<blockquote>一个数组a[n],求构造出一个b[n],使得b[i]=a[0]*a[1]*...a[n-1]/a[i];不能用除法，除了循环变量外 不能用额外的变量 ，要求O(1)的空间复杂度，O(n)的时间复杂度。</blockquote>


<table cellpadding="0" cellspacing="0" border="1" >
<tbody >
<tr >

<td width="38" valign="top" >**b[0]**
</td>

<td width="22" valign="top" >
</td>

<td width="22" valign="top" >2
</td>

<td width="22" valign="top" >3
</td>

<td width="22" valign="top" >4
</td>

<td width="22" valign="top" >5
</td>

<td width="22" valign="top" >6
</td>

<td width="22" valign="top" >7
</td>

<td width="22" valign="top" >8
</td>

<td width="22" valign="top" >9
</td>

<td width="29" valign="top" >10
</td>
</tr>
<tr >

<td width="38" valign="top" >**b[1]**
</td>

<td width="22" valign="top" >1
</td>

<td width="22" valign="top" >
</td>

<td width="22" valign="top" >3
</td>

<td width="22" valign="top" >4
</td>

<td width="22" valign="top" >5
</td>

<td width="22" valign="top" >6
</td>

<td width="22" valign="top" >7
</td>

<td width="22" valign="top" >8
</td>

<td width="22" valign="top" >9
</td>

<td width="29" valign="top" >10
</td>
</tr>
<tr >

<td width="38" valign="top" >**b[2]**
</td>

<td width="22" valign="top" >1
</td>

<td width="22" valign="top" >2
</td>

<td width="22" valign="top" >
</td>

<td width="22" valign="top" >4
</td>

<td width="22" valign="top" >5
</td>

<td width="22" valign="top" >6
</td>

<td width="22" valign="top" >7
</td>

<td width="22" valign="top" >8
</td>

<td width="22" valign="top" >9
</td>

<td width="29" valign="top" >10
</td>
</tr>
<tr >

<td width="38" valign="top" >**b[3]**
</td>

<td width="22" valign="top" >1
</td>

<td width="22" valign="top" >2
</td>

<td width="22" valign="top" >3
</td>

<td width="22" valign="top" >
</td>

<td width="22" valign="top" >5
</td>

<td width="22" valign="top" >6
</td>

<td width="22" valign="top" >7
</td>

<td width="22" valign="top" >8
</td>

<td width="22" valign="top" >9
</td>

<td width="29" valign="top" >10
</td>
</tr>
<tr >

<td width="38" valign="top" >**b[4]**
</td>

<td width="22" valign="top" >1
</td>

<td width="22" valign="top" >2
</td>

<td width="22" valign="top" >3
</td>

<td width="22" valign="top" >4
</td>

<td width="22" valign="top" >
</td>

<td width="22" valign="top" >6
</td>

<td width="22" valign="top" >7
</td>

<td width="22" valign="top" >8
</td>

<td width="22" valign="top" >9
</td>

<td width="29" valign="top" >10
</td>
</tr>
<tr >

<td width="38" valign="top" >**b[5]**
</td>

<td width="22" valign="top" >1
</td>

<td width="22" valign="top" >2
</td>

<td width="22" valign="top" >3
</td>

<td width="22" valign="top" >4
</td>

<td width="22" valign="top" >5
</td>

<td width="22" valign="top" >
</td>

<td width="22" valign="top" >7
</td>

<td width="22" valign="top" >8
</td>

<td width="22" valign="top" >9
</td>

<td width="29" valign="top" >10
</td>
</tr>
<tr >

<td width="38" valign="top" >**b[6]**
</td>

<td width="22" valign="top" >1
</td>

<td width="22" valign="top" >2
</td>

<td width="22" valign="top" >3
</td>

<td width="22" valign="top" >4
</td>

<td width="22" valign="top" >5
</td>

<td width="22" valign="top" >6
</td>

<td width="22" valign="top" >
</td>

<td width="22" valign="top" >8
</td>

<td width="22" valign="top" >9
</td>

<td width="29" valign="top" >10
</td>
</tr>
<tr >

<td width="38" valign="top" >**b[7]**
</td>

<td width="22" valign="top" >1
</td>

<td width="22" valign="top" >2
</td>

<td width="22" valign="top" >3
</td>

<td width="22" valign="top" >4
</td>

<td width="22" valign="top" >5
</td>

<td width="22" valign="top" >6
</td>

<td width="22" valign="top" >7
</td>

<td width="22" valign="top" >
</td>

<td width="22" valign="top" >9
</td>

<td width="29" valign="top" >10
</td>
</tr>
<tr >

<td width="38" valign="top" >**b[8]**
</td>

<td width="22" valign="top" >1
</td>

<td width="22" valign="top" >2
</td>

<td width="22" valign="top" >3
</td>

<td width="22" valign="top" >4
</td>

<td width="22" valign="top" >5
</td>

<td width="22" valign="top" >6
</td>

<td width="22" valign="top" >7
</td>

<td width="22" valign="top" >8
</td>

<td width="22" valign="top" >
</td>

<td width="29" valign="top" >10
</td>
</tr>
<tr >

<td width="38" valign="top" >**b[9]**
</td>

<td width="22" valign="top" >1
</td>

<td width="22" valign="top" >2
</td>

<td width="22" valign="top" >3
</td>

<td width="22" valign="top" >4
</td>

<td width="22" valign="top" >5
</td>

<td width="22" valign="top" >6
</td>

<td width="22" valign="top" >7
</td>

<td width="22" valign="top" >8
</td>

<td width="22" valign="top" >9
</td>

<td width="29" valign="top" >
</td>
</tr>
</tbody>
</table>
<!-- more -->

关键不能使用除法，不能使用循环额外的变量，空间复杂的O(1)，时间复杂度O(n)。已上眼，倘若没有上述条件约束，可以在时间复杂度O(n)内完成。

先关注上面表格中的左下角，b[i]的部分乘积可以由b[i-1]间接求出。譬如：（不考虑右上角的乘积，只考虑左下角）b[2] = b[1] * a[1] ，以此类推。于是：


    for i = [1,n]
    	b[i] *= b[i-1] * a[i-1];


再把焦点放在右上角，右上角部分从下往上看，也可以由上面的思路得到结果。但此时，我们似乎要打一个擦边球，借助一个外围的变量。


    for i = [n-2,0],temp *= a[i+1]
    	b[i] *= temp;


于是分右下角和左上角分别处理，可以满足“空间复杂的O(1)，时间复杂度O(n)”的条件（条件好苛刻）。

有下面的代码：


    int main()
    {
    #define  N 10
    	int a[N],b[N];
    	for(int i=0; i<10; i++)
    		a[i] = i+1,
    		b[i] = 1;

    	for(int i=1; i<N; i++)
    		b[i] *= b[i-1] * a[i-1];

    	for(int i=N-2,temp = 1; temp *= a[i+1],i>=0; i--)
    		b[i] *= temp;

    	for(int i=0; i<N; i++)
    		cout << b[i] << " ";
    	cout << endl;

    	return 0;
    }




<blockquote><p>3628800 1814400 1209600 907200 725760 604800 518400 453600 403200 362880<br>
请按任意键继续. . .</p></blockquote>


我只能帮到这里了，如果有更好的方法，拭目以待。

本文完 2012-11-4

Dylan [http://daoluan.github.io/](http://daoluan.github.io/)


<blockquote></blockquote>
