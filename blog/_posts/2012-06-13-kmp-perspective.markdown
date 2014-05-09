---
author: daoluan
comments: true
date: 2012-06-13 16:43:00+00:00
layout: post
slug: kmp-perspective
title: 【字符串匹配】KMP算法之道
wordpress_id: 498
categories:
- 算法
tags:
- 《算法导轮》学习总结
---

修订于2012-06-18，心急的读者可以着重看“有趣的字符串匹配提示”，这个例子看懂了，KMP也就差不多了。


# 闲话




<blockquote>上午算法考试的时候，感觉OK，前一两星期幸好把图算法都吃透了一遍，复习的时候节省了时间:)。前一半考题不理解背书的都可以，有几题没记过，不靠谱地照着理解写下来。最后的吹水题让我想起了之前的比赛，有一题是曹老师给的实验题，刚好比赛上出现了，而且相似度极高。要是高考，曹老师可就红了:)。这也让我捡了便宜。

我们校区2012的招生计划出来了，结果我们校区悲催到只招30个法语本科生，也就是说2012的本科孩子只有30人。不知道法语的怎么看，但对这个校区的未来，我是看不到什么希望。“坑爹啊...”</blockquote>


有趣的字符串匹配“提示”

对于T=abaabab，P=abab，从T的第一个字符开始匹配：
<table cellpadding="2" width="224" cellspacing="0" border="0" >
<tbody >
<tr >

<td width="33" valign="top" >
</td>

<td width="28" valign="top" >a
</td>

<td width="29" valign="top" >b
</td>

<td width="27" valign="top" >a
</td>

<td width="28" valign="top" >a
</td>

<td width="26" valign="top" >b
</td>

<td width="26" valign="top" >a
</td>

<td width="25" valign="top" >b
</td>
</tr>
<tr >

<td width="33" valign="top" >
</td>

<td width="29" valign="top" >a
</td>

<td width="30" valign="top" >b
</td>

<td width="28" valign="top" >a
</td>

<td width="29" valign="top" >b
</td>

<td width="27" valign="top" >
</td>

<td width="26" valign="top" >
</td>

<td width="26" valign="top" >
</td>
</tr>
<tr >

<td width="33" valign="top" >第一次匹配
</td>

<td width="29" valign="top" >1
</td>

<td width="30" valign="top" >2
</td>

<td width="28" valign="top" >3
</td>

<td width="29" valign="top" >0
</td>

<td width="28" valign="top" >
</td>

<td width="26" valign="top" >
</td>

<td width="27" valign="top" >
</td>
</tr>
</tbody>
</table>
可以看到，第四个字符已经匹配失败了。此时如果采用最朴素的算法，也就是重新从第二字符开始匹配（不画表了）。

KMP是这样做的：既然上面第四个字符已经匹配失败了，那么可以试着从已经匹配成功的前三个字符（即上面的“aba”）找到既是“aba”的后缀又是“aba”的前缀的字串，要求是此字串长度应该是所有满足条件中最大的，暂且记为π(“aba”)。很显然，π(“aba”)=1，因为

a b a
      a b a

因此猜测从第三个字符开始匹配可能会成功**（其实应该是从第四个字符开始匹配，因为π(“aba”)=1已经暗示第三个字符“a”匹配成功）**（猜测，只是猜测而已）
<table cellpadding="2" width="224" cellspacing="0" border="0" >
<tbody >
<tr >

<td width="33" valign="top" >
</td>

<td width="28" valign="top" >a
</td>

<td width="29" valign="top" >b
</td>

<td width="27" valign="top" >a
</td>

<td width="28" valign="top" >a
</td>

<td width="26" valign="top" >b
</td>

<td width="26" valign="top" >a
</td>

<td width="25" valign="top" >b
</td>
</tr>
<tr >

<td width="34" valign="top" >第一次匹配
</td>

<td width="28" valign="top" >a
</td>

<td width="30" valign="top" >b
</td>

<td width="28" valign="top" >a
</td>

<td width="29" valign="top" >b
</td>

