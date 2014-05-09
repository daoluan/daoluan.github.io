---
author: daoluan
comments: true
date: 2012-05-06 10:27:00+00:00
layout: post
slug: knapsack-problems
title: 背包问题（01背包，完全背包，多重背包）
wordpress_id: 58
categories:
- 算法
tags:
- 01背包
- 多重背包
- 完全背包
- 背包问题
---

# 写在最前面的


近日为以下琐事烦身：

差不多要向学院提交项目申请了，本来是想做个多模式的IM系统的，可是跟往届通过审核的项目比起来，缺乏创新和研究价值，所以在文档上要多做手脚，花点心思。

<!-- more -->



	
  * 一大堆的作业，每每期中都是这样。

	
  * 一直想读的DirectUI开源代码一直没有进展下去。

	
  * 准备五月底的软件设计比赛。

	
  * 魔兽玩的好菜。

	
  * 空虚寂寞，想找个GF...


背包问题，经典有[背包九讲](http://www.google.com.hk/#hl=zh-CN&newwindow=1&safe=strict&site=&source=hp&q=%E8%83%8C%E5%8C%85%E4%B9%9D%E8%AE%B2&oq=%E8%83%8C%E5%8C%85%E4%B9%9D&aq=0&aqi=g2&aql=&gs_l=hp.3.0.0l2.167.13160.0.14083.46.32.14.0.0.4.277.3579.10j13j3.26.0...0.0.fdYcxJL8ndA&bav=on.2,or.r_gc.r_pw.,cf.osb&fp=5d6d0c415301648b&biw=1152&bih=628)。



# 01背包


[![魔兽插图](http://images.cnblogs.com/cnblogs_com/daoluanxiaozi/201205/201205061646439368.jpg)](http://images.cnblogs.com/cnblogs_com/daoluanxiaozi/201205/201205061646426826.jpg)


<blockquote>不死族的巫妖王发工资拉,死亡骑士拿到一张N元的钞票(记住,只有一张钞票),为了防止自己在战斗中频繁的死掉,他决定给自己买一些道具,于是他来到了地精商店前.

死亡骑士:"我要买道具!"

地精商人:"我们这里有三种道具,血瓶150块一个,魔法药200块一个,无敌药水350块一个."

死亡骑士:"好的,给我一个血瓶."

说完他掏出那张N元的大钞递给地精商人.

地精商人:"我忘了提醒你了,我们这里没有找客人钱的习惯的,多的钱我们都当小费收了的,嘿嘿."

死亡骑士:"......你妹"

死亡骑士想,与其把钱当小费送个他还不如自己多买一点道具,反正以后都要买的,早点买了放在家里也好,但是要尽量少让他赚小费.

现在死亡骑士希望你能帮他计算一下,最少他要给地精商人多少小费.</blockquote>


上面就是一个01背包问题。上面的问题可以描述为：


<blockquote>有n个物品，每个物品的重量为weight[i]，每个物品的价值为value[i]。现在有一个背包，它所能容纳的重量为total，问：当你面对这么多有价值的物品时，你的背包所能带走的最大价值是多少？</blockquote>


思路：每个物品无非是装入背包或者不装入背包，那么就一个一个物品陆续放入背包中。可以有


<blockquote>**tab[i][j] = max(tab[i-1][j-weight[i]]+value[i],tab[i-1][j]) (\{i,j|0<i<=n,0<=j<=total\}) **</blockquote>


其中i表示放第i个物品，j表示背包所容纳的重量，那么tab[i-1][j-weight[i]]+value[i]表示放入第i物品，刚开始接触会有疑问，tab[i-1][j-weight[i]]这个值，可以这样理解：tab[i-1][j]为装到上一个物品在背包j容量时的最佳值，那么如果我要在j容量的时候放入现在的i物品，那么是不是要j-weight[i]，所以tab[i-1][j-weight[i]]+value[i]为放入第i物品的价值；tab[i-1][j]就是不放入第i个物品。

动态规划的思维就在这里体现了，即tab[i-1][j]是tab[i][j]的最优解（我觉得上面的思路讲解较容易理解）。

例子：5个物品，（重量，价值）分别为：（5，12），（4，3），（7，10），（2，3），（6，6）。
<table cellpadding="0" cellspacing="0" border="1" >
<tbody >
<tr >
<td width="73" valign="top" >背包容量</td></tbody>
<td width="33" valign="top" >0</td></tbody>
<td width="33" valign="top" >1</td></tbody>
<td width="33" valign="top" >2</td></tbody>
<td width="33" valign="top" >3</td></tbody>
<td width="33" valign="top" >4</td></tbody>
<td width="33" valign="top" >5</td></tbody>
<td width="33" valign="top" >6</td></tbody>
<td width="33" valign="top" >7</td></tbody>
<td width="33" valign="top" >8</td></tbody>
<td width="33" valign="top" >9</td></tbody>
<td width="33" valign="top" >10</td></tbody>
<td width="33" valign="top" >11</td></tbody>
<td width="33" valign="top" >12</td></tbody>
<td width="33" valign="top" >13</td></tbody>
<td width="33" valign="top" >14</td></tbody>
<td width="33" valign="top" >15</td></tbody>
</tr></tbody>
<tr >
<td width="73" valign="top" >5物品</td></tbody>
<td width="33" valign="top" >0</td></tbody>
<td width="33" valign="top" >0</td></tbody>
<td width="33" valign="top" >0</td></tbody>
<td width="33" valign="top" >0</td></tbody>
<td width="33" valign="top" >0</td></tbody>
<td width="33" valign="top" >0</td></tbody>
<td width="33" valign="top" >6</td></tbody>
<td width="33" valign="top" >12</td></tbody>
<td width="33" valign="top" >12</td></tbody>
<td width="33" valign="top" >15</td></tbody>
<td width="33" valign="top" >15</td></tbody>
<td width="33" valign="top" >18</td></tbody>
<td width="33" valign="top" >22</td></tbody>
<td width="33" valign="top" >22</td></tbody>
<td width="33" valign="top" >25</td></tbody>
<td width="33" valign="top" >25</td></tbody>
</tr></tbody>
<tr >
<td width="73" valign="top" >4物品</td></tbody>
<td width="33" valign="top" >0</td></tbody>
<td width="33" valign="top" >0</td></tbody>
<td width="33" valign="top" >3</td></tbody>
<td width="33" valign="top" >3</td></tbody>
<td width="33" valign="top" >3</td></tbody>
<td width="33" valign="top" >3</td></tbody>
<td width="33" valign="top" >3</td></tbody>
<td width="33" valign="top" >12</td></tbody>
<td width="33" valign="top" >12</td></tbody>
<td width="33" valign="top" >15</td></tbody>
<td width="33" valign="top" >15</td></tbody>
<td width="33" valign="top" >18</td></tbody>
<td width="33" valign="top" >22</td></tbody>
<td width="33" valign="top" >22</td></tbody>
<td width="33" valign="top" >25</td></tbody>
<td width="33" valign="top" >25</td></tbody>
</tr></tbody>
<tr >
<td width="73" valign="top" >3物品</td></tbody>
<td width="33" valign="top" >0</td></tbody>
<td width="33" valign="top" >0</td></tbody>
<td width="33" valign="top" >0</td></tbody>
<td width="33" valign="top" >0</td></tbody>
<td width="33" valign="top" >0</td></tbody>
<td width="33" valign="top" >0</td></tbody>
<td width="33" valign="top" >0</td></tbody>
<td width="33" valign="top" >12</td></tbody>
<td width="33" valign="top" >12</td></tbody>
<td width="33" valign="top" >15</td></tbody>
<td width="33" valign="top" >15</td></tbody>
<td width="33" valign="top" >15</td></tbody>
<td width="33" valign="top" >22</td></tbody>
<td width="33" valign="top" >22</td></tbody>
<td width="33" valign="top" >22</td></tbody>
<td width="33" valign="top" >22</td></tbody>
</tr></tbody>
<tr >
<td width="73" valign="top" >2物品</td></tbody>
<td width="33" valign="top" >0</td></tbody>
<td width="33" valign="top" >0</td></tbody>
<td width="33" valign="top" >0</td></tbody>
<td width="33" valign="top" >0</td></tbody>
<td width="33" valign="top" >3</td></tbody>
<td width="33" valign="top" >12</td></tbody>
<td width="33" valign="top" >12</td></tbody>
<td width="33" valign="top" >12</td></tbody>
<td width="33" valign="top" >12</td></tbody>
<td width="33" valign="top" >15</td></tbody>
<td width="33" valign="top" >15</td></tbody>
<td width="33" valign="top" >15</td></tbody>
<td width="33" valign="top" >15</td></tbody>
<td width="33" valign="top" >15</td></tbody>
<td width="33" valign="top" >15</td></tbody>
<td width="33" valign="top" >15</td></tbody>
</tr></tbody>
<tr >
<td width="73" valign="top" >1物品</td></tbody>
<td width="33" valign="top" >0</td></tbody>
<td width="33" valign="top" >0</td></tbody>
<td width="33" valign="top" >0</td></tbody>
<td width="33" valign="top" >0</td></tbody>
<td width="33" valign="top" >0</td></tbody>
<td width="33" valign="top" >12</td></tbody>
<td width="33" valign="top" >12</td></tbody>
<td width="33" valign="top" >12</td></tbody>
<td width="33" valign="top" >12</td></tbody>
<td width="33" valign="top" >12</td></tbody>
<td width="33" valign="top" >12</td></tbody>
<td width="33" valign="top" >12</td></tbody>
<td width="33" valign="top" >12</td></tbody>
<td width="33" valign="top" >12</td></tbody>
<td width="33" valign="top" >12</td></tbody>
<td width="33" valign="top" >12</td></tbody>
</tr></tbody>
</tbody></tbody>
</table></tbody>
故有：

    
    for i=[weight[0],total]
        tab[n-1][i] = weight[0];    //    n为物品数量
    for i=[1,n)
        for j=[weight[i],total]
            tab[n-i-1] = max(tab[n-i][j-weight[i]]+value[i],tab[n-i][j])
        /*    print tab[0][total]    */




# 完全背包




<blockquote>不死族的巫妖王发工资拉,死亡骑士拿到一张N元的钞票(记住,只有一张钞票),为了防止自己在战斗中频繁的死掉,他决定给自己买一些道具,于是他来到了地精商店前.

死亡骑士:"我要买道具!"

地精商人:"我们这里有三种道具,血瓶150块无限个,魔法药200块无限个,无敌药水350块无限个."

死亡骑士:"好的,给我一个血瓶."

说完他掏出那张N元的大钞递给地精商人.

地精商人:"我忘了提醒你了,我们这里没有找客人钱的习惯的,多的钱我们都当小费收了的,嘿嘿."

死亡骑士:"......你妹"

死亡骑士想,与其把钱当小费送个他还不如自己多买一点道具,反正以后都要买的,早点买了放在家里也好,但是要尽量少让他赚小费.

现在死亡骑士希望你能帮他计算一下,最少他要给地精商人多少小费.</blockquote>


上面的魔兽场景描述跟上面的只有小小的差异，就是物品有一个变为了无限个，这就是完全背包问题。完全背包问题可以描述为：


<blockquote>有n种物品，每种物品有无限个，每个物品的重量为weight[i]，每个物品的价值为value[i]。现在有一个背包，它所能容纳的重量为total，问：当你面对这么多有价值的物品时，你的背包所能带走的最大价值是多少？</blockquote>


有了上面01背包的式子，这题会变的容易理解很多，只是这个式子要有小小的改动。01背包在二维数组上操作，就是为了防止一个物品被放入多次的情况。因此一维数组可以满足完全背包的问题。如下：


<blockquote>**tab[j] = max(tab[j-weight[i]]+value[i],tab[j]);(\{i,j|0<i<=n,0<=j<=total\})**</blockquote>


根本就是一样的，只不过物品可以被放多次。
<table cellpadding="0" cellspacing="0" border="1" >
<tbody >
<tr >
<td width="73" valign="top" >背包容量</td></tbody>
<td width="33" valign="top" >0</td></tbody>
<td width="33" valign="top" >1</td></tbody>
<td width="33" valign="top" >2</td></tbody>
<td width="33" valign="top" >3</td></tbody>
<td width="33" valign="top" >4</td></tbody>
<td width="33" valign="top" >5</td></tbody>
<td width="33" valign="top" >6</td></tbody>
<td width="33" valign="top" >7</td></tbody>
<td width="33" valign="top" >8</td></tbody>
<td width="33" valign="top" >9</td></tbody>
<td width="33" valign="top" >10</td></tbody>
<td width="33" valign="top" >11</td></tbody>
<td width="33" valign="top" >12</td></tbody>
<td width="33" valign="top" >13</td></tbody>
<td width="33" valign="top" >14</td></tbody>
<td width="33" valign="top" >15</td></tbody>
</tr></tbody>
<tr >
<td width="73" valign="top" >i物品</td></tbody>
<td width="33" valign="top" >X</td></tbody>
<td width="33" valign="top" >X</td></tbody>
<td width="33" valign="top" >X</td></tbody>
<td width="33" valign="top" >X</td></tbody>
<td width="33" valign="top" >X</td></tbody>
<td width="33" valign="top" >X</td></tbody>
<td width="33" valign="top" >X</td></tbody>
<td width="33" valign="top" >X</td></tbody>
<td width="33" valign="top" >X</td></tbody>
<td width="33" valign="top" >X</td></tbody>
<td width="33" valign="top" >X</td></tbody>
<td width="33" valign="top" >X</td></tbody>
<td width="33" valign="top" >X</td></tbody>
<td width="33" valign="top" >X</td></tbody>
<td width="33" valign="top" >X</td></tbody>
<td width="33" valign="top" >X</td></tbody>
</tr></tbody>
</tbody></tbody>
</table></tbody>
故有：

    
    for i=[0,n)
        for(j=weight[i]; j<=total; j++)
            tab[j] = max(tab[j-weight[i]]+value[i],tab[j])
    /*    print tab[0][total]    */




# 多重背包




<blockquote>不死族的巫妖王发工资拉,死亡骑士拿到一张N元的钞票(记住,只有一张钞票),为了防止自己在战斗中频繁的死掉,他决定给自己买一些道具,于是他来到了地精商店前.

死亡骑士:"我要买道具!"

地精商人:"我们这里有三种道具,血瓶150块a个,魔法药200块b个,无敌药水350块c个."

死亡骑士:"好的,给我一个血瓶."

说完他掏出那张N元的大钞递给地精商人.

地精商人:"我忘了提醒你了,我们这里没有找客人钱的习惯的,多的钱我们都当小费收了的,嘿嘿."

死亡骑士:"......你妹"

死亡骑士想,与其把钱当小费送个他还不如自己多买一点道具,反正以后都要买的,早点买了放在家里也好,但是要尽量少让他赚小费.

现在死亡骑士希望你能帮他计算一下,最少他要给地精商人多少小费.</blockquote>


上面的魔兽场景描述跟上面的又有了小小的差异，就是物品有一个变为了有限个，问题也就变成了多重背包问题。


<blockquote>有n种物品，每种物品有amount[i]个，每个物品的重量为weight[i]，每个物品的价值为value[i]。现在有一个背包，它所能容纳的重量为total，问：当你面对这么多有价值的物品时，你的背包所能带走的最大价值是多少？</blockquote>


多重和完全更接近，多了数量的限制，用一个count[n]计数数组来限制物品i的数量。当放入第i个物品是较优值的时候，count[i]=count[i-weight[i]]+1;这样做是因为，放入第i个物品的操作是基于count[i-weight[i]]放入的，所以当count[i-weight[i]]>=amount[i]时，就要阻止放入即便放入第i个物品是较优值。 故有：

    
    for i=[0,n)
        /*    将count数组清零        */
        for(j=weight[i]; j<=total; j++)
            if    count[i-weight[i]]<amout[i]
                tab[j] = max(tab[j-weight[i]]+value[i],tab[j]);
                if    tab[j]=tab[j-weight[i]]+value[i]    //    决定放入i是较优解
                    count[i] = count[i-weight[i]] + 1
            else    if    tab[j]=0        //    防止装第1个物品和装其他物品的情况
                tab[j] = tab[j-1],count[j] = count[j-1]
            else    count[j] = count[j-1]
    /*    print tab[0][total]    */




# 总结


总结都在上面了。

附件：[背包问题--01背包-完全背包-多重背包.rar](http://files.cnblogs.com/daoluanxiaozi/%E8%83%8C%E5%8C%85%E9%97%AE%E9%A2%98--01%E8%83%8C%E5%8C%85-%E5%AE%8C%E5%85%A8%E8%83%8C%E5%8C%85-%E5%A4%9A%E9%87%8D%E8%83%8C%E5%8C%85.rar)



本文完 Sunday, May 06, 2012

捣乱小子 [http://daoluanxiaozi.cnblogs.com/](http://daoluanxiaozi.cnblogs.com/)
