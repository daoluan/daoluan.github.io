---
title: 深入剖析 redis 数据结构 redisObject
date: 2014-06-24 15:49:12 Z
categories:
- linux
tags:
- redis
- redisObject
- 数据结构
author: daoluan
comments: true
layout: post
wordpress_id: 2378
---

redis 是 key-value 存储系统，其中 key 类型一般为字符串，而 value 类型则为 redis 对象（redis object）。redis 对象可以绑定各种类型的数据，譬如 string、list 和 set。

    
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


redis 中定义了 struct redisObject，**它是一个简单优秀的数据结构**，因为在 redisObject 中数据属性和数据分开来了，其中，数据属性包括数据类型，存储编码方式，淘汰时钟，引用计数。下面一一展开：

数据类型，标记了 redis 对象绑定的是什么类型的数据，有下面几种可能的值；

    
    /* Object types */
    #define REDIS_STRING 0
    #define REDIS_LIST 1
    #define REDIS_SET 2
    #define REDIS_ZSET 3
    #define REDIS_HASH 4


存储编码方式，一个数据，可以以多种方式存储。譬如，数据类型为 REDIS_SET 的数据编码方式可能为 REDIS_ENCODING_HT，也可能为 REDIS_ENCODING_INTSET。

    
    /* Objects encoding. Some kind of objects like Strings and Hashes can be
    * internally represented in multiple ways. The 'encoding' field of the object
    * is set to one of this fields for this object. */
    #define REDIS_ENCODING_RAW 0     /* Raw representation */
    #define REDIS_ENCODING_INT 1     /* Encoded as integer */
    #define REDIS_ENCODING_HT 2      /* Encoded as hash table */
    #define REDIS_ENCODING_ZIPMAP 3  /* Encoded as zipmap */
    #define REDIS_ENCODING_LINKEDLIST 4 /* Encoded as regular linked list */
    #define REDIS_ENCODING_ZIPLIST 5 /* Encoded as ziplist */
    #define REDIS_ENCODING_INTSET 6  /* Encoded as intset */
    #define REDIS_ENCODING_SKIPLIST 7  /* Encoded as skiplist */


淘汰时钟，redis 对数据集占用内存的大小有「实时」的计算，当超出限额时，会淘汰超时的数据。

引用计数，一个 redis 对象可能被多个指针引用。当需要增加或者减少引用的时候，必须调用相应的函数，程序员必须遵守这一准则。

    
    // 增加 redis 对象引用
    void incrRefCount(robj *o) {
        o->refcount++;
    }
    
    // 减少 redis 对象引用。特别的，引用为零的时候会销毁对象
    void decrRefCount(robj *o) {
        if (o->refcount <= 0) redisPanic("decrRefCount against refcount <= 0");
    
        // 如果取消的是最后一个引用，则释放资源
        if (o->refcount == 1) {
            // 不同数据类型，销毁操作不同
            switch(o->type) {
            case REDIS_STRING: freeStringObject(o); break;
            case REDIS_LIST: freeListObject(o); break;
            case REDIS_SET: freeSetObject(o); break;
            case REDIS_ZSET: freeZsetObject(o); break;
            case REDIS_HASH: freeHashObject(o); break;
            default: redisPanic("Unknown object type"); break;
            }
            zfree(o);
        } else {
            o->refcount--;
        }
    }


得益于 redis 是单进程单线程工作的，所以增加/减少引用的操作不必保证原子性，这在 memcache 中是做不到的。

struct redisObject 把最后一个指针留给了真正的数据。



Dylan 2014-6-18

[http://daoluan.github.io](http://daoluan.github.io/)
