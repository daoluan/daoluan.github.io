---
author: dylanzheng
comments: true
date: 2019-07-29 15:52:02 +0000
layout: post
title: ssdb 如何利用 leveldb
categories:
- 存储
tags: []
slug: ''

---
ssdb 号称比 Redis 要快，里面用了 leveldb 来实现。和 Redis 的实现不一样，Redis 有一套协议来写 binlog。ssdb 直接使用了 leveldb。

我一直好奇他是怎么利用 leveldb 的。按说 leveldb 是 kv 存储的，binlog 要求有顺序。