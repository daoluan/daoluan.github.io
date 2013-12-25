---
author: daoluan
comments: true
date: 2012-09-05 04:43:26+00:00
layout: post
slug: gtd-project-developers-record
title: GTD项目开发实录
wordpress_id: 975
categories:
- 学习总结
- 随笔
tags:
- GTD项目实录
---

## 文章目录





	
  * 暑假说起GTD的事情

	
  * 第一次uGeeeeek团伙会议

	
  * UIButton 简易UI

	
  * 漫谈界面和数据

	
  * MySQL入门教程

	
  * 初探libevent网络库

	
  * c++ __FILE__，__LINE__和__FUNCTION__的使用方法




<!-- more -->





## 初探c++ __FILE__，__LINE__和__FUNCTION__的使用方法


[c++ __FILE__，__LINE__和__FUNCTION__的使用方法](http://daoluan.net/blog/archives/1095) 在stackoverflow上一个有趣不错的帖子。曾经也在一年前某公司的面试题目遇到这些字眼，可见它可以是c++程序猿基本的素质。__FILE__，__LINE__，__FUNCTION__ 这三个c++内置扩展宏对程序调试非常有好处。日后会尝试着写一个比较通用的c++程序测试工具。

2012-09-27




## 初探libevent网络库


[初探libevent网络库](http://daoluan.net/blog/archives/1089) libevent是个不错的网络库，后期想按着文章中的思路去开发一个多线程版本。借助libevent，当下的系统已经完成登录模块，万变不离其宗，更新和同步模块随着数据库模型的确定也该尘埃落定。

2012-09-27




## MySQL入门教程


[MySQL入门教程](http://daoluan.net/blog/?p=1063) 第三篇报告。前台后台设计如期而至，现正紧张后台数据库测试，兵马未动，粮草先行！

2012-09-25




## 漫谈界面和数据


[漫谈界面和数据](http://daoluan.net/blog/archives/1029) 第二篇报告。

![](http://daoluan.net/blog/wp-content/uploads/2012/09/UI_data_combine.png)

PC前端开发当中对数据的掌控变得不那么得心了。之前就有听说过MFC很难做到界面元素和业务逻辑的分离，可是纵观下来，觉得这个项目还有令人满意的地方：


> 因为GTD做到 了：

首先一块界面/界面数据区，界面/数据捆绑器，数据区。

> 
> 
	
>   1. 界面/界面数据区负责UI设计和界面数据的显示。
> 
	
>   2. 界面/数据捆绑器负责维护界面和业务逻辑之间的同步等等。
> 
	
>   3. 数据区则负责纯数据的管理。
> 






[![](http://daoluan.net/blog/wp-content/uploads/2012/09/UI_data_detach.png)](http://daoluan.net/blog/archives/975/ui_data_detach)




2012-09-14




## UIButton 简易的UI


[UIButton 简易UI](http://daoluan.net/blog/archives/1006) 第一篇项目报告中的内容抽象绘图按钮，抽象出来过后发现，使用更加灵活。效果图如下：

[![](http://daoluan.net/blog/wp-content/uploads/2012/09/UIButtonApp.jpg)](http://daoluan.net/blog/archives/1006/uibuttonapp)

项目前端已经完成60%（不含优化部分），等待其他代码的同时，接下来主要是服务器和数据库部分。下面是前端部署（乱画的）：

[![](http://daoluan.net/blog/wp-content/uploads/2012/09/gtd_client.png)](http://daoluan.net/blog/archives/975/gtd_client)

2012-09-10







## 第一次uGeeeek团伙会议


昨晚我们团伙进行了自成立以来第一次的会议。我们团伙有一个不错的名字uGeek，我经常故意拉长它的读音uGeeeeek，原因是团伙有5个成员，三男两女。会议的内容很充实，涉及到项目研发的很多方面，这归功于我们的项目组长。说到统领，这也是我自己所欠缺的，要设法强化统领团伙的技能。欠缺统领技能，技术再牛也不牛，只有给别人打工的份。


[![](http://daoluan.net/blog/wp-content/uploads/2012/09/leader.jpg)](http://daoluan.net/blog/archives/975/leader)


后来提及了在项目中兴趣问题，深处团伙当中，必须为自己的方向做一个定义，这对项目和个人来说利益是双收的。而兴趣是优先考虑的。或许我的这些话说的有点亡羊补牢，往前一点说，项目伊始，头目就要有选择的组织团伙，这不仅仅在意识达成一致，在技术或者说兴趣上也要互补，而这一点很难做到。而我们往往不能兼顾后者，不免有投机取巧之嫌。

项目当中，首先着手开干的是PC客户端应用，在这一方面我比较熟悉，所以主要负责PC客户端，其他队员则主要负责安卓移动和web端。而我对自己的定位便是PC和web服务端。

队员的任务必须精心部署，按个人的能力来划分。任务的划分不应加入太多的项目相关性，而是更多的一编程般性，因为更多的项目相关性会束缚coder的编程思路，以至于代码偏刻板。我做的有点疏忽，缺乏专业的眼光，所以研发的过程中好多次的修正。

客户端前端开发过程中，我简化directUI的思维，在UI，业务逻辑上和数据层的耦合，做到了一定程度上的松绑。会出现在后续的开发记录当中。:)

2012-09-07



## 暑假说起GTD的事情





暑假的文字。跟以前的同学说起我们项目的事情，我按我理解向他大概软件的开发流程，需求分析，架构，编码，测试，美化完善，正式上线。 同学说：这跟建房子一个道理。同时他也指出一个问题：你们既是建筑总工程师，还是水泥师傅，还是装修师傅。。。


[![](http://daoluan.net/blog/wp-content/uploads/2012/09/birds-nest-.jpg)](http://daoluan.net/blog/archives/975/birds-nest)







何尝不是？！学校里组队进行项目开发往往面临很多问题，前面提到的算一个。



	
  * 分工不明确

	
  * 有组织无纪律

	
  * 团队意识模糊


所以在学校里想真正完成一个项目，面临着严重的挑战，这不仅仅是技术问题。团队成员即使人数再多，不懂团队不懂纪律，跟一般散沙有什么区别，而靠一个人是做不到的。强化**团队气势**，提高**团队品质**，加强**团队合作**。所以意识到这一点，如果成员之间不懂纪律，毫无章法，还是及早退出吧。

2012-08


