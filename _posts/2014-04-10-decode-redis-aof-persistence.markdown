---
author: daoluan
comments: true
date: 2014-04-10 05:30:15+00:00
layout: post
slug: decode-redis-aof-persistence
title: 深入剖析 redis AOF 持久化策略
wordpress_id: 2308
categories:
- linux
- 学习总结
- 网络编程
tags:
- aof
- redis
- 持久化
- 源码剖析
---

本篇主要讲的是 AOF 持久化，了解 AOF 的数据组织方式和运作机制。redis 主要在 aof.c 中实现 AOF 的操作。


### 数据结构 rio


redis AOF 持久化同样借助了 struct rio. 详细内容在《深入剖析 redis RDB 持久化策略》中有介绍。


### AOF 数据组织方式


假设 redis 内存有「name:Jhon」的键值对，那么进行 AOF 持久化后，AOF 文件有如下内容：

    
    *2     # 2个参数
    $6     # 第一个参数长度为 6
    SELECT     # 第一个参数
    $1     # 第二参数长度为 1
    8     # 第二参数
    *3     # 3个参数
    $3     # 第一个参数长度为 4
    SET     # 第一个参数
    $4     # 第二参数长度为 4
    name     # 第二个参数
    $4     # 第三个参数长度为 4
    Jhon     # 第二参数长度为 4


所以对上面的内容进行恢复，能得到熟悉的一条 redis 命令：SELECT 8;SET name Jhon.
可以想象的是，redis 遍历内存数据集中的每个 key-value 对，依次写入磁盘中；redis 启动的时候，从 AOF 文件中读取数据，恢复数据。


### AOF 持久化运作机制


和 redis RDB 持久化运作机制不同，redis AOF 有后台执行和边服务边备份两种方式。

