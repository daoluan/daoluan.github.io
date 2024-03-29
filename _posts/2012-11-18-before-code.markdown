---
title: 写代码之前要做什么？
date: 2012-11-18 02:38:29 Z
categories:
- 随笔
tags:
- 随笔
author: daoluan
comments: true
layout: post
wordpress_id: 1473
---

在想到这个问题的时候，很多童鞋都会笃定回答：我会先构思程序大体的框架，接着就开始写代码。

A：难道你就不将你的构思巨细文档下？

B：一般的编程任务不会太难的话，我觉得YY也很可靠，可能更高效。

A：为什么这么急的写代码？

B：手痒~~

<!-- more -->

先小说下YY。YY即意淫，这里意即写代码时，不草稿不文档，脑瓜里天马行空，心猿意马。

我不确定是不是大多数的Coder都这么做？！但我周遭的许多同学确实是这么说的做的。首先，很可能是程序猿对自己的YY思维太过自信，再者就是急功近利——想要一睹自己在写完代码后『F7』+『Ctrl+F5』（注：VS2008 C++的生成解决方案和运行的快捷键，笔者经常在写完代码后，习惯这样快速运行）的运行结果和预期的一样。基于这种心态，我们越想去劈劈拍拍敲代码。

在这学期，我们课程安排里有软件工程这一门，说的就是软件从无到有的一个过程，其间包括提出问题，需求分析，详细设计，软甲架构，编码测试，接着可能就是RTM。但是，笔者似乎对软件工程这门课程很有偏见，以为跟我的感觉，它太过教条化，与自己先前写代码的方式违背。先说说教材，我们学校选的是《软件工程导论》XXX版，随口问了身旁的一位小哥，对这本书什么评价，答曰：“不好！”问为什么还拿来当教材？答曰：“上面印着XXXX精品教材。”笔者想不明白，为什么一本在自由书市无人问津的书籍，还会出**第N版**（读重音），还在各高校这么有市场。存在即合理~~呵呵。。。

在前几天，开始看[《代码大全了》](http://book.douban.com/subject/1477390/)，含金量对得起它的厚度。而它的讲解真教人拍手称快。这样的书才能被奉为“机经”，被程序猿收藏于案头架上。当然，代码大全并不是完整的讲述软件工程，毕竟它只在软件架构部分“事无巨细”。而想要完整讲述软件工程这一学科，它的每一个阶段都可以是一本或几本书。

扯的有点远了。任务越是庞杂的时候，零零碎碎的问题就越来越多，而且缺乏『高层设计』和『底层设计』的迭代设计过程，这些问题会越来越凸显，而且一盘散沙，眼花缭乱，于是很可能前功尽弃，重头再来一遍，又或者破罐子破摔。思维空间似一张草稿，范围有限，不容的我们天马行空，欲在狭小的范围描述一个庞杂的系统，显得有些吃力，这时候文档就越发重要了。如果不以为然，要么恭喜你，你是天才架构师；要么XX你，项目经验太少。当有项目经验过后，会发现『YY』显得苍白无力。

童鞋们可能牢骚：这些烂大街老掉牙的东西！是啊，明白这些的人太多了，笔者是其中之一，可忍耐非常脆弱，不费吹灰便可被『噼噼啪啪敲键盘』的欲望击垮。所以，如果读者这么不幸与读者有类似的经历的话，当下要做的就是**『禁欲』**。

不是每个人天生都是天才架构师，都能鸟瞰软件系统，一来就『噼噼啪啪』干起来。也许这一次的设计不是那么的完美，但如上所提到的，『高层设计』和『底层设计』的迭代设计的过程会让你不断的发现其中的瑕疵，完善整个系统。好吧，再退一步讲，即便经过设计的系统还是很不合理的系统，那你也能很快体验到设计后『奋笔疾书』敲代码的快感，关键是意识到这问题的时候，学习才能提高了。

一个设计合理与否的系统很快会自己给出答案。一个显而易见的方法是，当**需要更改**的时候，系统需要在多大的程度上被修改。这里提一个蹩脚的比喻：


<blockquote><p>程序猿==医生，</p>
<p>客户有问题需要解决，过来找你。你是医生，他是患者。</p>
<p>你要经过望闻问切，找到患者的病因（需求分析）</p>
<p>针对病因，找到适合的治疗方案（合适的技术）</p></blockquote>


而当医生宣布你已经无药可救的时候，很明显系统有问题。

学计算机的，对IT稍有些狂热的人，都会突发奇想做自己的应用，而且这种想法经常有，注重软件设计的机会，将大有裨益。阅读[《代码大全了》](http://book.douban.com/subject/1477390/)那会，一个很有趣的地方：说要把界面和数据逻辑分开，而『更换界面的需求（譬如将可视化变为较为容易测试的console）』能回答界面和数据逻辑分开与否。这一提示能够让我们日后在设计的时候时刻提高警惕——如果真的有需求要将可视化界面更换为console，数据层和业务逻辑层能否不动声色。

最后，『真的程序员，敢于直面惨淡的重构，敢于正视淋漓的需求。』，这句话某中意义上是YY高手不思进取，对现实世界的妥协。别急着『噼噼啪啪』，设计下，文档下，或许不至于惨淡。

笔者没有软件工程系统的学习经验，上述文字自己的所感所想，欢迎斧正。

本文完 2012-11-18

Dylan [http://daoluan.github.io/](http://daoluan.github.io/)
