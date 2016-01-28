---
author: daoluan
comments: true
date: 2013-06-30 06:05:52+00:00
layout: post
slug: longest-palindromic-substring
title: 最长回文子串（Longest Palindromic Substring）
wordpress_id: 1775
categories:
- 学习总结
---

一个「对称」的序列，就可称为回文序列，譬如：aba，abba 等。详细介绍参看： [http://zh.wikipedia.org/wiki/%E5%9B%9E%E6%96%87%E6%95%B0](http://zh.wikipedia.org/wiki/%E5%9B%9E%E6%96%87%E6%95%B0)

最长回文子串问题是要求在给出的一个序列中，找到最长的回文字串。譬如：一个序列 cabccba，它的最长回文子串是 abccba。


### 暴力


暴力穷举可以解决问题。三个循环穷举所有可能的序列。


    for i in range(0,len(str))
         for j in range(i,len(str)
                   is_palindromic_number(i,j)//这里有个循环


但算法的复杂度是 O(n^3)。


### 一个更好的思路


在面试的是被问到这个题目，我拙计，下面是当天聊天中给出的思路：


<blockquote><p>2013-06-10</p>
<p>捣乱 9:52:08</p>
<p>开始想到遍历，不放过任何一个回文中心，计算最大回文串，但欠妥，效率低。</p>
<p>回文串的难处在回文串中有回文串。</p>
<p>另一个是用栈，描述一下：</p>
<p>用一个栈，不断往里压串种的元素，如果发现回文串，不压栈而且要弹出栈里的元素，并相应的记录回文串的位置和大小（可用一个数组来存储）</p>
<p><strong>当发现「回文串 1 中存在回文串 2，回文串 3，回文串 4，…回文串 N」的情况，要作检测，具体是看回文串 2 和回文串 N ，回文串 3 和回文串 N-1 是否对称且相等。</strong>譬如：</p>
<p>d abc cba abc cba d</p>
<p>是回文串中有回文串的情况。</p>
<p>abc 和 cba 是回文串，接下来的又是一样。所以后来栈是这样：d，只剩一个元素，并且还有一个 d 准备压栈，但压栈的时候发现：因为 dd 是回文又之前处理出现了回文，因此要检测 dd 范围内的回文是否对称且相等。</p>
<p>这种方法有穷举的嫌疑，但规避了很多不合题意的情况。</p></blockquote>


上面的做法不稳定，因为其中的回溯过程（加粗部分）。


### Manacher 线性算法


利用一个辅助数组 arr[n]，其中 arr[i] 记录的是以 str[i] 为中心的回文子串长度。当计算 arr[i] 的时候，arr[0...i-1] 是已知并且可被利用的。Manacher 核心在于：**用 mx 记录之前计算的最长的回文子串长度所能到达的最后边界，用 id 记录其对应的中心，可以利用回文子串中的回文子串信息。**

![lps02](http://md.daoluan.net/images/blog/2013/06/lps02.png)

假设 id 与 mx 已经得出，当计算以 str[i] 为中心回文子串长度时，因为已经可以确定绿色部分已经是回文子串了，所以可以利用以 str[j] 为中心回文子串长度即 arr[j]。在上图的情况下，所以可以从箭头所指出开始比较。还有一种情况：

[![lps01](http://md.daoluan.net/images/blog/2013/06/lps01.png)](http://md.daoluan.net/images/blog/2013/06/lps01.png)

这种情况下，不能直接利用以 str[j] 为中心回文子串长度即 arr[j]，因为以 id 为中心回文子串长度只计算到了绿色箭头所指之处，所以能力利用的信息是 mx-i，比较 mx-i 之后的字符。

下面个举一例：

0123456789

ceabadabac

1112141?

当计算「？」即 arr[7] 的时候，id = 5,mx = 8，所以 arr[7] 可以给一个初值为 arr[2*id-7=3]=2，并且比较 str[7-2] 与 str[7+2] 是否相等......

0123456789

cdabadabac

1113141?

当计算「？」即 arr[7] 的时候，id = 5,mx = 8，此时 arr[7] 不能赋 arr[2*id-7=3]=3 的初值，因为以 id 为中心的回文子串只为图中蓝色部分：[![lps03](http://md.daoluan.net/images/blog/2013/06/lps03.png)](http://md.daoluan.net/images/blog/2013/06/lps03.png) 。所以，arr[7] 只能赋值为 mx-i = 8-7 = 1，继续比较以更新 arr[7]。

Manacher 线性算法只要在纸上演算一遍就明白了。

从上面的描述，Manacher 算法只扫描了一遍，在具体计算中，借用了历史数据以更快的速度算出当下的结果，从而避免重复的比较，因此是线性的？！（笔者还无法证明）

下面是 Python 的算法描述：


    str = "abcdcba "
    str = "#" + "#".join(str) + "#"
    print str

    i = 0
    mx = 0
    id = 0
    p = [0 ] * len(str)
    while i<len(str):
        if mx > i:
            p[i] = min(p[ 2*id-i],mx-i)
        else:
            p[i] = 1

        while i-p[i] >=0 and i+p[i] < len(str) and str[i-p[i]]==str[i+p[i]]:
            p[i] += 1

        if mx < p[i]+i:
            mx = p[i] + i
            id = i
        i+=1

    print p


#a#b#c#d#c#b#a#

[1, 2, 1, 2, 1, 2, 1, 8, 1, 2, 1, 2, 1, 2, 1]

一个小 trick 是在原串中穿插字符「#」，可以将统一奇数回文串和偶数回文串的情况。

捣乱 2013-06-30

http://daoluan.net
