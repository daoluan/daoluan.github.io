---
title: 无锁消息队列
date: 2014-12-10 15:16:27 Z
categories:
- linux
tags:
- lock free
- queue
- 无锁消息队列
author: daoluan
comments: true
layout: post
wordpress_id: 2436
---

### 背景


近期在项目中用到了无锁队列 （lock free queue）这个东西，在项目中后台需要收集数据，待收集完整后需要落地，如果收集和落地都由一个进程来做，效果不好。无锁队列是蛮实用的一种数据结构。譬如，当一些后台的任务，写数据库，日志文件等，会出现较长时间的阻塞，可以交由后台进程去处理。这时候就涉及 IPC 方面的知识。当然，完全可以使用 fifo，mq 之类的系统预置的调用，但频繁的系统调用是吃不消的。

一个解决方法是，在共享内存中实现无锁队列，逻辑进程往队列中 push 任务，后端服务进程从队列中 pop 任务，以提高逻辑进程的处理能力。


### **单个生产者与单个消费者**


如果一个共享队列只与一个生产者与一个消费者共享，那么此队列可以这么设计：

[![single_producer_0](http://daoluan.github.io/images/blog/2014/12/single_producer_0.png)](http://daoluan.github.io/images/blog/2014/12/single_producer_0.png)

在共享内存中， 分别维护 front 指针，rear 指针和循环队列，其中 front 指针指向队列头部，其值由生产者维护；rear 指针指向队列尾部，其值由消费者维护；循环队列是一个大数组。注意，front, rear 存储的是数据的下标而已，且**队列最后一个空间不可用，后者是为了方便作 full 判断。**

所以，当 front==rear 的时候，队列为空：

[![single_producer_1](http://daoluan.github.io/images/blog/2014/12/single_producer_1.png)](http://daoluan.github.io/images/blog/2014/12/single_producer_1.png)

当 (front+1)%MAX_QUEUE_SIZE==rear 的时候，队列满了：

[![single_producer_2](http://daoluan.github.io/images/blog/2014/12/single_producer_2.png)](http://daoluan.github.io/images/blog/2014/12/single_producer_2.png)

获取循环队列大小的时候，需要注意 front<rear 的情况：

    
    queue_size = (front-rear)<0 ? (front+MAX_QUEUE_SIZE-rear) : front-rear


此时，最简单的无锁共享队列即完成了。为，front, rear 指针分别由单个生产者和单个消费者维护（修改），这里不存在覆盖写等问题。后台进程可定期检测队列是否为空，非空的时候执行消费操作即可。经过讨论，项目中采用是这种数据结构并更新了系统设计方案（逻辑层和存储层分离），CPU 降低了 10%~


### **单个生产者与多个消费者**




#### 背景


多个进程共同维护一份数据的时候，非常容易出问题，譬如最常见的是丢失修改问题。要保证更新这些指针的时候是原子操作，才可以避规避这些情况，linux 下最常见的即是加锁。

在我们的项目中，生产者经过优化后能力超过了后端消费能力，于是想到增加消费者，但上面的“单个生产者与单个消费者”中描述的数据结构不能满足要求。在介绍解决方法之前，要介绍一下 CAS 操作。


#### CAS 简介


如何保证原子操作？简单加减运算的原子性能通过 CPU 提供的 CAS 原子操作 **CMPXCHG** 指令来保证。CAS 即 Compare & Set，或者 Compare & Swap，这有点类似于乐观锁。即在正在的修改操作之前，先读取旧的值 old，在修改完成之后，再一次读取旧值是否更改，如果更改则再尝试，直到修改成功为止。

c 语言描述可以写成：

    
    bool CAS(type *accum, type *dest, int newval)
    {
      if ( *accum == *dest ) {
          *dest = newval;
          return true;
      }
      return false;
    }


CAS 操作帮忙解决了多进程维护一份数据的同步问题。


#### **具体实现**


具体实现需要在“单个生产者与单个消费者”中描述的方法上，稍微修改一下。入队操作都是一样的，只有一个生产者，维护 front 值。出队操作稍有不同。

[![single_producer_multi_customers_0](http://daoluan.github.io/images/blog/2014/12/single_producer_multi_customers_0.png)](http://daoluan.github.io/images/blog/2014/12/single_producer_multi_customers_0.png)

先保存旧的 rear ->old_rear，接着拷贝数据，

[![single_producer_multi_customers_1](http://daoluan.github.io/images/blog/2014/12/single_producer_multi_customers_1.png)](http://daoluan.github.io/images/blog/2014/12/single_producer_multi_customers_1.png)

CAS(&rear, old_rear, rear+1)，如果用数组模拟环形数组，考虑越界的情况，

[![single_producer_multi_customers_2](http://daoluan.github.io/images/blog/2014/12/single_producer_multi_customers_2.png)](http://daoluan.github.io/images/blog/2014/12/single_producer_multi_customers_2.png)

不成功，重新开始。


### 多个生产者与多个消费者


这种情况下，要考虑多个生产者之间 push 操作同步的问题。

我们设置三个值：front, rear, write_index. 前两个值和上面描述的一样，分别是队列头部和尾部，write_index 的作用是为生产者在 push 的时候预留空间，在无 push 操作的时候，write_index==front。
[![multi_producers_multi_customers_0](http://daoluan.github.io/images/blog/2014/12/multi_producers_multi_customers_0.png)](http://daoluan.github.io/images/blog/2014/12/multi_producers_multi_customers_0.png)

在入队的时候，保存旧的 write_index -> old_write_index，接着 CAS(&write_index, old_write_index, old_write_index+1). 这一步不成功，需要重复执行。

[![multi_producers_multi_customers_1](http://daoluan.github.io/images/blog/2014/12/multi_producers_multi_customers_1.png)](http://daoluan.github.io/images/blog/2014/12/multi_producers_multi_customers_1.png)

接着将数据写到对应的位置上，

[![multi_producers_multi_customers_2](http://daoluan.github.io/images/blog/2014/12/multi_producers_multi_customers_2.png)](http://daoluan.github.io/images/blog/2014/12/multi_producers_multi_customers_2.png)

最后 CAS(&front, old_write_index, old_write_index+1)，直到 CAS 成功为止。这一步不成功，需要重复执行。

[![multi_producers_multi_customers_3](http://daoluan.github.io/images/blog/2014/12/multi_producers_multi_customers_3.png)](http://daoluan.github.io/images/blog/2014/12/multi_producers_multi_customers_3.png)

在网络上的资料中，还在这最后一步**不成功的情况**下添了点花：不成功的时候，调用 sched_yield(); 主要目的是让该生产者主动让出 cpu 给其他的生产者，因为可能其他生产者正在执行 push 操作，这样它就可以完成 push 操作了。确实，这在处理器数量少于生产者数量的时候，对性能来说是比较关键的。

这里涉及两个 CAS 操作。**如果有两个进程同时 push，A 先执行 push，但结果 B 先完成 push 操作，结果是 A push 操作不成功，但它会继续尝试 push 直到成功为止。**

出队的操作和“单个生产者与多个消费者”中描述的方法一样。在现有的项目中，较少遇到“多个生产者与多个消费者”的场景，这样复杂的情况，可能还不如开多个队列，让不同的生产者去 push 不同的队列，以简化问题。

推荐看《参考》中的资料，**无锁实现说白了就是在需要同步的地方（会出现竞争的地方）使用原子操作函数 (?)。**另外，上面的无锁消息队列都是基于线性数组的，还有一种是基于链表的做法，这里有一份实现代码，推荐看：[https://github.com/haipome/lock_free_queue](https://github.com/haipome/lock_free_queue)

参考：

[http://www.codeproject.com/Articles/153898/Yet-another-implementation-of-a-lock-free-circular](http://www.codeproject.com/Articles/153898/Yet-another-implementation-of-a-lock-free-circular)
[http://coolshell.cn/articles/8239.html](http://coolshell.cn/articles/8239.html)
[http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.53.8674&rep=rep1&type=pdf](http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.53.8674&rep=rep1&type=pdf)



Dylan 2014-12-10

[http://daoluan.github.io](http://daoluan.github.io/)
