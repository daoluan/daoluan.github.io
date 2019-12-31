---
title: 深入剖析 redis 数据结构 intset
date: 2014-07-02 16:29:16 Z
categories:
- linux
tags:
- intset
- redis
- 数据结构
author: daoluan
comments: true
layout: post
wordpress_id: 2403
---

intset 和 dict 都是 sadd 命令的底层数据结构，当添加的所有数据都是整数时，会使用前者；否则使用后者。**特别的**，当遇到添加数据为字符串，即不能表示为整数时，redis 会把数据结构转换为 dict，即把 intset 中的数据全部搬迁到 dict。

本片展开的是 intset，dict 的文章可以参看之前写的《深入剖析 redis 数据结构 dict》。


### intset 结构体


intset 底层本质是一个**有序的、不重复的、整型**的数组，支持不同类型整数。

    
    typedef struct intset {
        // 每个整数的类型
        uint32_t encoding;
    
        // intset 长度
        uint32_t length;
    
        // 整数数组
        int8_t contents[];
    } intset;


encoding 能下面的三个值：分别是 16，32 和 64位整数：

    
    /* Note that these encodings are ordered, so:
    * INTSET_ENC_INT16 < INTSET_ENC_INT32 < INTSET_ENC_INT64. */
    #define INTSET_ENC_INT16 (sizeof(int16_t))
    #define INTSET_ENC_INT32 (sizeof(int32_t))
    #define INTSET_ENC_INT64 (sizeof(int64_t))




### intset 搜索


intset 是有序的整数数组，可以用二分搜索查找。

    
    static uint8_t intsetSearch(intset *is, int64_t value, uint32_t *pos) {
        int min = 0, max = intrev32ifbe(is->length)-1, mid = -1;
        int64_t cur = -1;
    
        /* The value can never be found when the set is empty */
        // 集合为空
        if (intrev32ifbe(is->length) == 0) {
            if (pos) *pos = 0;
            return 0;
        } else {
            /* Check for the case where we know we cannot find the value,
             * but do know the insert position. */
            // value 比最大元素还大
            if (value > _intsetGet(is,intrev32ifbe(is->length)-1)) {
                if (pos) *pos = intrev32ifbe(is->length);
                return 0;
            // value 比最小元素还小
            } else if (value < _intsetGet(is,0)) {
                if (pos) *pos = 0;
                return 0;
            }
        }
    
        // 二分查找
        while(max >= min) {
            mid = (min+max)/2;
            cur = _intsetGet(is,mid);
            if (value > cur) {
                min = mid+1;
            } else if (value < cur) {
                max = mid-1;
            } else {
                break;
            }
        }
    
        if (value == cur) {
            if (pos) *pos = mid;
            return 1;
        } else {
            if (pos) *pos = min;
            return 0;
        }
    }




### intset 插入


intset 实现中比较远有意思的是插入算法部分。

    
    /* Insert an integer in the intset */
    intset *intsetAdd(intset *is, int64_t value, uint8_t *success) {
        uint8_t valenc = _intsetValueEncoding(value);
        uint32_t pos;
        if (success) *success = 1;
    
        /* Upgrade encoding if necessary. If we need to upgrade, we know that
         * this value should be either appended (if > 0) or prepended (if < 0),
         * because it lies outside the range of existing values. */
        // 需要插入整数的所需内存超出了原有集合整数的范围，即内存类型不同，
        // 则升级整数类型
        if (valenc > intrev32ifbe(is->encoding)) {
            /* This always succeeds, so we don't need to curry *success. */
            return intsetUpgradeAndAdd(is,value);
    
        // 正常，分配内存，插入
        } else {
            // intset 内部不允许重复
            /* Abort if the value is already present in the set.
             * This call will populate "pos" with the right position to insert
             * the value when it cannot be found. */
            if (intsetSearch(is,value,&pos)) {
                if (success) *success = 0;
                return is;
            }
    
            // realloc
            is = intsetResize(is,intrev32ifbe(is->length)+1);
    
            // 迁移内存，腾出空间给新的数据。intsetMoveTail() 完成内存迁移工作
            if (pos < intrev32ifbe(is->length)) intsetMoveTail(is,pos,pos+1);
        }
    
        // 在腾出的空间中设置新的数据
        _intsetSet(is,pos,value);
    
        // 更新 intset size
        is->length = intrev32ifbe(intrev32ifbe(is->length)+1);
        return is;
    }
    
    // 升级整数类型，譬如从 short->int。当插入数据的内存占用比原有数据大
    // 的时候，会被调用
    /* Upgrades the intset to a larger encoding and inserts the given integer. */
    static intset *intsetUpgradeAndAdd(intset *is, int64_t value) {
        uint8_t curenc = intrev32ifbe(is->encoding);
        uint8_t newenc = _intsetValueEncoding(value);
        int length = intrev32ifbe(is->length);
    
        // value<0 头插，value>0 尾插
        int prepend = value < 0 ? 1 : 0;
    
        // realloc
        /* First set new encoding and resize */
        is->encoding = intrev32ifbe(newenc);
        is = intsetResize(is,intrev32ifbe(is->length)+1);
    
        // 逆向处理，防止数据被覆盖，一般的插入排序步骤
        /* Upgrade back-to-front so we don't overwrite values.
         * Note that the "prepend" variable is used to make sure we have an empty
         * space at either the beginning or the end of the intset. */
        while(length--)
            _intsetSet(is,length+prepend,_intsetGetEncoded(is,length,curenc));
    
        // value<0 放在集合开头，否则放在集合末尾。
        // 因为，此函数是对整数所占内存进行升级，意味着 value 不是在集合中最大就是最小！
        /* Set the value at the beginning or the end. */
        if (prepend)
            _intsetSet(is,0,value);
        else
            _intsetSet(is,intrev32ifbe(is->length),value);
    
        // 更新 set size
        is->length = intrev32ifbe(intrev32ifbe(is->length)+1);
        return is;
    }




Dylan 2014-7-3

[http://daoluan.net](http://daoluan.net/)


