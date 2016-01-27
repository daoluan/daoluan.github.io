---
author: daoluan
comments: true
date: 2014-06-16 12:26:07+00:00
layout: post
slug: decode-redis-data-struct-dict
title: 深入剖析 redis 数据结构 dict
wordpress_id: 2370
categories:
- linux
tags:
- dict
- redis
- 数据结构
---

### redis 的键值对存储在哪里


在 redis 中有多个数据集，数据集采用的数据结构是哈希表，用以存储键值对。默认所有的客户端都是使用第一个数据集，如果客户端有需要可以使用 select 命令来选择不同的数据集。redis 在初始化服务器的时候就会初始化所有的数据集：

    
    void initServer() {
        ......
        // 分配数据集空间
        server.db = zmalloc(sizeof(redisDb)*server.dbnum);
        ......
        // 初始化 redis 数据集
        /* Create the Redis databases, and initialize other internal state. */
        for (j = 0; j < server.REDIS_DEFAULT_DBNUM; j++) { // 初始化多个数据库
            // 哈希表，用于存储键值对
            server.db[j].dict = dictCreate(&dbDictType,NULL);
    
            // 哈希表，用于存储每个键的过期时间
            server.db[j].expires = dictCreate(&keyptrDictType,NULL);
            ......
        }
        ......
    }




### 哈希表 dict


