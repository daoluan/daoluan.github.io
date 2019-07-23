---
title: 'Django 源码小剖: Django 对象关系映射(ORM)文件组织结构'
date: 2013-10-12 01:08:18 Z
categories:
- 学习总结
tags:
- Django
- 源代码
author: daoluan
comments: true
layout: post
wordpress_id: 2028
---

### 引


从前面已经知道, 一个 request 的到来和一个对应 response 的返回的流程, 数据处理和数据库离不开. 我们也经常在 views.py 的函数定义中与数据库打交道.


### django ORM 源代码组织结构


对于数据库, django 有自己的一套 ORM(对象关系映射), 或许其他的框架可以随意更换 ORM, 但 django 不建议这么做. 因为 django 内置有很多的 model, 这些 model 无疑是用 django 内置 ORM 实现的, 如果更换后, 内置的 model 就无效了, 除非以下两个选择:



	
  1. 你已经吃透了 django 的 ORM, 定制自己的 ORM, 但必须用里面的规则, 比如类的属性名等等;

	
  2. 又或者更换自己的 ORM, 不使用 django 内置的 model.


**django 是一个大而全的框架, 但大而全却又增加了它本身的负担, 使其灵活性大大降低. 所以你看, 高内聚低耦合不容易做到.**


数据库本身的复杂的, 数据库操作涉及的选项有很多, 一个 ORM 也并不简单. django 数据库部分在 django.db 中实现, 在展开之前先介绍一下它的源代码文件组织:




    
    django.db
    ----backends 各种数据库后端实现
        ----dummy 哑后端, 什么都不做, 定义空方法
        ----mysql mysql 实现
        ----oracle oracle 实现
        ----.....
    ----models 重头戏, backends 中各种数据库都是基于此实现的
        ----fields 数据库表字段实现
            ----.....
        ----sql 语句, 记录 sql 语句的各种选项, where 等, 最后生成 sql 语句; 连接数据库得到结果
            ----.....
        ----aggregates.py 聚合相关
        ----base.py 定义 Model 类
        ----constants.py 一些常量
        ----deletion.py 数据库表项的删除实现
        ----expressions.py 表达式类, where 会出现表达式
        ----loading.py
        ----manager.py ORM 的管理器
        ----options.py 数据库表选项, 譬如主键等
        ----query.py 数据库查询集类
        ----query_utils.py 小工具
        ----related.py 与`表关联`相关
        ----signals.py
        ----__init__.py


django ORM 底层的实现都在 django.db.models 中. 如你所知, 数据库操作的选项很多, 这里并不专注展开这些选项在 django ORM 中是如何实现的, 而**将展开的是 django ORM 的实现的框架**, 当用 django ORM 执行一个简单的查询操作时, 里面是如何工作的, 工具类之间是如何协调的. 了解这些, 使用 django ORM 会更游刃有余.

我已经在 github 备份了 Django 源码的注释: [Decode-Django](https://github.com/daoluan/Decode-Django), 有兴趣的童鞋 fork 吧.

捣乱 2013-9-22

[http://daoluan.net](http://daoluan.net/)