<td width="27" valign="top" >
</td>

<td width="27" valign="top" >
</td>

<td width="26" valign="top" >
</td>
</tr>
<tr >

<td width="33" valign="top" >第二次匹配
</td>

<td width="28" valign="top" >
</td>

<td width="30" valign="top" >
</td>

<td width="28" valign="top" >a
</td>

<td width="29" valign="top" >b

</td>

<td width="28" valign="top" >a
</td>

<td width="27" valign="top" >b
</td>

<td width="26" valign="top" >
</td>
</tr>
</tbody>
</table>
好吧，结果是不成功，因为出现了T中的第四个字符匹配失败的情况。不过可以发现，KMP算法没有像朴素算法那样，从T的第二个字符开始匹配，转而从T的第三个字符开始匹配，那为什么不从第二个字符开始匹配呢，**因为从T的第三个字符开始匹配才有可能是成功的。如果你认为（或者说你有足够的证据证明）从第二字符开始匹配会成功，那么上面找“既前缀又后缀”的结果：**

a b a
   a b a 

即π(“aba”)=2应该是成立的，很明显不是。

好吧，这里不成功, 前面成功匹配的字符没有, 因此 π(null)=0.这逼着从T的第四个字符开始匹配，也是不成功：
<table cellpadding="2" width="224" cellspacing="0" border="0" >
<tbody >
<tr >

<td width="33" valign="top" >
</td>

<td width="28" valign="top" >a
</td>

<td width="29" valign="top" >b
</td>

<td width="27" valign="top" >a
</td>

<td width="28" valign="top" >a
</td>

<td width="26" valign="top" >b
</td>

<td width="26" valign="top" >a
</td>

<td width="25" valign="top" >b
</td>
</tr>
<tr >

<td width="34" valign="top" >第一次匹配
</td>

<td width="28" valign="top" >
</td>

<td width="30" valign="top" >
</td>

<td width="28" valign="top" >a
</td>

<td width="29" valign="top" >b
</td>

<td width="27" valign="top" >
</td>

<td width="27" valign="top" >
</td>

<td width="26" valign="top" >
</td>
</tr>
<tr >

<td width="33" valign="top" >第二次匹配
</td>

<td width="28" valign="top" >
</td>

<td width="30" valign="top" >
</td>

<td width="28" valign="top" >
</td>

<td width="29" valign="top" >a

</td>

<td width="28" valign="top" >b
</td>

<td width="27" valign="top" >a
</td>

<td width="26" valign="top" >b
</td>
</tr>
</tbody>
</table>
于是匹配成功。你将看到KMP也是这么做的，关键是如何计算上面的说的“既前缀又后缀”的结果——其实就是帮助匹配的辅助表。


# KMP算法之道




<blockquote>问题定义：

字符串匹配问题：T=“www.daoluan.net/blog”，P=“daoluan”，问P是否在T中出现？答：是。</blockquote>


之前遇到的字符串匹配算法效率不是很看好，有限自动机之于最为朴素的穷举法有一定的提高，但是初始化过程仍不乐观，总体效率不高。奇葩的是，KMP算法初始化和匹配过程分别可以达到O(n)和O(m)，实在是神奇。本篇文章目的就是吃透KMP。纵观KMP，它无非就基于三个核心的结论，吃透这个三个结论，将KMP踩在脚下。

KMP和有限自动机字符串匹配一样，借助了一个辅助一维表，但KMP的辅助表计算时间在O(m)内。这个辅助表是关于匹配内容P的前缀表。

在提及这些结论之前，先允许我啰嗦一下：


<blockquote>对于字串P，(k)P表示长度k的P的前缀；P(k)表示长度为k的P的后缀。比如P=abcdef，(3)P=abc，P(3)=def。

π(q)表示P的前缀(q)P的最长后缀P(k)的长度（也就是k要取最大值）。比如：P=ababababca，π(8)即(8)P=abababab的最长后缀P(k)的长度，k最大为6，因为

abababab|ca
ababab|abca

∴π(8)=6。</blockquote>