[![aof_persistence](http://md.daoluan.net/images/blog/2014/04/aof_persistence.png)](http://md.daoluan.net/images/blog/2014/04/aof_persistence.png)

1）AOF 后台执行的方式和 RDB 有类似的地方，fork 一个子进程，主进程仍进行服务，子进程执行 AOF 持久化，数据被 dump 到磁盘上。与 RDB 不同的是，后台子进程持久化过程中，主进程会记录期间的所有数据变更（主进程还在服务），并存储在 server.aof_rewrite_buf_blocks 中；后台子进程结束后，redis 更新缓存追加到 AOF 文件中，是 RDB 持久化所不具备的。

来说说更新缓存这个东西。redis 服务器产生数据变更的时候，譬如 set name Jhon，不仅仅会修改内存数据集，也会记录此更新（修改）操作，记录的方式就是上面所说的数据组织方式。

更新缓存可以存储在 server.aof_buf 中，你可以把它理解为一个小型临时中转站，所有累积的更新缓存都会先放入这里，它会在特定时机写入文件或者插入到 server.aof_rewrite_buf_blocks 下链表（下面会详述）；server.aof_buf 中的数据在 propagrate() 添加，在涉及数据更新的地方都会调用 propagrate() 以累积变更。更新缓存也可以存储在 server.aof_rewrite_buf_blocks，这是一个元素类型为 struct aofrwblock 的链表，你可以把它理解为一个仓库，当后台有 AOF 子进程的时候，会将累积的更新缓存（在 server.aof_buf 中）插入到链表中，而当 AOF 子进程结束，它会被整个写入到文件。两者是有关联的。

下面是后台执行的主要代码：

    
    // 启动后台子进程，执行 AOF 持久化操作。bgrewriteaofCommand()，startAppendOnly()，serverCron() 中会调用此函数
    /* This is how rewriting of the append only file in background works:
    *
    * 1) The user calls BGREWRITEAOF
    * 2) Redis calls this function, that forks():
    *    2a) the child rewrite the append only file in a temp file.
    *    2b) the parent accumulates differences in server.aof_rewrite_buf.
    * 3) When the child finished '2a' exists.
    * 4) The parent will trap the exit code, if it's OK, will append the
    *    data accumulated into server.aof_rewrite_buf into the temp file, and
    *    finally will rename(2) the temp file in the actual file name.
    *    The the new file is reopened as the new append only file. Profit!
    */
    int rewriteAppendOnlyFileBackground(void) {
        pid_t childpid;
        long long start;
    
        // 已经有正在执行备份的子进程
        if (server.aof_child_pid != -1) return REDIS_ERR;
    
        start = ustime();
        if ((childpid = fork()) == 0) {
            char tmpfile[256];
    
            // 子进程
            /* Child */
    
            // 关闭监听
            closeListeningSockets(0);
    
            // 设置进程 title
            redisSetProcTitle("redis-aof-rewrite");
    
            // 临时文件名
            snprintf(tmpfile,256,"temp-rewriteaof-bg-%d.aof", (int) getpid());
    
            // 脏数据，其实就是子进程所消耗的内存大小
            if (rewriteAppendOnlyFile(tmpfile) == REDIS_OK) {
                // 获取脏数据大小
                size_t private_dirty = zmalloc_get_private_dirty();
    
                // 记录脏数据
                if (private_dirty) {
                    redisLog(REDIS_NOTICE,
                        "AOF rewrite: %zu MB of memory used by copy-on-write",
                        private_dirty/(1024*1024));
                }
                exitFromChild(0);
            } else {
                exitFromChild(1);
            }
        } else {
            /* Parent */
            server.stat_fork_time = ustime()-start;
            if (childpid == -1) {
                redisLog(REDIS_WARNING,
                    "Can't rewrite append only file in background: fork: %s",
                    strerror(errno));
                return REDIS_ERR;
            }
            redisLog(REDIS_NOTICE,
                "Background append only file rewriting started by pid %d",childpid);
            // AOF 已经开始执行，取消 AOF 计划
            server.aof_rewrite_scheduled = 0;
    
            // AOF 最近一次执行的起始时间
            server.aof_rewrite_time_start = time(NULL);
    
            // 子进程 ID
            server.aof_child_pid = childpid;
            updateDictResizePolicy();
    
            // 因为更新缓存都将写入文件，要强制产生选择数据集的指令 SELECT ，以防出现数据合并错误。
            /* We set appendseldb to -1 in order to force the next call to the
             * feedAppendOnlyFile() to issue a SELECT command, so the differences
             * accumulated by the parent into server.aof_rewrite_buf will start
             * with a SELECT statement and it will be safe to merge. */
            server.aof_selected_db = -1;
    
            replicationScriptCacheFlush();
            return REDIS_OK;
        }
        return REDIS_OK; /* unreached */
    }
    
    // AOF 持久化主函数。只在 rewriteAppendOnlyFileBackground() 中会调用此函数
    /* Write a sequence of commands able to fully rebuild the dataset into
    * "filename". Used both by REWRITEAOF and BGREWRITEAOF.
    *
    * In order to minimize the number of commands needed in the rewritten
    * log Redis uses variadic commands when possible, such as RPUSH, SADD
    * and ZADD. However at max REDIS_AOF_REWRITE_ITEMS_PER_CMD items per time
    * are inserted using a single command. */
    int rewriteAppendOnlyFile(char *filename) {
        dictIterator *di = NULL;
        dictEntry *de;
        rio aof;
        FILE *fp;
        char tmpfile[256];
        int j;
        long long now = mstime();
    
        /* Note that we have to use a different temp name here compared to the
         * one used by rewriteAppendOnlyFileBackground() function. */
        snprintf(tmpfile,256,"temp-rewriteaof-%d.aof", (int) getpid());
    
        // 打开文件
        fp = fopen(tmpfile,"w");
        if (!fp) {
            redisLog(REDIS_WARNING, "Opening the temp file for AOF rewrite in rewriteAppendOnlyFile(): %s", strerror(errno));
            return REDIS_ERR;
        }
    
        // 初始化 rio 结构体
        rioInitWithFile(&aof,fp);
    
        // 如果设置了自动备份参数，将进行设置
        if (server.aof_rewrite_incremental_fsync)
            rioSetAutoSync(&aof,REDIS_AOF_AUTOSYNC_BYTES);
    
        // 备份每一个数据集
        for (j = 0; j < server.dbnum; j++) {
            char selectcmd[] = "*2\r\n$6\r\nSELECT\r\n";
            redisDb *db = server.db+j;
            dict *d = db->dict;
            if (dictSize(d) == 0) continue;
    
            // 获取数据集的迭代器
            di = dictGetSafeIterator(d);
            if (!di) {
                fclose(fp);
                return REDIS_ERR;
            }
    
            // 写入 AOF 操作码
            /* SELECT the new DB */
            if (rioWrite(&aof,selectcmd,sizeof(selectcmd)-1) == 0) goto werr;
    
            // 写入数据集序号
            if (rioWriteBulkLongLong(&aof,j) == 0) goto werr;
    
            // 写入数据集中每一个数据项
            /* Iterate this DB writing every entry */
            while((de = dictNext(di)) != NULL) {
                sds keystr;
                robj key, *o;
                long long expiretime;
    
                keystr = dictGetKey(de);
                o = dictGetVal(de);
    
                // 将 keystr 封装在 robj 里
                initStaticStringObject(key,keystr);
    
                // 获取过期时间
                expiretime = getExpire(db,&key);
    
                // 如果已经过期，放弃存储
                /* If this key is already expired skip it */
                if (expiretime != -1 && expiretime < now) continue;
    
                // 写入键值对应的写操作
                /* Save the key and associated value */
                if (o->type == REDIS_STRING) {
                    /* Emit a SET command */
                    char cmd[]="*3\r\n$3\r\nSET\r\n";
                    if (rioWrite(&aof,cmd,sizeof(cmd)-1) == 0) goto werr;
                    /* Key and value */
                    if (rioWriteBulkObject(&aof,&key) == 0) goto werr;
                    if (rioWriteBulkObject(&aof,o) == 0) goto werr;
                } else if (o->type == REDIS_LIST) {
                    if (rewriteListObject(&aof,&key,o) == 0) goto werr;
                } else if (o->type == REDIS_SET) {
                    if (rewriteSetObject(&aof,&key,o) == 0) goto werr;
                } else if (o->type == REDIS_ZSET) {
                    if (rewriteSortedSetObject(&aof,&key,o) == 0) goto werr;
                } else if (o->type == REDIS_HASH) {
                    if (rewriteHashObject(&aof,&key,o) == 0) goto werr;
                } else {
                    redisPanic("Unknown object type");
                }
    
                // 写入过期时间
                /* Save the expire time */
                if (expiretime != -1) {
                    char cmd[]="*3\r\n$9\r\nPEXPIREAT\r\n";
                    if (rioWrite(&aof,cmd,sizeof(cmd)-1) == 0) goto werr;
                    if (rioWriteBulkObject(&aof,&key) == 0) goto werr;
                    if (rioWriteBulkLongLong(&aof,expiretime) == 0) goto werr;
                }
            }
    
            // 释放迭代器
            dictReleaseIterator(di);
        }
    
        // 写入磁盘
        /* Make sure data will not remain on the OS's output buffers */
        fflush(fp);
        aof_fsync(fileno(fp));
        fclose(fp);
    
        // 重写文件名
        /* Use RENAME to make sure the DB file is changed atomically only
         * if the generate DB file is ok. */
        if (rename(tmpfile,filename) == -1) {
            redisLog(REDIS_WARNING,"Error moving temp append only file on the final destination: %s", strerror(errno));
            unlink(tmpfile);
            return REDIS_ERR;
        }
        redisLog(REDIS_NOTICE,"SYNC append only file rewrite performed");
        return REDIS_OK;
    
    werr:
        // 清理工作
        fclose(fp);
        unlink(tmpfile);
        redisLog(REDIS_WARNING,"Write error writing append only file on disk: %s", strerror(errno));
        if (di) dictReleaseIterator(di);
        return REDIS_ERR;
    }
    
    // 后台子进程结束后，redis 更新缓存 server.aof_rewrite_buf_blocks 追加到 AOF 文件中
    // 在 AOF 持久化结束后会执行这个函数， backgroundRewriteDoneHandler() 主要工作是将 server.aof_rewrite_buf_blocks，即 AOF 缓存写入文件
    /* A background append only file rewriting (BGREWRITEAOF) terminated its work.
     * Handle this. */
    void backgroundRewriteDoneHandler(int exitcode, int bysignal) {
            ......
            // 将 AOF 缓存 server.aof_rewrite_buf_blocks 的 AOF 写入磁盘
            if (aofRewriteBufferWrite(newfd) == -1) {
                redisLog(REDIS_WARNING,
                    "Error trying to flush the parent diff to the rewritten AOF: %s", strerror(errno));
                close(newfd);
                goto cleanup;
            }
            ......
    }
    
    // 将累积的更新缓存 server.aof_rewrite_buf_blocks 同步到磁盘
    /* Write the buffer (possibly composed of multiple blocks) into the specified
    * fd. If no short write or any other error happens -1 is returned,
    * otherwise the number of bytes written is returned. */
    ssize_t aofRewriteBufferWrite(int fd) {
        listNode *ln;
        listIter li;
        ssize_t count = 0;
    
        listRewind(server.aof_rewrite_buf_blocks,&li);
        while((ln = listNext(&li))) {
            aofrwblock *block = listNodeValue(ln);
            ssize_t nwritten;
    
            if (block->used) {
                nwritten = write(fd,block->buf,block->used);
                if (nwritten != block->used) {
                    if (nwritten == 0) errno = EIO;
                    return -1;
                }
                count += nwritten;
            }
        }
        return count;
    }


2）边服务边备份的方式，即 redis 服务器会把所有的数据变更存储在 server.aof_buf 中，并在特定时机将更新缓存写入预设定的文件（server.aof_filename）。特定时机有三种：



	
  1. 进入事件循环之前

	
  2. redis 服务器定时程序 serverCron() 中

	
  3. 停止 AOF 策略的 stopAppendOnly() 中


redis 无非是不想服务器突然崩溃终止，导致过多的数据丢失。redis 默认是每两秒钟进行一次边服务边备份，即隔两秒将累积的写入文件。

**redis 为什么取消直接在本进程进行 AOF 持久化的方法？**原因可能是产生一个 AOF 文件要比 RDB 文件消耗更多的时间；如果在当前进程执行 AOF 持久化，会占用服务进程（主进程）较多的时间，停止服务的时间也更长（？）

下面是边服务边备份的主要代码：

    
    // 同步磁盘；将所有累积的更新 server.aof_buf 写入磁盘
    /* Write the append only file buffer on disk.
    *
    * Since we are required to write the AOF before replying to the client,
    * and the only way the client socket can get a write is entering when the
    * the event loop, we accumulate all the AOF writes in a memory
    * buffer and write it on disk using this function just before entering
    * the event loop again.
    *
    * About the 'force' argument:
    *
    * When the fsync policy is set to 'everysec' we may delay the flush if there
    * is still an fsync() going on in the background thread, since for instance
    * on Linux write(2) will be blocked by the background fsync anyway.
    * When this happens we remember that there is some aof buffer to be
    * flushed ASAP, and will try to do that in the serverCron() function.
    *
    * However if force is set to 1 we'll write regardless of the background
    * fsync. */
    void flushAppendOnlyFile(int force) {
        ssize_t nwritten;
        int sync_in_progress = 0;
    
        // 无数据，无需同步到磁盘
        if (sdslen(server.aof_buf) == 0) return;
    
        // 创建线程任务，主要调用 fsync()
        if (server.aof_fsync == AOF_FSYNC_EVERYSEC)
            sync_in_progress = bioPendingJobsOfType(REDIS_BIO_AOF_FSYNC) != 0;
    
        // 如果没有设置强制同步的选项，可能不会立即进行同步
        if (server.aof_fsync == AOF_FSYNC_EVERYSEC && !force) {
            // 推迟执行 AOF
            /* With this append fsync policy we do background fsyncing.
             * If the fsync is still in progress we can try to delay
             * the write for a couple of seconds. */
            if (sync_in_progress) {
                if (server.aof_flush_postponed_start == 0) {
                    // 设置延迟冲洗时间选项
                    /* No previous write postponinig, remember that we are
                     * postponing the flush and return. */
                    server.aof_flush_postponed_start = server.unixtime; // /* Unix time sampled every cron cycle. */
                    return;
    
                // 没有超过 2s，直接结束
                } else if (server.unixtime - server.aof_flush_postponed_start < 2) {
                    /* We were already waiting for fsync to finish, but for less
                     * than two seconds this is still ok. Postpone again. */
                    return;
                }
    
                // 否则，要强制写入磁盘
                /* Otherwise fall trough, and go write since we can't wait
                 * over two seconds. */
                server.aof_delayed_fsync++;
                redisLog(REDIS_NOTICE,"Asynchronous AOF fsync is taking too long (disk is busy?). Writing the AOF buffer without waiting for fsync to complete, this may slow down Redis.");
            }
        }
    
        // 取消延迟冲洗时间设置
        /* If you are following this code path, then we are going to write so
         * set reset the postponed flush sentinel to zero. */
        server.aof_flush_postponed_start = 0;
    
        /* We want to perform a single write. This should be guaranteed atomic
         * at least if the filesystem we are writing is a real physical one.
         * While this will save us against the server being killed I don't think
         * there is much to do about the whole server stopping for power problems
         * or alike */
        // AOF 文件已经打开了。将 server.aof_buf 中的所有缓存数据写入文件
        nwritten = write(server.aof_fd,server.aof_buf,sdslen(server.aof_buf));
    
        if (nwritten != (signed)sdslen(server.aof_buf)) {
            /* Ooops, we are in troubles. The best thing to do for now is
             * aborting instead of giving the illusion that everything is
             * working as expected. */
            if (nwritten == -1) {
                redisLog(REDIS_WARNING,"Exiting on error writing to the append-only file: %s",strerror(errno));
            } else {
                redisLog(REDIS_WARNING,"Exiting on short write while writing to "
                                       "the append-only file: %s (nwritten=%ld, "
                                       "expected=%ld)",
                                       strerror(errno),
                                       (long)nwritten,
                                       (long)sdslen(server.aof_buf));
    
                if (ftruncate(server.aof_fd, server.aof_current_size) == -1) {
                    redisLog(REDIS_WARNING, "Could not remove short write "
                             "from the append-only file.  Redis may refuse "
                             "to load the AOF the next time it starts.  "
                             "ftruncate: %s", strerror(errno));
                }
            }
            exit(1);
        }
    
        // 更新 AOF 文件的大小
        server.aof_current_size += nwritten;
    
        /*当 server.aof_buf 足够小,重新利用空间，防止频繁的内存分配。
        相反，当 server.aof_buf 占据大量的空间，采取的策略是释放空间，可见 redis 对内存很敏感。*/
        /* Re-use AOF buffer when it is small enough. The maximum comes from the
         * arena size of 4k minus some overhead (but is otherwise arbitrary). */
        if ((sdslen(server.aof_buf)+sdsavail(server.aof_buf)) < 4000) {
            sdsclear(server.aof_buf);
        } else {
            sdsfree(server.aof_buf);
            server.aof_buf = sdsempty();
        }
    
        /* Don't fsync if no-appendfsync-on-rewrite is set to yes and there are
         * children doing I/O in the background. */
        if (server.aof_no_fsync_on_rewrite &&
            (server.aof_child_pid != -1 || server.rdb_child_pid != -1))
                return;
    
        // sync,写入磁盘
        /* Perform the fsync if needed. */
        if (server.aof_fsync == AOF_FSYNC_ALWAYS) {
            /* aof_fsync is defined as fdatasync() for Linux in order to avoid
             * flushing metadata. */
            aof_fsync(server.aof_fd); /* Let's try to get this data on the disk */
            server.aof_last_fsync = server.unixtime;
        } else if ((server.aof_fsync == AOF_FSYNC_EVERYSEC &&
                    server.unixtime > server.aof_last_fsync)) {
            if (!sync_in_progress) aof_background_fsync(server.aof_fd);
            server.aof_last_fsync = server.unixtime;
        }
    }




### 细说更新缓存


上面两次提到了「更新缓存」，它即是 redis 累积的数据变更。

更新缓存可以存储在 server.aof_buf 中，可以存储在 server.server.aof_rewrite_buf_blocks 连表中。他们的关系是：每一次数据变更记录都会写入 server.aof_buf 中，同时如果后台子进程在持久化，变更记录还会被写入 server.server.aof_rewrite_buf_blocks 中。server.aof_buf 会在特定时期写入指定文件，server.server.aof_rewrite_buf_blocks 会在后台持久化结束后追加到文件。

redis 源码中是这么实现的：propagrate()->feedAppendOnlyFile()->aofRewriteBufferAppend()

注释：feedAppendOnlyFile() 会把更新添加到 server.aof_buf；接下来会有一个判断，如果存在 AOF 子进程，则调用 aofRewriteBufferAppend() 将 server.aof_buf 中的所有数据插入到 server.aof_rewrite_buf_blocks 链表。

一副可以缓解视力疲劳的图片——AOF 持久化运作机制：

[![how_aof_works](http://md.daoluan.net/images/blog/2014/04/how_aof_works.png)](http://md.daoluan.net/images/blog/2014/04/how_aof_works.png)

下面是主要的代码：

    
    // 向 AOF 和从机发布数据更新
    /* Propagate the specified command (in the context of the specified database id)
    * to AOF and Slaves.
    *
    * flags are an xor between:
    * + REDIS_PROPAGATE_NONE (no propagation of command at all)
    * + REDIS_PROPAGATE_AOF (propagate into the AOF file if is enabled)
    * + REDIS_PROPAGATE_REPL (propagate into the replication link)
    */
    void propagate(struct redisCommand *cmd, int dbid, robj **argv, int argc,
                   int flags)
    {
        // AOF 策略需要打开，且设置 AOF 传播标记，将更新发布给本地文件
        if (server.aof_state != REDIS_AOF_OFF && flags & REDIS_PROPAGATE_AOF)
            feedAppendOnlyFile(cmd,dbid,argv,argc);
    
        // 设置了从机传播标记，将更新发布给从机
        if (flags & REDIS_PROPAGATE_REPL)
            replicationFeedSlaves(server.slaves,dbid,argv,argc);
    }
    
    // 将数据更新记录到 AOF 缓存中
    void feedAppendOnlyFile(struct redisCommand *cmd, int dictid, robj **argv, int argc) {
        sds buf = sdsempty();
        robj *tmpargv[3];
    
        /* The DB this command was targeting is not the same as the last command
         * we appendend. To issue a SELECT command is needed. */
        if (dictid != server.aof_selected_db) {
            char seldb[64];
    
            snprintf(seldb,sizeof(seldb),"%d",dictid);
            buf = sdscatprintf(buf,"*2\r\n$6\r\nSELECT\r\n$%lu\r\n%s\r\n",
                (unsigned long)strlen(seldb),seldb);
            server.aof_selected_db = dictid;
        }
    
        if (cmd->proc == expireCommand || cmd->proc == pexpireCommand ||
            cmd->proc == expireatCommand) {
            /* Translate EXPIRE/PEXPIRE/EXPIREAT into PEXPIREAT */
            buf = catAppendOnlyExpireAtCommand(buf,cmd,argv[1],argv[2]);
        } else if (cmd->proc == setexCommand || cmd->proc == psetexCommand) {
            /* Translate SETEX/PSETEX to SET and PEXPIREAT */
            tmpargv[0] = createStringObject("SET",3);
            tmpargv[1] = argv[1];
            tmpargv[2] = argv[3];
            buf = catAppendOnlyGenericCommand(buf,3,tmpargv);
            decrRefCount(tmpargv[0]);
            buf = catAppendOnlyExpireAtCommand(buf,cmd,argv[1],argv[2]);
        } else {
            /* All the other commands don't need translation or need the
             * same translation already operated in the command vector
             * for the replication itself. */
            buf = catAppendOnlyGenericCommand(buf,argc,argv);
        }
    
        // 将生成的 AOF 追加到 server.aof_buf 中。server.在下一次进入事件循环之前，aof_buf 中的内容将会写到磁盘上
        /* Append to the AOF buffer. This will be flushed on disk just before
         * of re-entering the event loop, so before the client will get a
         * positive reply about the operation performed. */
        if (server.aof_state == REDIS_AOF_ON)
            server.aof_buf = sdscatlen(server.aof_buf,buf,sdslen(buf));
    
        // 如果已经有 AOF 子进程运行，redis 采取的策略是累积子进程 AOF 备份的数据和内存中数据集的差异。 aofRewriteBufferAppend() 把 buf 的内容追加到 server.aof_rewrite_buf_blocks 数组中
        /* If a background append only file rewriting is in progress we want to
         * accumulate the differences between the child DB and the current one
         * in a buffer, so that when the child process will do its work we
         * can append the differences to the new append only file. */
        if (server.aof_child_pid != -1)
            aofRewriteBufferAppend((unsigned char*)buf,sdslen(buf));
    
        sdsfree(buf);
    }
    
    // 将数据更新记录写入 server.aof_rewrite_buf_blocks，此函数只由 feedAppendOnlyFile() 调用
    /* Append data to the AOF rewrite buffer, allocating new blocks if needed. */
    void aofRewriteBufferAppend(unsigned char *s, unsigned long len) {
        // 尾插法
        listNode *ln = listLast(server.aof_rewrite_buf_blocks);
        aofrwblock *block = ln ? ln->value : NULL;
    
        while(len) {
            /* If we already got at least an allocated block, try appending
             * at least some piece into it. */
            if (block) {
                unsigned long thislen = (block->free < len) ? block->free : len;
                if (thislen) {  /* The current block is not already full. */
                    memcpy(block->buf+block->used, s, thislen);
                    block->used += thislen;
                    block->free -= thislen;
                    s += thislen;
                    len -= thislen;
                }
            }
    
            if (len) { /* First block to allocate, or need another block. */
                int numblocks;
    
                // 创建新的节点，插到尾部
                block = zmalloc(sizeof(*block));
                block->free = AOF_RW_BUF_BLOCK_SIZE;
                block->used = 0;
    
                // 尾插法
                listAddNodeTail(server.aof_rewrite_buf_blocks,block);
    
                /* Log every time we cross more 10 or 100 blocks, respectively
                 * as a notice or warning. */
                numblocks = listLength(server.aof_rewrite_buf_blocks);
                if (((numblocks+1) % 10) == 0) {
                    int level = ((numblocks+1) % 100) == 0 ? REDIS_WARNING :
                                                             REDIS_NOTICE;
                    redisLog(level,"Background AOF buffer size: %lu MB",
                        aofRewriteBufferSize()/(1024*1024));
                }
            }
        }
    }


两种数据落地的方式，就是 AOF 的两个主线。因此，redis AOF 持久化机制有两条主线：后台执行和边服务边备份，抓住这两点就能理解 redis AOF 了。

这里有一个疑问，**两条主线都会涉及文件的写：后台执行会写一个 AOF 文件，边服务边备份也会写一个，以哪个为准？**

后台持久化的数据首先会被写入「temp-rewriteaof-bg-%d.aof」，其中「%d」是 AOF 子进程 id；待 AOF 子进程结束后，「temp-rewriteaof-bg-%d.aof」会被以追加的方式打开，继而写入 server.aof_rewrite_buf_blocks 中的更新缓存，最后「temp-rewriteaof-bg-%d.aof」文件被命名为 server.aof_filename，所以之前的名为 server.aof_filename 的文件会被删除，也就是说边服务边备份写入的文件会被删除。边服务边备份的数据会被一直写入到 server.aof_filename 文件中。

因此，确实会产生两个文件，但是最后都会变成 server.aof_filename 文件。

这里还有一个疑问，既然有了后台持久化，为什么还要边服务边备份？边服务边备份时间长了会产生数据冗余甚至备份过旧的数据，而后台持久化可以消除这些东西。看，这里是 redis 的双保险。


### AOF 恢复过程


AOF 的数据恢复过程设计实在是棒极了，它模拟一个服务过程。redis 首先虚拟一个客户端，读取 AOF 文件恢复 redis 命令和参数；然后就像服务客户端一样执行命令相应的函数，从而恢复数据。这些过程主要在loadAppendOnlyFile() 中实现。

    
    // 加载 AOF 文件，恢复数据
    /* Replay the append log file. On error REDIS_OK is returned. On non fatal
    * error (the append only file is zero-length) REDIS_ERR is returned. On
    * fatal error an error message is logged and the program exists. */
    int loadAppendOnlyFile(char *filename) {
        struct redisClient *fakeClient;
        FILE *fp = fopen(filename,"r");
        struct redis_stat sb;
        int old_aof_state = server.aof_state;
        long loops = 0;
    
        // 文件大小不能为 0
        if (fp && redis_fstat(fileno(fp),&sb) != -1 && sb.st_size == 0) {
            server.aof_current_size = 0;
            fclose(fp);
            return REDIS_ERR;
        }
    
        if (fp == NULL) {
            redisLog(REDIS_WARNING,"Fatal error: can't open the append log file for reading: %s",strerror(errno));
            exit(1);
        }
    
        // 正在执行 AOF 加载操作，于是暂时禁止 AOF 的所有操作，以免混淆
        /* Temporarily disable AOF, to prevent EXEC from feeding a MULTI
         * to the same file we're about to read. */
        server.aof_state = REDIS_AOF_OFF;
    
        // 虚拟出一个客户端，即 redisClient
        fakeClient = createFakeClient();
        startLoading(fp);
    
        while(1) {
            int argc, j;
            unsigned long len;
            robj **argv;
            char buf[128];
            sds argsds;
            struct redisCommand *cmd;
    
            // 每循环 1000 次，在恢复数据的同时，服务器也为客户端服务。aeProcessEvents() 会进入事件循环
            /* Serve the clients from time to time */
            if (!(loops++ % 1000)) {
                loadingProgress(ftello(fp));
                aeProcessEvents(server.el, AE_FILE_EVENTS|AE_DONT_WAIT);
            }
    
            // 可能 aof 文件到了结尾
            if (fgets(buf,sizeof(buf),fp) == NULL) {
                if (feof(fp))
                    break;
                else
                    goto readerr;
            }
    
            // 必须以“*”开头，格式不对，退出
            if (buf[0] != '*') goto fmterr;
    
            // 参数的个数
            argc = atoi(buf+1);
    
            // 参数个数错误
            if (argc < 1) goto fmterr;
    
            // 为参数分配空间
            argv = zmalloc(sizeof(robj*)*argc);
    
            // 依次读取参数
            for (j = 0; j < argc; j++) {
                if (fgets(buf,sizeof(buf),fp) == NULL) goto readerr;
                if (buf[0] != '$') goto fmterr;
                len = strtol(buf+1,NULL,10);
                argsds = sdsnewlen(NULL,len);
                if (len && fread(argsds,len,1,fp) == 0) goto fmterr;
                argv[j] = createObject(REDIS_STRING,argsds);
                if (fread(buf,2,1,fp) == 0) goto fmterr; /* discard CRLF */
            }
    
            // 找到相应的命令
            /* Command lookup */
            cmd = lookupCommand(argv[0]->ptr);
            if (!cmd) {
                redisLog(REDIS_WARNING,"Unknown command '%s' reading the append only file", (char*)argv[0]->ptr);
                exit(1);
            }
    
            // 执行命令，模拟服务客户端请求的过程，从而写入数据
            /* Run the command in the context of a fake client */
            fakeClient->argc = argc;
            fakeClient->argv = argv;
            cmd->proc(fakeClient);
    
            /* The fake client should not have a reply */
            redisAssert(fakeClient->bufpos == 0 && listLength(fakeClient->reply) == 0);
            /* The fake client should never get blocked */
            redisAssert((fakeClient->flags & REDIS_BLOCKED) == 0);
    
            // 释放虚拟客户端空间
            /* Clean up. Command code may have changed argv/argc so we use the
             * argv/argc of the client instead of the local variables. */
            for (j = 0; j < fakeClient->argc; j++)
                decrRefCount(fakeClient->argv[j]);
            zfree(fakeClient->argv);
        }
    
        /* This point can only be reached when EOF is reached without errors.
         * If the client is in the middle of a MULTI/EXEC, log error and quit. */
        if (fakeClient->flags & REDIS_MULTI) goto readerr;
    
        // 清理工作
        fclose(fp);
        freeFakeClient(fakeClient);
    
        // 恢复旧的 AOF 状态
        server.aof_state = old_aof_state;
        stopLoading();
    
        // 记录最近 AOF 操作的文件大小
        aofUpdateCurrentSize();
        server.aof_rewrite_base_size = server.aof_current_size;
        return REDIS_OK;
    
    readerr:
        // 错误，清理工作
        if (feof(fp)) {
            redisLog(REDIS_WARNING,"Unexpected end of file reading the append only file");
        } else {
            redisLog(REDIS_WARNING,"Unrecoverable error reading the append only file: %s", strerror(errno));
        }
        exit(1);
    fmterr:
        redisLog(REDIS_WARNING,"Bad file format reading the append only file: make a backup of your AOF file, then use ./redis-check-aof --fix <filename>");
        exit(1);
    }




### AOF 的适用场景


如果对数据比较关心，分秒必争，可以用 AOF 持久化，而且 AOF 文件很容易进行分析。

—-

捣乱 2014-3-26

[http://daoluan.net](http://daoluan.net)
