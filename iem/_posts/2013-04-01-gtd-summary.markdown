---
author: daoluan
comments: true
date: 2013-04-01 11:10:42+00:00
layout: post
slug: gtd-summary
title: GTD时间管理作品总结
wordpress_id: 1633
categories:
- cplusplus
- linux
- 学习总结
- 网络编程
- 随笔
tags:
- GTD项目实录
---


<p>GTD时间管理项目接近尾声。</p>
<p><span style="color: #ff6600;"><strong>前端后台通用代码兼容</strong></span> GTD 时间管理项目的PC端开发其实是从寒假开始。随着底层数据库的粗略确定，后台服务器的通用功能 C 代码（譬如网络数据的打包和解压）在组员的帮助下完成了。对，是C代码，因为一开始是后台服务器决定使用纯C编写。现在想起来，那时太固执了，这就好像，别人扛枪拉炮攻占我们的地盘了，我们放着原子弹不用，还吵着要提着扁担锄头跟敌人死磕。最后改为了C/C++ ，编译器也相应改为 g++ 。</p>
<p>另外，那个时候，我还很自信，小看了未来将要遇到的问题。</p>
<p><span style="color: #ff6600;"><strong>数据库设计，本末倒置</strong></span> 粗略确定！不知道浪费了多少编译连接调试的时间。现在看来，在动手开始一个项目之前，底层数据模式是需要首要考虑和确定的，当初自己犯下的错误就是本末倒置，更多的去考虑界面，虽在界面折腾了一段时间，还是有些许的收获，但衡量一下，是点芝麻丢瓜的赔本买卖。我不是说其他的不重要，但代码就是跟着数据走的，数据是软件的灵魂。</p>
<p><span style="color: #ff6600;"><strong>linux网络编程</strong></span> 在后台服务器网络编程上我琢磨了好长的时间。首先想到的是手动自己写一个最简易的功能模块，对网络数据进行收发。自己也确实是实践了，但最后没有采用，因为潜在未知的问题一直在困扰我（微博上的讨论：<a href="http://weibo.com/2313159920/yC6O46ZyP?type=repost" onclick="javascript:_gaq.push(['_trackEvent','outbound-article','http://weibo.com']);">这里</a>）。首先，GTD 时间管理项目不属于大工程，完成一个网络库工作量大，能考虑的和可能要考虑的问题多，得不偿失；互联网上流传着很多成熟稳定适用于 C/S 开发的网络库，衣来伸手饭来张口<span style="line-height: 1.714285714; font-size: 1rem;">。</span></p>
<p><span style="font-size: 1rem;">进行简单的测试过后，</span><span style="font-size: 1rem; line-height: 1.714285714;">最终敲定使用 libevent 网络库：通过注册事件完成网络事务。</span></p>
<p><span style="color: #ff6600;"><strong>再来一次</strong></span> 发现数据库需要重新改写确定，于是和 @国东 再一次商讨了 GTD 时间管理项目后台数据库，确定下来之后，放心的在原有的基础上重新设计，重新做一遍。血淋淋的教训啊，重做的过程中，偶尔骂自己：「怎么会写出这么恶心的代码？」</p>
<p><span style="color: #ff6600;"><strong style="font-size: 1rem;">确定</strong><strong>DBMS和数据持久化</strong></span>&nbsp;在数据库管理系统上，后台选用的是 mysql ； PC 前端一开始选用简单文件读写，但一来它很容易被用户更改，这是潜在的问题；二来，不方便进行数据更新。所以，选用了轻量级的 SQLite。</p>
<p>因为要对数据库进行添加/修改/删除等等操作，势必需要有可执行的 SQL 语句。一开是方法是到处生成raw SQL语句，然后交由数据库操作接口执行，缺乏数据持久性。当对数据库表修改的时候，势必要对raw SQL生成器作大量的修改。于是便有了&nbsp;<a title="链向 【译】Simple MySQL ORM for C 的固定链接" href="http://daoluan.net/blog/simple-mysql-orm-for-c-translation/" rel="bookmark">【译】Simple MySQL ORM for C</a>。但这仍然有一个缺点，因为前端使用的是 SQLite ，Simple MySQL ORM for C 是为 MySQL 而生的，无法使用到前端中。最好是该用&nbsp;<a href="http://sourceforge.net/apps/trac/litesql/" onclick="javascript:_gaq.push(['_trackEvent','outbound-article','http://sourceforge.net']);">LiteSQL</a>&nbsp;，不然学习的成本很大。</p>
<p><span style="color: #ff6600;"><strong>数据同步策略</strong></span> 最后一个较为棘手的问题：同步问题。在 CSDN 上发起的讨论：<a href="http://bbs.csdn.net/topics/390389282" onclick="javascript:_gaq.push(['_trackEvent','outbound-article','http://bbs.csdn.net']);">讨论：印象笔记的同步策略是怎么样的？</a></p>
<p>需要考虑三个部分，分别是用户新增、修改和删除。</p>
<p>其中「修改」可以用时间戳的方法解决（没错，因为数据库表需要添加 timestamp &lt;时间戳&gt;字段，所以上面提到的「raw SQL」需要进行大量的修改）。新增和删除则可以通过记录用户的操作来实现，譬如：用户新添/删除一个数据，则记录他的操作：</p>
<p><strong>[user_id]:[data_item_id]:[datetime]:[operation]</strong></p>
<p>当前端提出同步请求的时候，则对此用户的<strong>操作集</strong>进行分析，即可得到用户新增/删除的数据项。</p>
<p><span style="color: #ff6600;"><strong>我们团队成果</strong></span> @卓升 负责移动安卓前端，已经做完而且上架：<a href="http://apk.hiapk.com/html/2012/11/966795.html?module=256&amp;info=ZwB0AGQA" onclick="javascript:_gaq.push(['_trackEvent','outbound-article','http://apk.hiapk.com']);">这里</a>；@国东 和 @曼云 、@华娜 合作完成 GTD 时间管理项目 web 端：<a href="http://ugeek.sinaapp.com/" onclick="javascript:_gaq.push(['_trackEvent','outbound-article','http://ugeek.sinaapp.com']);">这里</a>。</p>
<p><strong><span style="color: #ff6600;">最后</span>&nbsp;</strong>好记性不如烂笔头，鄙人需要写下在写程序过程中需要注意的问题，我甚至觉得这是程序员可以有的素养：</p>
<ul>
<li><span style="line-height: 1.714285714; font-size: 1rem;">交流。和同学网友社区提出自己的问题，给出自己的想法。</span></li>
<li><span style="line-height: 1.714285714; font-size: 1rem;">集中火力。遇到瓶颈，集中弹药火力攻坚。</span></li>
<li><span style="line-height: 1.714285714; font-size: 1rem;">结对编程。能大大提高编程效率，道不同不相为谋，最好与技术方向一致的伙伴结伴编程。</span></li>
<li><span style="line-height: 1.714285714; font-size: 1rem;">勿</span><span style="line-height: 1.714285714; font-size: 1rem;">重复发明轮子。很容易能再互联网上找到一些成熟的框架或者工具以及相关的文档，提取扼要部分，嵌入自己的作品当中。</span></li>
</ul>
<p><span style="color: #ff6600;"><strong>技术总结</strong></span> 如果觉得上面说的太务虚，那接下来是GTD时间管理项目PC前端和对应的后台服务器开发的技术总结。</p>
<p>MFC界面开发：</p>
<ul>
<li><span style="line-height: 14px;"><a href="http://daoluan.net/blog/gtd-project-developers-record/#3">UIButton 简易UI</a></span></li>
<li><a href="http://daoluan.net/blog/gtd-project-developers-record/#4">漫谈界面和数据</a></li>
</ul>
<p>linux网络编程：</p>
<ul>
<li><span style="line-height: 14px;"><a href="http://daoluan.net/blog/tcp%e5%8d%8f%e8%ae%ae-cs%e7%bd%91%e7%bb%9c%e7%bc%96%e7%a8%8b/" data-ke-src="http://daoluan.net/blog/tcp%e5%8d%8f%e8%ae%ae-cs%e7%bd%91%e7%bb%9c%e7%bc%96%e7%a8%8b/">基于TCP的C/S初级网络编程1</a><br>
</span></li>
<li><a href="http://daoluan.net/blog/%e5%9f%ba%e4%ba%8etcp%e7%9a%84cs%e5%88%9d%e7%ba%a7%e7%bd%91%e7%bb%9c%e7%bc%96%e7%a8%8b/" data-ke-src="http://daoluan.net/blog/%e5%9f%ba%e4%ba%8etcp%e7%9a%84cs%e5%88%9d%e7%ba%a7%e7%bd%91%e7%bb%9c%e7%bc%96%e7%a8%8b/">基于TCP的C/S初级网络编程2</a></li>
<li><a href="http://daoluan.net/blog/hava-a-look-at-libevent/" data-ke-src="http://daoluan.net/blog/libevent/">初探libevent网络库</a></li>
<li>&lt;微博小讨论&gt;<a href="http://weibo.com/2313159920/yC6O46ZyP?type=repost" onclick="javascript:_gaq.push(['_trackEvent','outbound-article','http://weibo.com']);">这里</a></li>
</ul>
<p>数据库实践：</p>
<ul>
<li><a style="line-height: 1.714285714; font-size: 1rem;" href="http://daoluan.net/blog/mysql-entry/" data-ke-src="http://daoluan.net/blog/mysql-entry/">MySQL入门教程</a></li>
<li><a href="http://daoluan.net/blog/linux-c-reuse-port/" data-ke-src="http://daoluan.net/blog/linux-c-reuse-port/">Linux c端口复用</a></li>
<li><a href="http://daoluan.net/blog/simple-mysql-orm-for-c-translation/" data-ke-src="http://daoluan.net/blog/simple-mysql-orm-for-c-translation/">【译】Simple MySQL ORM for C</a></li>
</ul>
<p>其他：</p>
<ul>
<li><a href="http://daoluan.net/blog/gtd-project-developers-record/" data-ke-src="http://daoluan.net/blog/gtd-project-developers-record/">GTD项目开发实录</a></li>
<li><a style="line-height: 1.714285714; font-size: 1rem;" href="http://bbs.csdn.net/topics/390389282" onclick="javascript:_gaq.push(['_trackEvent','outbound-article','http://bbs.csdn.net']);">讨论：印象笔记的同步策略是怎么样的？</a></li>
</ul>
<p><span style="font-size: 1rem;">是为 GTD 时间管理总结。</span></p>
<p><span style="font-size: 1rem;">捣乱&nbsp;</span><span style="font-size: 1rem; line-height: 1.714285714;">2013-4-1 </span></p>
<p><span style="font-size: 1rem; line-height: 1.714285714;"><a href="http://daoluan.net">daoluan.net</a></span></p>