[![redis_ds_dict](http://daoluan.net/blog/wp-content/uploads/2014/06/redis_ds_dict.png)](http://daoluan.net/blog/wp-content/uploads/2014/06/redis_ds_dict.png)

数据集采用的数据结构是哈希表，数据真正存储在哈希表中，用开链法解决冲突问题，struct dictht 即为一个哈希表。但在 redis 哈希表数据结构 struct dict 中有两个哈希表，下文将两个哈希表分别称为第一个和第二个哈希表，**redis 提供两个哈希表是为了能够在不中断服务的情况下扩展（expand）哈希表，**很有趣的一部分。

    
    typedef struct dictEntry {
        void *key;
        union {
            void *val;
            uint64_t u64;
            int64_t s64;
        } v;
        struct dictEntry *next;
    } dictEntry;
    
    // 要存储多种多样的数据结构，势必不同的数据有不同的哈希算法，不同的键值比较算法，不同的析构函数。
    typedef struct dictType {
        // 哈希函数
        unsigned int (*hashFunction)(const void *key);
    
        void *(*keyDup)(void *privdata, const void *key);
        void *(*valDup)(void *privdata, const void *obj);
    
        // 比较函数
        int (*keyCompare)(void *privdata, const void *key1, const void *key2);
    
        // 键值析构函数
        void (*keyDestructor)(void *privdata, void *key);
        void (*valDestructor)(void *privdata, void *obj);
    } dictType;
    
    // 一般哈希表数据结构
    /* This is our hash table structure. Every dictionary has two of this as we
    * implement incremental rehashing, for the old to the new table. */
    typedef struct dictht {
        // 两个哈希表
        dictEntry **table;
    
        // 哈希表的大小
        unsigned long size;
    
        // 哈希表大小掩码
        unsigned long sizemask;
    
        // 哈希表中数据项数量
        unsigned long used;
    } dictht;
    
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




### 扩展哈希表


redis 为每个数据集配备两个哈希表，能在不中断服务的情况下扩展哈希表。平时哈希表扩展的做法是，为新的哈希表另外开辟一个空间，将原哈希表的数据重新计算哈希值，以移动到新哈希表。如果原哈希表数据过多，中间大量的计算过程会耗费大量时间。

redis 扩展哈希表的做法有点小聪明：为第二个哈希表分配新空间，其空间大小为原哈希表键值对数量的两倍（是的，没错），接着逐步将第一个哈希表中的数据移动到第二个哈希表；待移动完毕后，将第二个哈希值赋值给第一个哈希表，第二个哈希表置空。在这个过程中，数据会分布在两个哈希表，这时候就要求在 CURD 时，都要考虑两个哈希表。

而这里，将第一个哈希表中的数据移动到第二个哈希表被称为**重置哈希（rehash）。**


### 重置哈希表


在 CURD 的时候会执行一步的重置哈希表操作，在服务器定时程序 serverCorn() 中会执行一定时间的重置哈希表操作。为什么在定时程序中重置哈希表了，还 CURD 的时候还要呢？或者反过来问。一个可能的原因是 redis 做了两手准备：在服务器空闲的时候，定时程序会完成重置哈希表；在服务器过载的时候，更多重置哈希表操作会落在 CURD 的服务上。

下面是重置哈希表的函数，其主要任务就是选择哈希表中的一个位置上的单链表，重新计算哈希值，放到第二个哈希表。

    
    int dictRehash(dict *d, int n) {
        // 重置哈希表结束，直接返回
        if (!dictIsRehashing(d)) return 0;
    
        while(n--) {
            dictEntry *de, *nextde;
    
            // 第一个哈希表为空，证明重置哈希表已经完成，将第二个哈希表赋值给第一个，
            // 结束
            /* Check if we already rehashed the whole table... */
            if (d->ht[0].used == 0) {
                zfree(d->ht[0].table);
                d->ht[0] = d->ht[1];
                _dictReset(&d->ht[1]);
                d->rehashidx = -1;
                return 0;
            }
    
            /* Note that rehashidx can't overflow as we are sure there are more
             * elements because ht[0].used != 0 */
            assert(d->ht[0].size > (unsigned)d->rehashidx);
    
            // 找到哈希表中不为空的位置
            while(d->ht[0].table[d->rehashidx] == NULL) d->rehashidx++;
            de = d->ht[0].table[d->rehashidx];
    
            // 此位置的所有数据移动到第二个哈希表
            /* Move all the keys in this bucket from the old to the new hash HT */
            while(de) {
                unsigned int h;
                nextde = de->next;
    
                /* Get the index in the new hash table */
                // 计算哈希值
                h = dictHashKey(d, de->key) & d->ht[1].sizemask;
    
                // 头插法
                de->next = d->ht[1].table[h];
                d->ht[1].table[h] = de;
    
                // 更新哈希表中的数据量
                d->ht[0].used--;
                d->ht[1].used++;
    
                de = nextde;
            }
            // 置空
            d->ht[0].table[d->rehashidx] = NULL;
    
            // 指向哈希表的下一个位置
            d->rehashidx++;
        }
        return 1;
    }




### 低效率的哈希表添加替换


在 redis 添加替换的时候，都先要查看数据集中是否已经存在该键，也就是一个查找的过程，如果一个redis 命令导致过多的查找，会导致效率低下。可能是为了扬长避短，即高读性能和低写性能，redis 中数据的添加和替换效率不高，特别是替换效率低的恶心。

[![search_in_call_chain](http://daoluan.net/blog/wp-content/uploads/2014/06/search_in_call_chain.png)](http://daoluan.net/blog/wp-content/uploads/2014/06/search_in_call_chain.png)

在 redis SET 命令的调用链中，添加键值对会导致了 2次的键值对查找；替换键值对最多会导致 4次的键值对查找。在 dict 的实现中，dictFind() 和 _dictIndex() 都会导致键值对的查找，详细可以参看源码。所以，从源码来看，经常在 redis 上写不是一个明智的选择。


### 哈希表的迭代


在 RDB 和 AOF 持久化操作中，都需要迭代哈希表。哈希表的遍历本身难度不大，但因为每个数据集都有两个哈希表，所以遍历哈希表的时候也需要注意遍历两个哈希表：第一个哈希表遍历完毕的时候，如果发现重置哈希表尚未结束，则需要继续遍历第二个哈希表。

    
    // 迭代器取下一个数据项的入口
    dictEntry *dictNext(dictIterator *iter)
    {
        while (1) {
            if (iter->entry == NULL) {
                dictht *ht = &iter->d->ht[iter->table];
                // 新的迭代器
                if (iter->index == -1 && iter->table == 0) {
                    if (iter->safe)
                        iter->d->iterators++;
                    else
                        iter->fingerprint = dictFingerprint(iter->d);
                }
                iter->index++;
    
                // 下标超过了哈希表大小，不合法
                if (iter->index >= (signed) ht->size) {
                    // 如果正在重置哈希表，redis 会尝试在第二个哈希表上进行迭代，
                    // 否则真的就不合法了
    
                    if (dictIsRehashing(iter->d) && iter->table == 0) {
                    // 正在重置哈希表，证明数据正在从第一个哈希表整合到第二个哈希表，
                    // 则指向第二个哈希表
                        iter->table++;
                        iter->index = 0;
                        ht = &iter->d->ht[1];
                    } else {
                    // 否则迭代完毕，这是真正不合法的情况
                        break;
                    }
                }
    
                // 取得数据项入口
                iter->entry = ht->table[iter->index];
            } else {
                // 取得下一个数据项人口
                iter->entry = iter->nextEntry;
            }
    
            // 迭代器会保存下一个数据项的入口，因为用户可能会删除此函数返回的数据项
            // 入口，如此会导致迭代器失效，找不到下一个数据项入口
            if (iter->entry) {
                /* We need to save the 'next' here, the iterator user
                 * may delete the entry we are returning. */
                iter->nextEntry = iter->entry->next;
                return iter->entry;
            }
        }
        return NULL;
    }




捣乱 2014-6-16

[http://daoluan.net](http://daoluan.net/)
