---
title: 深入剖析 redis 数据结构 ziplist
date: 2014-06-20 01:21:35 Z
categories:
- linux
tags:
- redis
- ziplist
- 数据结构
author: daoluan
comments: true
layout: post
wordpress_id: 2387
---

### 概述


在 redis 中，list 有两种存储方式：双链表（LinkedList）和压缩双链表（ziplist）。双链表即普通数据结构中遇到的，在 adlist.h 和 adlist.c 中实现。压缩双链表以连续的内存空间来表示双链表，压缩双链表节省前驱和后驱指针的空间（8B），这在小的 list 上，压缩效率是非常明显的；压缩双链表在 ziplist.h 和 ziplist.c 中实现。

这篇主要详述压缩双链表，普通双链表可以参看其他资料。


### 压缩双链表的具体实现


在压缩双链表中，节省了前驱和后驱指针的空间，共 8个字节，**这让数据在内存中更为紧凑**。只要清晰的描述每个数据项的边界，就可以轻易得到后驱数据项的位置；只要描述前驱数据项的大小，就可以定位前驱数据项的位置，redis 就是这么做的。

ziplist 的格式可以表示为：

    
    <zlbytes><zltail><zllen><entry>...<entry><zlend>


zlbytes 是 ziplist 占用的空间；zltail 是最后一个数据项的偏移位置，这方便逆向遍历链表，也是双链表的特性；zllen 是数据项 entry 的个数；zlend 就是 255，占 1B.详细展开 entry 的结构。

entry 的格式即为典型的 type-lenght-value，即 TLV，表述如下：

    
    |<prelen><<encoding+lensize><len>><data>|
    |---1----------------2--------------3---|


域 1）是前驱数据项的大小。因为不用描述前驱的数据类型，描述较为简单。

域 2） 是此数据项的的类型和数据大小。为了节省空间，redis 预设定了多种长度的字符串和整数。

    
    3种长度的字符串
    #define ZIP_STR_06B (0 << 6)
    #define ZIP_STR_14B (1 << 6)
    #define ZIP_STR_32B (2 << 6)
    
    5种长度的整数
    #define ZIP_INT_16B (0xc0 | 0<<4)
    #define ZIP_INT_32B (0xc0 | 1<<4)
    #define ZIP_INT_64B (0xc0 | 2<<4)
    #define ZIP_INT_24B (0xc0 | 3<<4)
    #define ZIP_INT_8B 0xfe


域 3）为真正的数据。

透过 ziplist 查找函数 ziplistFind()，熟悉 ziplist entry 对数据格式：

    
    // 在 ziplist 中查找数据项
    /* Find pointer to the entry equal to the specified entry. Skip 'skip' entries
    * between every comparison. Returns NULL when the field could not be found. */
    unsigned char *ziplistFind(unsigned char *p, unsigned char *vstr, unsigned int vlen, unsigned int skip) {
        int skipcnt = 0;
        unsigned char vencoding = 0;
        long long vll = 0;
    
        while (p[0] != ZIP_END) {
            unsigned int prevlensize, encoding, lensize, len;
            unsigned char *q;
    
            ZIP_DECODE_PREVLENSIZE(p, prevlensize);
    
            // 跳过前驱数据项大小，解析数据项大小
            // len 为 data 大小
            // lensize 为 len 所占内存大小
            ZIP_DECODE_LENGTH(p + prevlensize, encoding, lensize, len);
    
            // q 指向 data
            q = p + prevlensize + lensize;
    
            if (skipcnt == 0) {
                /* Compare current entry with specified entry */
                if (ZIP_IS_STR(encoding)) {
                // 字符串比较
                    if (len == vlen && memcmp(q, vstr, vlen) == 0) {
                        return p;
                    }
                } else {
                // 整数比较
                    /* Find out if the searched field can be encoded. Note that
                     * we do it only the first time, once done vencoding is set
                     * to non-zero and vll is set to the integer value. */
                    if (vencoding == 0) {
                        // 尝试将 vstr 解析为整数
                        if (!zipTryEncoding(vstr, vlen, &vll, &vencoding)) {
                            /* If the entry can't be encoded we set it to
                             * UCHAR_MAX so that we don't retry again the next
                             * time. */
                            // 不能编码为数字！！！会导致当前查找的数据项被跳过
                            vencoding = UCHAR_MAX;
                        }
                        /* Must be non-zero by now */
                        assert(vencoding);
                    }
    
                    /* Compare current entry with specified entry, do it only
                     * if vencoding != UCHAR_MAX because if there is no encoding
                     * possible for the field it can't be a valid integer. */
                    if (vencoding != UCHAR_MAX) {
                        // 读取整数
                        long long ll = zipLoadInteger(q, encoding);
                        if (ll == vll) {
                            return p;
                        }
                    }
                }
    
                /* Reset skip count */
                skipcnt = skip;
            } else {
                /* Skip entry */
                skipcnt--;
            }
    
            // 移动到 ziplist 的下一个数据项
            /* Move to next entry */
            p = q + len;
        }
    
        // 没有找到
        return NULL;
    }


注意，ziplist 每次插入新的数据都要 realloc。


### 为什么要用 ziplist


redis HSET 命令官网的描述是：


<blockquote>Sets field in the hash stored at key to value. If key does not exist, a new key holding a hash is created. If field already exists in the hash, it is overwritten.</blockquote>


实际上，HSET 底层所使用的数据结构正是上面所说的 ziplist，而不是平时所说的 hashtable。

那为什么要使用 ziplist，反对的理由是查找来说，（ziplist O(N)）VS（hashtable O(1)）？redis 可是为内存节省想破了头。首先 ziplist 比 hashtable 更节省内存，再者，**redis 考虑到如果数据紧凑的 ziplist 能够放入 CPU 缓存**（hashtable 很难，因为它是非线性的），那么查找算法甚至会比 hashtable 要快！。ziplist 由此有性能和内存空间的有事。



Dylan 2014-6-20

[http://daoluan.github.io](http://daoluan.github.io/)
