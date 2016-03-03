---
author: daoluan
comments: true
date: 2014-06-28 13:10:57+00:00
layout: post
slug: decode-redis-transaction
title: 深入剖析 redis 事务机制
wordpress_id: 2396
categories:
- linux
tags:
- redis
- transaction
- 事务
---

### redis 事务简述


MULTI，EXEC，DISCARD，WATCH 四个命令是 redis 事务的四个基础命令。其中：



	
  * MULTI，告诉 redis 服务器开启一个事务。注意，只是开启，而不是执行

	
  * EXEC，告诉 redis 开始执行事务

	
  * DISCARD，告诉 redis 取消事务

	
  * WATCH，监视某一个键值对，它的作用是在事务执行之前如果监视的键值被修改，事务会被取消。


在介绍 redis 事务之前，先来展开 redis 命令队列的内部实现。


### redis 命令队列


redis 允许一个客户端不间断执行多条命令：发送 MULTI 后，用户键入多条命令；再发送 EXEC 即可不间断执行之前输入的多条命令。因为，redis 是单进程单线的工作模式，因此多条命令的执行是不会被中断的。

    
    > MULTI
    OK
    > INCR foo
    QUEUED
    > INCR bar
    QUEUED
    > EXEC
    1) (integer) 1
    2) (integer) 1


内部实现不难：redis 服务器收到来自客户端的 MULTI 命令后，为客户端保存一个命令队列结构体，直到收到 EXEC 后才开始执行命令队列中的命令。

下面是命令队列的数据结构：

    
    // 命令结构体，命令队列专用
    /* Client MULTI/EXEC state */
    typedef struct multiCmd {
        // 命令参数
        robj **argv;
    
        // 参数个数
        int argc;
    
        // 命令结构体，包含了与命令相关的参数，譬如命令执行函数
        // 如需更详细了解，参看 redis.c 中的 redisCommandTable 全局参数
        struct redisCommand *cmd;
    } multiCmd;
    
    // 命令队列结构体
    typedef struct multiState {
        // 命令队列
        multiCmd *commands;     /* Array of MULTI commands */
    
        // 命令的个数
        int count;              /* Total number of MULTI commands */
    
        // 以下两个参数暂时没有用到，和主从复制有关
        int minreplicas;        /* MINREPLICAS for synchronous replication */
        time_t minreplicas_timeout; /* MINREPLICAS timeout as unixtime. */
    } multiState;


通由上面给出的 redis 客户端操作，来看看 redis 服务器的状态变化：

    
    > MULTI
    OK
    > INCR foo
    QUEUED
    > INCR bar
    QUEUED
    > EXEC
    1) (integer) 1
    2) (integer) 1


