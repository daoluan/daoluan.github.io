---
author: daoluan
comments: true
date: 2012-05-30 09:00:00+00:00
layout: post
slug: prim-kruskal-dijkstra
title: 【图论】信手拈来的Prim，Kruskal和Dijkstra
wordpress_id: 437
categories:
- 算法
---

# 关于三个简单的图论算法


prim，dijkstra和kruskal三个图论的算法，初学者容易将他们搞混，所以放在一起了。

prim和kruskal是最小生成树（MST）的算法，dijkstra是单源最短路径的算法。

<!-- more -->


# prim


最小生成树prim算法采用了**贪心策略**：把点分成两个集合，A为已被处理（已经在最小生成树中）的顶点，B为待处理的顶点，(A,B)也就是一个割。若边(u,v)满足u∈A，v∈B，那么(u,v)就是通过割(A,B)的一条边。

很自然的，会有一定数量的边会通过该割，其中权重最小的边就是**轻边**。


> 什么是轻边？
> 
> [![image.png](http://daoluan.net/blog/wp-content/uploads/2012/05/image9.png)](http://daoluan.net/blog/wp-content/uploads/2012/05/image9.png)
> 
> 左边集合和右边集合就组成一个割，其中**边(a,b)是跨越两个集合最小的边**（途中标记为红色），它就是要找的轻边。

每次操作都是选择min{w(u,v)|u∈A,v∈B}，从而将v加入到A中，即将v标记为已处理顶点，直到将所有点都处理完为止。

上述过程可以产生最小生成树，即证明：A，B通过轻边（权重最小的边）(u,v)连接，现假设不选择(u,v)，而选择(u’,v’)得到了**更优**的最小生成树，注意w(u,v)<w(u’,v’)。证明推翻这个假设即可。

把(u’,v’)去掉，补上(u,v)，这不影响A，B的连通，这样就得到了比上述假设更优的最小生成树，从而推翻假设，同时也证明了这个算法具有最优子结构。

prim的伪代码：

    
    for i=[0,n)
    	dist[i] = tab[0][i]
    visit[0] = true
    for i=[1,n)
    	min = MAX_VALUE
    	for j=[0,n)
    		if !visit[j] && min>dist[j]
    			min = dist[j]
    	for k=[0,n)
    		if !visit[k] && dist[j]>tab[i][j]
    			dist[j] = tab[i][j]




# kruskal


最小生成树kruskal算法也具有**贪心策略**：将所有点边按权值大小从小到大排列，每次都从中选取最小权值的边(u,v)，并把它添加到正在生长的森林中。所以开始的时候图中n个顶点构成森林中的n棵树（通俗的讲就是n个集合），而且这些树（集合）只有一个顶点。

重复上述过程，就可以将森林中的树不断的合并（通俗的讲就是合并两个不相交集合），直到将所有点同属于一棵树为止（通俗的讲就是只剩下一个集合）。

[![image.png](http://daoluan.net/blog/wp-content/uploads/2012/05/image11.png)](http://daoluan.net/blog/wp-content/uploads/2012/05/image11.png)

如上图，有了四个独立的集合，先不管上面的边上从这个集合中哪个点连到那个集合的哪个点，我们只要找到最小权值的边（对于上面的图中是11），合并集合即可。因此上面的例子进行合并后：

[![image.png](http://daoluan.net/blog/wp-content/uploads/2012/05/image12.png)](http://daoluan.net/blog/wp-content/uploads/2012/05/image12.png)

kruskal证明过程可以参照prim算法的证明过程。

kruskal实现过程涉及了不相交子集的合并，可以开辟一个简单的数组，然后通过标记每个点的父节点来简化合并过程。举例：图中有10个顶点

一开始：

<table width="402" border="0" cellspacing="0" cellpadding="2">
<tbody>
<tr>
<td valign="top" width="35">i</td>
<td valign="top" width="38">0</td>
<td valign="top" width="38">1</td>
<td valign="top" width="38">2</td>
<td valign="top" width="36">3</td>
<td valign="top" width="36">4</td>
<td valign="top" width="36">5</td>
<td valign="top" width="36">6</td>
<td valign="top" width="36">7</td>
<td valign="top" width="36">8</td>
<td valign="top" width="35">9</td>
</tr>
<tr>
<td valign="top" width="35">parent</td>
<td valign="top" width="38">0</td>
<td valign="top" width="38">1</td>
<td valign="top" width="38">2</td>
<td valign="top" width="37">3</td>
<td valign="top" width="37">4</td>
<td valign="top" width="37">5</td>
<td valign="top" width="37">6</td>
<td valign="top" width="37">7</td>
<td valign="top" width="38">8</td>
<td valign="top" width="38">9</td>
</tr>
</tbody>
</table>

假设一段时间后：0 1 2 0 0 0 6 7 1 1

<table width="402" border="0" cellspacing="0" cellpadding="2">
<tbody>
<tr>
<td valign="top" width="35">i</td>
<td valign="top" width="38">0</td>
<td valign="top" width="38">1</td>
<td valign="top" width="38">2</td>
<td valign="top" width="36">3</td>
<td valign="top" width="36">4</td>
<td valign="top" width="36">5</td>
<td valign="top" width="36">6</td>
<td valign="top" width="36">7</td>
<td valign="top" width="36">8</td>
<td valign="top" width="35">9</td>
</tr>
<tr>
<td valign="top" width="35">parent</td>
<td valign="top" width="38">0</td>
<td valign="top" width="38">1</td>
<td valign="top" width="38">2</td>
<td valign="top" width="37">0</td>
<td valign="top" width="37">0</td>
<td valign="top" width="37">0</td>
<td valign="top" width="37">6</td>
<td valign="top" width="37">7</td>
<td valign="top" width="38">1</td>
<td valign="top" width="38">1</td>
</tr>
</tbody>
</table>


从上面的表可以判断顶点1，顶点8和顶点9同属于同一个集合；顶点0，顶点3，顶点4和顶点5同属于一个集合；凡是parent[i]=i都是单个点的集合，比如顶点2等。

所以程序中设计了两个函数，find和makeset，find用于找到一个集合的root，比如find(9)=1，find(5)=0；而makeset用于合并两个不相交的子集，它的作用就是修改其中一个集合的root就可以了。需要注意的是，kruskal算法要防止出现环，所以，当发现最小的边(u,v)同属于一棵树的时候，不能将其makeset。

kruskal的伪代码：

    
    for i=[0,n)
    	parent[i] = i
    //	根据权值升序排序
    sort
    while set_count>1
    	if find(u)!=find(v)
    		minprice+=w(u,v)
    		makeset(u,v)
    	//	update u and v;




# prim和kruskal的实现区别


一个非常明显的区别就是prim在任何时刻都只有两个集合，一个是已处理顶点集合，一个是待处理集合；而kruskal则有多个集合，所以kruskal涉及不相交子集合并的比较复杂的操作问题。


> 简单的MST应用：
> 
> 某省调查乡村交通状况，得到的统计表中列出了任意两村庄间的距离。省政府“畅通工程”的目标是使全省任何两个村庄间都可以实现公路交通（但不一定有直接的公路相连，只要能间接通过公路可达即可），并要求铺设的公路总长度为最小。请计算最小的公路总长度。
> 
> 或者
> 
> 省政府“畅通工程”的目标是使全省任何两个村庄间都可以实现公路交通（但不一定有直接的公路相连，只要能间接通过公路可达即可）。经过调查评估，得到的统计表中列出了有可能建设公路的若干条道路的成本。现请你编写程序，计算出全省畅通需要的最低成本。




# dijkstra


dijkstra要求所有点边的权值都是非负的，主要是如果出现负权边，可能会出现负权环，dijkstra就无法应付了。


> 关于dijkstra的小故事
> 
> 这个人名真不好记，所以我一直把它读作disco，对不住迪科斯彻爹爹。


dijkstra算法中设置了一个顶点集合S，从源点到集合中的顶点的最终最短路径的权值均已经确定。dijkstra过程反复从V-S（V即图的顶点集）中选择一个顶点v，使得d(s,v)为最短，并将v加入到集合S中，接着对v的所有边进行松弛。


> 什么是松弛？
> 
> 就是可能会出现这样的情况，假设源点为s，tab(u,v)为顶点u到顶点v的权值，dist(u)为迄今为止找到的s到u最短路径。在松弛(u,v)的过程中，要测试**是否可以通过u，对迄今为止找到的v的最短路径进行改进。**也就是可能会出现dist(v)>dist(u)+tab(u,v)的情况。
> 
> [![image.png](http://daoluan.net/blog/wp-content/uploads/2012/05/image13.png)](http://daoluan.net/blog/wp-content/uploads/2012/05/image13.png)
> 
> 上面的图因为dist(v)>dist(u)+tab(u,v)即6>2+3，故要对边(u,v)进行松弛的时候会将dist(v)从6更正为5。但对于下面的情况，在松弛过后，dist(v)没有改变因为dist(v)<=dist(u)+tab(u,v)即4<=2+3。
> 
> [![image.png](http://daoluan.net/blog/wp-content/uploads/2012/05/image14.png)](http://daoluan.net/blog/wp-content/uploads/2012/05/image14.png)
> 
> 松弛技术在Bellman-Ford负权回路探测算法中也有应用。不禁想起还小的一个作为题：两点之间曲线更短...


**dijkstra的过程**

初始将顶点s加入到S中，并更新s到其他顶点的路径权值。

  * 选择最短路径dist(s,t)，并将t加入到S中。

	
  * 在第一步中得到t，对于u∈V-S，松弛边(t,v)。


重复上述过程，直到所有的顶点都被加入到集合S中为止。

可以给出伪代码：

    
    //	初始化
    for i=[0,n)
    	dist[i] = tab[0][i]
    visit[0] = true;
    
    for i=[1,n)
    	//	寻找最短路径(s,t)，同时把t加入S集合
    	min = MAX_VALUE
    	for j=[0,n)
    		if !visit[j] && dist[j]<min
    			min = dist[j]
    
    	visit[j] = true
    
    	//	松弛边(t,v)，其中v为顶点
    	for k=[0,n)
    		if !visit[k] && dist[k]>dist[j]+tab[j][k]
    			dist[k] = dist[j]+tab[j][k]




> 简单的dijkstra应用：
> 
> 某省自从实行了很多年的畅通工程计划后，终于修建了很多路。不过路多了也不好，每次要从一个城镇到另一个城镇时，都有许多种道路方案可以选择，而某些方案要比另一些方案行走的距离要短很多。这让行人很困扰。
> 现在，已知起点和终点，请你计算出要从起点到终点，最短需要行走多少距离。




# 总结


prim，kruskal和dijkstra算法有贪心策略，他们贪在哪啊？



	
  1. prim：每次执行都选择轻边

	
  2. kruskal：每次执行都选择权值最小的边，同时合并两个不相交的子集

	
  3. dijkstra：每次执行都选择路径最短d(s,t)，并将顶点t加入到集合S中，同时对边进行松弛




附Dijkstra和Prim算法的源代码，他们都的基于邻接矩阵的，注意不是基于邻接表的




[【图论】信手拈来的Prim，Kruskal和Dijkstra附件.rar](http://www.cnblogs.com/daoluanxiaozi/archive/2012/05/30/2527162.html)





本文完 2012-05-30

捣乱小子 [http://www.daoluan.net/blog/](http://www.daoluan.net/blog/)
