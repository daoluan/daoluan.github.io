---
title: ssdb 如何利用 leveldb
date: 2019-07-29 03:52:00 Z
categories:
- 存储
author: dylanzheng
comments: true
layout: post
---

ssdb 号称比 Redis 要快，里面用了 leveldb 来实现。和 Redis 的实现不一样，Redis 有一套协议来写 binlog。ssdb 直接使用了 leveldb。

我一直好奇他是怎么利用 leveldb 的。按说 leveldb 是 kv 存储的，binlog 要求有顺序。

看了下实现，ssdh 对于每个 binlog 都有一个同步序号，是递增的，存入 leveldb 时只要以这个序号作为 key，那迭代的时候就是从 0 开始递增，从而保证是有序的。