[![redis_transaction](http://md.daoluan.net/images/blog/2014/06/redis_transaction.png)](http://md.daoluan.net/images/blog/2014/06/redis_transaction.png)

processCommand() 函数中的一段代码可以窥探命令入队的操作：

    
    // 执行命令
    int processCommand(redisClient *c) {
        ......
    
        // 加入命令队列的情况
        /* Exec the command */
        if (c->flags & REDIS_MULTI &&
            c->cmd->proc != execCommand && c->cmd->proc != discardCommand &&
            c->cmd->proc != multiCommand && c->cmd->proc != watchCommand)
        {
            // 命令入队
            queueMultiCommand(c);
            addReply(c,shared.queued);
    
        // 真正执行命令。
        // 注意，如果是设置了多命令模式，那么不是直接执行命令，而是让命令入队
        } else {
            call(c,REDIS_CALL_FULL);
            if (listLength(server.ready_keys))
                handleClientsBlockedOnLists();
        }
        return REDIS_OK;
    }




### 键值的监视


稍后再展开事务执行和取消的部分。

redis 的官方文档上说，WATCH 命令是为了让 redis 拥有 check-and-set(CAS)的特性。CAS 的意思是，一个客户端在修改某个值之前，要检测它是否更改；如果没有更改，修改操作才能成功。

一个不含 CAS 特性的例子：



<table cellpadding="2" width="100%" cellspacing="0" border="1" >
<tbody >
<tr >

<td valign="top" >
</td>

<td valign="top" >client A
</td>

<td valign="top" >clien B
</td>
</tr>
<tr >

<td valign="top" >0
</td>

<td valign="top" >get score(score=10)
</td>

<td valign="top" >
</td>
</tr>
<tr >

<td valign="top" >1
</td>

<td valign="top" >
</td>

<td valign="top" >get score(score=10)
</td>
</tr>
<tr >

<td valign="top" >2
</td>

<td valign="top" >temp=score+1(temp=11)
</td>

<td valign="top" >


temp=score+1(temp=11)

</td>
</tr>
<tr >

<td valign="top" >3
</td>

<td valign="top" >
</td>

<td valign="top" >set score temp(score=11)
</td>
</tr>
<tr >

<td valign="top" >4
</td>

<td valign="top" >


set score temp(score=11)

</td>

<td valign="top" >
</td>
</tr>
<tr >

<td valign="top" >5
</td>

<td valign="top" >final: score=11
</td>

<td valign="top" >


final: score=11

</td>
</tr>
</tbody>
</table>



含有 CAS 特性的例子：



<table cellpadding="2" width="100%" cellspacing="0" border="1" >
<tbody >
<tr >

<td valign="top" >
</td>

<td valign="top" >client A
</td>

<td valign="top" >clien B
</td>
</tr>
<tr >

<td valign="top" >0
</td>

<td valign="top" >get score(score=10)
</td>

<td valign="top" >
</td>
</tr>
<tr >

<td valign="top" >1
</td>

<td valign="top" >
</td>

<td valign="top" >get score(score=10)
</td>
</tr>
<tr >

<td valign="top" >2
</td>

<td valign="top" >temp=score+1(temp=11)
</td>

<td valign="top" >


temp=score+1(temp=11)

</td>
</tr>
<tr >

<td valign="top" >3
</td>

<td valign="top" >


（服务器标记 score 已经被修改）

</td>

<td valign="top" >set score temp(score=11)
</td>
</tr>
<tr >

<td valign="top" >4
</td>

<td valign="top" >


set score temp(score=11) (failed!!!)

</td>

<td valign="top" >
</td>
</tr>
<tr >

<td valign="top" >5
</td>

<td valign="top" >final: score=11
</td>

<td valign="top" >


final: score=11

</td>
</tr>
<tr >

<td valign="top" >6
</td>

<td valign="top" >


get score(score=11)

</td>

<td valign="top" >
</td>
</tr>
<tr >

<td valign="top" >7
</td>

<td valign="top" >


temp=score+1(temp=12)

</td>

<td valign="top" >
</td>
</tr>
<tr >

<td valign="top" >8
</td>

<td valign="top" >


set score temp(score=12)

</td>

<td valign="top" >
</td>
</tr>
<tr >

<td valign="top" >9
</td>

<td valign="top" >


final: score=12

</td>
</tr>
</tbody>
</table>



在后一个例子中，client A 第一次尝试修改失败，因为 client B 修改了 score.client A 失败过后，再次尝试修改才成功。**redis 事务的 CAS 特性借助了键值的监视。**

redis 数据集结构体 redisDB 和客户端结构体 redisClient 都会保存键值监视的相关数据。

[![redis_watched_keys](http://md.daoluan.net/images/blog/2014/06/redis_watched_keys.png)](http://md.daoluan.net/images/blog/2014/06/redis_watched_keys.png)

监视键值的过程：

    
    // WATCH 命令执行函数
    void watchCommand(redisClient *c) {
        int j;
    
        // WATCH 命令不能在 MULTI 和 EXEC 之间调用
        if (c->flags & REDIS_MULTI) {
            addReplyError(c,"WATCH inside MULTI is not allowed");
            return;
        }
    
        // 监视所给出的键
        for (j = 1; j < c->argc; j++)
            watchForKey(c,c->argv[j]);
        addReply(c,shared.ok);
    }
    
    // 监视键值函数
    /* Watch for the specified key */
    void watchForKey(redisClient *c, robj *key) {
        list *clients = NULL;
        listIter li;
        listNode *ln;
        watchedKey *wk;
    
        // 是否已经监视该键值
        /* Check if we are already watching for this key */
        listRewind(c->watched_keys,&li);
        while((ln = listNext(&li))) {
            wk = listNodeValue(ln);
            if (wk->db == c->db && equalStringObjects(key,wk->key))
                return; /* Key already watched */
        }
    
        // 获取监视该键值的客户端链表
        /* This key is not already watched in this DB. Let's add it */
        clients = dictFetchValue(c->db->watched_keys,key);
        // 如果不存在链表，需要新建一个
        if (!clients) {
            clients = listCreate();
            dictAdd(c->db->watched_keys,key,clients);
            incrRefCount(key);
        }
    
        // 尾插法。将客户端添加到链表尾部
        listAddNodeTail(clients,c);
    
        // 将监视键添加到 redisClient.watched_keys 的尾部
        /* Add the new key to the list of keys watched by this client */
        wk = zmalloc(sizeof(*wk));
        wk->key = key;
        wk->db = c->db;
        incrRefCount(key);
        listAddNodeTail(c->watched_keys,wk);
    }


当客户端键值的键值被修改的时候，监视该键值的所有客户端都会被标记为 REDIS_DIRTY_CAS，表示此该键值对被修改过。

touchWatchedKey() 是标记某键值被修改的函数，它一般不被 signalModifyKey() 函数包装。下面是 touchWatchedKey() 的实现。

    
    // 标记键值键值对的客户端为 REDIS_DIRTY_CAS，表示其所监视的数据已经被修改过
    /* "Touch" a key, so that if this key is being WATCHed by some client the
    * next EXEC will fail. */
    void touchWatchedKey(redisDb *db, robj *key) {
        list *clients;
        listIter li;
        listNode *ln;
    
        // 获取监视 key 的所有客户端
        if (dictSize(db->watched_keys) == 0) return;
        clients = dictFetchValue(db->watched_keys, key);
        if (!clients) return;
    
        // 标记监视 key 的所有客户端 REDIS_DIRTY_CAS
        /* Mark all the clients watching this key as REDIS_DIRTY_CAS */
        /* Check if we are already watching for this key */
        listRewind(clients,&li);
        while((ln = listNext(&li))) {
            redisClient *c = listNodeValue(ln);
    
            // REDIS_DIRTY_CAS 更改的时候会设置此标记
            c->flags |= REDIS_DIRTY_CAS;
        }
    }




### redis 事务的执行与取消


当用户发出 EXEC 的时候，在它 MULTI 命令之后提交的所有命令都会被执行。从代码的实现来看，如果客户端监视的数据被修改，它会被标记 REDIS_DIRTY_CAS，会调用 discardTransaction() 从而取消该事务。特别的，用户开启一个事务后会提交多个命令，如果命令在入队过程中出现错误，譬如提交的命令本身不存在，参数错误和内存超额等，都会导致客户端被标记 REDIS_DIRTY_EXEC，被标记 REDIS_DIRTY_EXEC 会导致事务被取消。

因此总结一下：



	
  * REDIS_DIRTY_CAS 更改的时候会设置此标记

	
  * REDIS_DIRTY_EXEC 命令入队时出现错误，此标记会导致 EXEC 命令执行失败


下面是执行事务的过程：

    
    // 执行事务内的所有命令
    void execCommand(redisClient *c) {
        int j;
        robj **orig_argv;
        int orig_argc;
        struct redisCommand *orig_cmd;
        int must_propagate = 0; /* Need to propagate MULTI/EXEC to AOF / slaves? */
    
        // 必须设置多命令标记
        if (!(c->flags & REDIS_MULTI)) {
            addReplyError(c,"EXEC without MULTI");
            return;
        }
    
        // 停止执行事务命令的情况：
        // 1. 被监视的数据被修改
        // 2. 命令队列中的命令执行失败
        /* Check if we need to abort the EXEC because:
         * 1) Some WATCHed key was touched.
         * 2) There was a previous error while queueing commands.
         * A failed EXEC in the first case returns a multi bulk nil object
         * (technically it is not an error but a special behavior), while
         * in the second an EXECABORT error is returned. */
        if (c->flags & (REDIS_DIRTY_CAS|REDIS_DIRTY_EXEC)) {
            addReply(c, c->flags & REDIS_DIRTY_EXEC ? shared.execaborterr :
                                                      shared.nullmultibulk);
            discardTransaction(c);
            goto handle_monitor;
        }
    
        // 执行队列中的所有命令
        /* Exec all the queued commands */
        unwatchAllKeys(c); /* Unwatch ASAP otherwise we'll waste CPU cycles */
    
        // 保存当前的命令，一般为 MULTI，在执行完所有的命令后会恢复。
        orig_argv = c->argv;
        orig_argc = c->argc;
        orig_cmd = c->cmd;
    
        addReplyMultiBulkLen(c,c->mstate.count);
    
        for (j = 0; j < c->mstate.count; j++) {
            // 命令队列中的命令被赋值给当前的命令
            c->argc = c->mstate.commands[j].argc;
            c->argv = c->mstate.commands[j].argv;
            c->cmd = c->mstate.commands[j].cmd;
    
            // 遇到包含写操作的命令需要将 MULTI 命令写入 AOF 文件
            /* Propagate a MULTI request once we encounter the first write op.
             * This way we'll deliver the MULTI/..../EXEC block as a whole and
             * both the AOF and the replication link will have the same consistency
             * and atomicity guarantees. */
            if (!must_propagate && !(c->cmd->flags & REDIS_CMD_READONLY)) {
                execCommandPropagateMulti(c);
                must_propagate = 1;
            }
    
            // 调用 call() 执行
            call(c,REDIS_CALL_FULL);
    
            // 这几句是多余的
            /* Commands may alter argc/argv, restore mstate. */
            c->mstate.commands[j].argc = c->argc;
            c->mstate.commands[j].argv = c->argv;
            c->mstate.commands[j].cmd = c->cmd;
        }
    
        // 恢复当前的命令，一般为 MULTI
        c->argv = orig_argv;
        c->argc = orig_argc;
        c->cmd = orig_cmd;
    
        // 事务已经执行完毕，清理与此事务相关的信息，如命令队列和客户端标记
        discardTransaction(c);
        /* Make sure the EXEC command will be propagated as well if MULTI
         * was already propagated. */
        if (must_propagate) server.dirty++;
    
        ......
    }


如上所说，被监视的键值被修改或者命令入队出错都会导致事务被取消：

    
    // 取消事务
    void discardTransaction(redisClient *c) {
        // 清空命令队列
        freeClientMultiState(c);
    
        // 初始化命令队列
        initClientMultiState(c);
    
        // 取消标记 flag
        c->flags &= ~(REDIS_MULTI|REDIS_DIRTY_CAS|REDIS_DIRTY_EXEC);;
        unwatchAllKeys(c);
    }




捣乱 2014-6-28

[http://daoluan.net](http://daoluan.net/)
