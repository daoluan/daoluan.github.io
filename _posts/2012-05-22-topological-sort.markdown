---
title: "【图论】拓扑排序应用"
date: 2012-05-22 15:18:47 Z
categories:
- 算法
tags:
- "《算法导轮》学习总结"
author: daoluan
comments: true
layout: post
wordpress_id: 425
---

拓扑排序虽是一种排序，但是它跟平时所接触的sort或者qsort不同，排序的意义不同。拓扑排序针对有向无回路图（DAG）而言的，不应用与存在回路的有向图。

[【图论】广度优先搜索和深度优先搜索](http://daoluan.github.io/blog/?p=295) 有说到了BFS和DFS，拓扑排序是DFS的一个应用。

<!-- more -->

有向无回路图能说明事件的发生的先后的顺序。比如穿衣服，士兵排队等。一个具体的例子，有N个物体，下面给出物体的重量比较，比如(a,b)表示a比b重等等，问已给出的条件是否会矛盾？其实就是判断用所给条件所组织的一个图中是否会存在环？

在DFS中加入时间戳，完成DFS后让节点按第二时间戳排序，就得到了DAG的拓扑排序结果。[【图论】有向图是否存在环](http://daoluan.github.io/blog/?p=410) 拓扑排序还可以解决这个问题。

下面是士兵排队，边(u,v)表示士兵u必须排在士兵v的前面。

[![image.png](http://daoluan.github.io/images/blog/2012/05/image7.png)](http://daoluan.github.io/images/blog/2012/05/image7.png)

DFS过程增加时间戳，然后按照时间戳来排列顶点就可以得到士兵的排列，就可以得到：

[![image.png](http://daoluan.github.io/images/blog/2012/05/image8.png)](http://daoluan.github.io/images/blog/2012/05/image8.png)

所以g在f的前面，f在e的前面...


# 拓扑排序实现


得到伪代码：


    TOPLLOGICAL-SORT(G)
        DFS    /****带时间戳****/
        /****按第二时间戳排序****/




# 拓扑排序判断有无环


拓扑排序可以用于有向图环的判断。对于有向无回路图来说，进行拓扑排序之后（将上面第二个图，可以参考一下），对于(left,right)，left指起点在左，right指终点在右，都有第二时间戳(right)<第二时间戳(left)，也就是说如果违反这个结果，图中是比存在环的。看看：

[![image.png](http://daoluan.github.io/images/blog/2012/05/image10.png)](http://daoluan.github.io/images/blog/2012/05/image10.png)

对于边(d,a)第二时间戳(a)>第二时间戳(d)，此图存在环。利用拓扑排序还可以实现单源最短路径算法。


<blockquote><p>题外话：</p>
<p>我的算法还是比较水，硬着头皮去参加蓝桥杯的决赛，尽力啦！尽量不要让结果是打酱油的。蓝桥杯的比赛跟ACM/ICPC都很难，但是业内应该是ACM/ICPC更有威望的。也罢，去看看北京也好。</p>
<p>我们班就W和Z再加上我三个人，W很牛掰，较量起来根本不是对手，以后要好好向他学习！</p>
<p>真正让我学习算法的时间比较晚，因为一开始对其他的技术比较兴趣，也算是亡羊补牢，希望能有所收获吧。</p></blockquote>


本文完 2012-05-22

Dylan [http://daoluan.github.io/blog](http://daoluan.github.io/blog/)