比如：匹配内容P=“daodaodaodaoluan”，那么关于P的前缀表 π(i) 即为：

P** d a o d a o d a o d a o l  u a n  **
π** 0 0 0 1 2 3 4  5 6 7 8 9 0 0 0 0**


<blockquote>π(q)有了定义，π*(q)可以有。通常加“*”表示所有，在这里也是。π*(q)是一个集合，它的所有成员可以迭代求出：

π*(q)={k|(k)P是(q)P的后缀且k<q}

={π1(q)，π2(q)，π3(q)，π4(q)....}，其中πn(q)=π[πn-1(q)]。</blockquote>


比如：同样对P=ababababca，求π*(8)， 有下图结果（来自算法导论）：

[![image.png](http://daoluan.net/blog/wp-content/uploads/2012/06/image3.png)](http://daoluan.net/blog/wp-content/uploads/2012/06/image3.png)

所以π*(8)={0,2,4,6}。对于其他的 π*(q)值也是这样计算。**这里的涉及了很多的定义，务必看懂，下面的三个结论才看得下去。如果太急，直接忽视这里，看上面的“有趣的字符串匹配”。**

假设已经得到了关于P的辅助表，

    
    kmp()
        m = strlen(P)
        n = strlen(T)
        π[m]
        kmptab(π)    //预处理辅助表
        q = -1
        for i=[0,n)
            while q>0 && P[q+1]!=T[i]
                q = π[q]
            if P[q+1]==T[i]
                q = q+1
            if q = m
                //    找到啦
            q = π[q]    //继续剩余T的寻找


其中π[m]为辅助表。如果P[q+1]==T[i]能连续成立m次，那么可以找到T中的P。所以如果有辅助表的存在，匹配过程还是很容易理解的。

KMP 有三个结论，他们主要是用来计算辅助表的：

- π*(q)={k|(k)P是(q)P的后缀且k<q}。明显.

- 如果π(q)>0，那么π(q)-1∈π*(q-1)。

∵π(q)=t，那么t<q，所以π(q)-1=t-1<q-1；

∵π(q)=t，∴(t)P是(q)P的后缀，（去掉(t)P和(q)P的最后一个字符）那么(t-1)P同样也是(q-1)P的后缀；

根据结论一，得到 t-1∈π*(q-1)，π(q)-1∈π*(q-1)总能成立。

- 图示结论[![image.png](http://daoluan.net/blog/wp-content/uploads/2012/06/image5.png)](http://daoluan.net/blog/wp-content/uploads/2012/06/image5.png)

上面的图中，如果匹配不成功, π 值会越来越小, 直到为0, 此时就需要重新从第一个字符开始匹配了.

上面的基础就是为计算辅助表的。有了上面的结论：

    
    kmptab(π)
        m = strlen(P)
        q = 0
        π[0] = 0
        for i=[1,m)
            while q>0 && P[q]!=P[i] // 与当前字符不匹配的时候, 才需要缩小 π
                q = π[q]    //    
    
            if P[q]=P[i]
                q = q + 1    //    与上图中的做法一致
            π[i] = q


实在是太短了。


# KMP的复杂度


KMP的复杂度一时我也说不清楚，借助了算法导论和Matrix67的手笔才略有领悟。KMP用到了平摊分析。就上面的kmptab(π)函数，从q的值来说，q = π[q]操作只会使的q越来越小，但总能q>0，因为q = π[q]是根据辅助表来得到的，而辅助表中最小为0。P[q]=P[i]条件成立，能使得q+1，也就是说q只有在这里才增加。最坏的情况，q被增加m-1次。所以while循环内的操作最多被执行m-1次的。平摊一下就是O(1)了。所以加上for循环，kmptab的复杂度为O(m)。

kmp主程序也是用这种平摊分析方法。

补充：KMP匹配过程中利用辅助表跳过了无效的检查，直接将检查过程跳转到将来可能成功匹配的字符上。

本文完 2012-06-14

捣乱小子 [www.daoluan.net/blog](http://www.daoluan.net/blog)
