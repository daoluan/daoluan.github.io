---
title: redis 数据结构综述
date: 2014-06-09 13:59:22 Z
categories:
- linux
tags:
- redis
- 数据结构
- 源码剖析
author: daoluan
comments: true
layout: post
wordpress_id: 2361
---

这里所说的数据结构是针对 redis 内部存储 key-value 的，其他诸如 redis 配置相关的数据结构，不在此篇讨论范围。


### 一览 redis 数据结构


**dict**，哈希表，redis 所有的 key-value 都存储在里面。

    
    // 哈希表（字典）数据结构，redis 的所有键值对都会存储在这里。其中包含两个哈希表。
    typedef struct dict {
        // 哈希表的类型，包括哈希函数，比较函数，键值的内存释放函数
        dictType *type;
    
        // 存储一些额外的数据
        void *privdata;
    
        // 两个哈希表
        dictht ht[2];
    
        // 哈希表重置下标，指定的是哈希数组的数组下标
        int rehashidx; /* rehashing not in progress if rehashidx == -1 */
    
        // 绑定到哈希表的迭代器个数
        int iterators; /* number of iterators currently running */
    } dict;


**redisObject**，任何 value 都会被包装成一个 redisObject，redisObject 能指定 value 的类型，编码方式等数据属性。

    
    typedef struct redisObject {
        // 刚刚好 32 bits
    
        // 对象的类型，字符串/列表/集合/哈希表
        unsigned type:4;
    
        // 未使用的两个位
        unsigned notused:2;     /* Not used */
    
        // 编码的方式，redis 为了节省空间，提供多种方式来保存一个数据
        // 譬如：“123456789” 会被存储为整数 123456789
        unsigned encoding:4;
    
        // 当内存紧张，淘汰数据的时候用到
        unsigned lru:22;        /* lru time (relative to server.lruclock) */
    
        // 引用计数
        int refcount;
    
        // 数据指针
        void *ptr;
    } robj;


**zset**，是一个跳表，插入删除速度非常快。

    
    typedef struct zset {
        // 哈希表
        dict *dict;
    
        // 跳表
        zskiplist *zsl;
    } zset;


**adlist**，普通的双链表。

    
    typedef struct list {
        // 头指针
        listNode *head;
    
        // 尾指针
        listNode *tail;
    
        // 数据拷贝函数指针
        void *(*dup)(void *ptr);
    
        // 析构函数指针
        void (*free)(void *ptr);
    
        // 数据比较指针
        int (*match)(void *ptr, void *key);
    
        // 链表长度
        unsigned long len;
    } list;


**ziplist**，是一个压缩的双链表，实现了针对 CPU cache 的优化。ziplist 实际上一个字符串，通过一系列的算法来实现压缩双链表。

**intset**，整数集合。

    
    typedef struct intset {
        // 每个整数的类型
        uint32_t encoding;
    
        // intset 长度
        uint32_t length;
    
        // 整数数组
        int8_t contents[];
    } intset;


**sds**，字符串数据结构，因为经常涉及字符串的操作，redis 做了特殊的实现，文档中将其称为 Hacking String.

    
    typedef char *sds;


**zipmap**，已经被废弃，我不会讨论这个数据结构。


### redis 命令和相关的数据结构


以添加数据的一类命令 SET,HSET,LPUSH,SADD,ZADD 为例，分别看看哪个命令底层用了哪些数据结构。

**SET** 命令底层所使用的即为 sds，或者整型数据类型 int,long long 等，或者浮点型 float，double。不同的情况所使用的数据类不同，SET 底层所使用的数据类型是最为简单的。

**HSET** 命令底层所使用的即为压缩双链表 ziplist，而非哈希表 dict。

**LPUSH** 命令底层所使用的即为压缩双链表 ziplist。

**SADD** 命令情况较为特殊，SADD 所面向的是一个集合（set）。如果往集合总添加的数据都是整数，会采用整数集合 intset；如果集合中的数据有一个不为整数，会采用哈希表 dict。因此，会一个特殊的情况，假使前 N个数据都为整数，第 N+1个数据为非整数，如字符串，那么数据结构会从 intset 转换为 dict。

**ZADD** 也较为特殊，SADD 所面向的是一个有序集合（sorted set）。ZADD 底层数据结构可以采用跳表 skiplist 和哈希表 dict 的结合；也可以采用 ziplist。具体选用哪种需要看 server.zset_max_ziplist_entries 和 server.zset_max_ziplist_value 两个配置变量的设置。前者掺合 dict 是为了能快速查找某个成员是否存在于跳表中。有序集一个较为普遍的应用是排行榜。

我将在接下来的系列文章中一一讲解每一个数据结构，以及选用相应数据结构的目的。



Dylan 2014-6-9

[http://daoluan.github.io](http://daoluan.github.io/)
