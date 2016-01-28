---
author: daoluan
comments: true
date: 2014-03-26 04:20:14+00:00
layout: post
slug: decode-redis-rdb-persistence
title: 深入剖析 redis RDB 持久化策略
wordpress_id: 2276
categories:
- linux
- 学习总结
- 网络编程
tags:
- RDB
- redis
- 持久化
- 源码剖析
---

### 简介 redis 持久化 RDB、AOF


redis 提供两种持久化方式：RDB 和 AOF。redis 允许两者结合，也允许两者同时关闭。



	
  * RDB 可以定时备份内存中的数据集。服务器启动的时候，可以从 RDB 文件中回复数据集。

	
  * AOF 可以记录服务器的所有写操作。在服务器重新启动的时候，会把所有的写操作重新执行一遍，从而实现数据备份。当写操作集过大（比原有的数据集还大），redis 会重写写操作集。


本篇主要讲的是 RDB 持久化，了解 RDB 的数据保存结构和运作机制。redis 主要在 rdb.h 和 rdb.c 两个文件中实现 RDB 的操作。


### 数据结构 rio


持久化的 IO 操作在 rio.h 和 rio.c 中实现，核心数据结构是 struct rio。RDB 中的几乎每一个函数都带有 rio 参数。struct rio 既适用于文件，又适用于内存缓存，从 struct rio 的实现可见一斑。

    
    struct _rio {
        // 函数指针，包括读操作，写操作和文件指针移动操作
        /* Backend functions.
         * Since this functions do not tolerate short writes or reads the return
         * value is simplified to: zero on error, non zero on complete success. */
        size_t (*read)(struct _rio *, void *buf, size_t len);
        size_t (*write)(struct _rio *, const void *buf, size_t len);
        off_t (*tell)(struct _rio *);
    
        // 校验和计算函数
        /* The update_cksum method if not NULL is used to compute the checksum of
         * all the data that was read or written so far. The method should be
         * designed so that can be called with the current checksum, and the buf
         * and len fields pointing to the new block of data to add to the checksum
         * computation. */
        void (*update_cksum)(struct _rio *, const void *buf, size_t len);
    
        // 校验和
        /* The current checksum */
        uint64_t cksum;
    
        // 已经读取或者写入的字符数
        /* number of bytes read or written */
        size_t processed_bytes;
    
        // 每次最多能处理的字符数
        /* maximum single read or write chunk size */
        size_t max_processing_chunk;
    
        // 可以是一个内存总的字符串，也可以是一个文件描述符
        /* Backend-specific vars. */
        union {
            struct {
                sds ptr;
                // 偏移量
                off_t pos;
            } buffer;
            struct {
                FILE *fp;
                // 偏移量
                off_t buffered; /* Bytes written since last fsync. */
                off_t autosync; /* fsync after 'autosync' bytes written. */
            } file;
        } io;
    };
    
    typedef struct _rio rio;


redis 定义两个 struct rio，分别是 rioFileIO 和 rioBufferIO，前者用于内存缓存，后者用于文件 IO：

    
    // 适用于内存缓存
    static const rio rioBufferIO = {
        rioBufferRead,
        rioBufferWrite,
        rioBufferTell,
        NULL,           /* update_checksum */
        0,              /* current checksum */
        0,              /* bytes read or written */
        0,              /* read/write chunk size */
        { { NULL, 0 } } /* union for io-specific vars */
    };
    
    // 适用于文件 IO
    static const rio rioFileIO = {
        rioFileRead,
        rioFileWrite,
        rioFileTell,
        NULL,           /* update_checksum */
        0,              /* current checksum */
        0,              /* bytes read or written */
        0,              /* read/write chunk size */
        { { NULL, 0 } } /* union for io-specific vars */
    };




### RDB 持久化的运作机制


[![rdb_persistence](http://md.daoluan.net/blog/images/2014/03/rdb_persistence.png)](http://md.daoluan.net/blog/images/2014/03/rdb_persistence.png)

redis 支持两种方式进行 RDB：当前进程执行和后台执行（BGSAVE）。RDB BGSAVE 策略是 fork 出一个子进程，把内存中的数据集整个 dump 到硬盘上。两个场景举例：



	
  1. redis 服务器初始化过程中，设定了定时事件，每隔一段时间就会触发持久化操作；进入定时事件处理程序中，就会 fork 产生子进程执行持久化操作。

	
  2. redis 服务器预设了 save 指令，客户端可要求服务器进程中断服务，执行持久化操作。


这里主要展开的内容是 RDB 持久化操作的写文件过程，读过程和写过程相反。子进程的产生发生在 rdbSaveBackground() 中，真正的 RDB 持久化操作是在 rdbSave()，想要直接进行 RDB 持久化，调用 rdbSave() 即可。

以下主要以代码的方式来展开 RDB 的运作机制：

    
    // 备份主程序
    /* Save the DB on disk. Return REDIS_ERR on error, REDIS_OK on success */
    int rdbSave(char *filename) {
        dictIterator *di = NULL;
        dictEntry *de;
        char tmpfile[256];
        char magic[10];
        int j;
        long long now = mstime();
        FILE *fp;
        rio rdb;
        uint64_t cksum;
    
        // 打开文件，准备写
        snprintf(tmpfile,256,"temp-%d.rdb", (int) getpid());
        fp = fopen(tmpfile,"w");
        if (!fp) {
            redisLog(REDIS_WARNING, "Failed opening .rdb for saving: %s",
                strerror(errno));
            return REDIS_ERR;
        }
    
        // 初始化 rdb 结构体。rdb 结构体内指定了读写文件的函数，已写/读字符统计等数据
        rioInitWithFile(&rdb,fp);
    
        if (server.rdb_checksum) // 校验和
            rdb.update_cksum = rioGenericUpdateChecksum;
    
        // 先写入版本号
        snprintf(magic,sizeof(magic),"REDIS%04d",REDIS_RDB_VERSION);
        if (rdbWriteRaw(&rdb,magic,9) == -1) goto werr;
    
        for (j = 0; j < server.dbnum; j++) {
            // server 中保存的数据
            redisDb *db = server.db+j;
    
            // 字典
            dict *d = db->dict;
            if (dictSize(d) == 0) continue;
    
            // 字典迭代器
            di = dictGetSafeIterator(d);
            if (!di) {
                fclose(fp);
                return REDIS_ERR;
            }
    
            // 写入 RDB 操作码
            /* Write the SELECT DB opcode */
            if (rdbSaveType(&rdb,REDIS_RDB_OPCODE_SELECTDB) == -1) goto werr;
    
            // 写入数据库序号
            if (rdbSaveLen(&rdb,j) == -1) goto werr;
    
            // 写入数据库中每一个数据项
            /* Iterate this DB writing every entry */
            while((de = dictNext(di)) != NULL) {
                sds keystr = dictGetKey(de);
                robj key,
                    *o = dictGetVal(de);
                long long expire;
    
                // 将 keystr 封装在 robj 里
                initStaticStringObject(key,keystr);
    
                // 获取过期时间
                expire = getExpire(db,&key);
    
                // 开始写入磁盘
                if (rdbSaveKeyValuePair(&rdb,&key,o,expire,now) == -1) goto werr;
            }
            dictReleaseIterator(di);
        }
        di = NULL; /* So that we don't release it again on error. */
    
        // RDB 结束码
        /* EOF opcode */
        if (rdbSaveType(&rdb,REDIS_RDB_OPCODE_EOF) == -1) goto werr;
    
        // 校验和
        /* CRC64 checksum. It will be zero if checksum computation is disabled, the
         * loading code skips the check in this case. */
        cksum = rdb.cksum;
        memrev64ifbe(&cksum);
        rioWrite(&rdb,&cksum,8);
    
        // 同步到磁盘
        /* Make sure data will not remain on the OS's output buffers */
        fflush(fp);
        fsync(fileno(fp));
        fclose(fp);
    
        // 修改临时文件名为指定文件名
        /* Use RENAME to make sure the DB file is changed atomically only
         * if the generate DB file is ok. */
        if (rename(tmpfile,filename) == -1) {
            redisLog(REDIS_WARNING,"Error moving temp DB file on the final destination: %s", strerror(errno));
            unlink(tmpfile);
            return REDIS_ERR;
        }
        redisLog(REDIS_NOTICE,"DB saved on disk");
        server.dirty = 0;
    
        // 记录成功执行保存的时间
        server.lastsave = time(NULL);
    
        // 记录执行的结果状态为成功
        server.lastbgsave_status = REDIS_OK;
        return REDIS_OK;
    
    werr:
        // 清理工作，关闭文件描述符等
        fclose(fp);
        unlink(tmpfile);
        redisLog(REDIS_WARNING,"Write error saving DB on disk: %s", strerror(errno));
        if (di) dictReleaseIterator(di);
        return REDIS_ERR;
    }
    
    // bgsaveCommand(),serverCron(),syncCommand(),updateSlavesWaitingBgsave() 会调用 rdbSaveBackground()
    int rdbSaveBackground(char *filename) {
        pid_t childpid;
        long long start;
    
        // 已经有后台程序了，拒绝再次执行
        if (server.rdb_child_pid != -1) return REDIS_ERR;
    
        server.dirty_before_bgsave = server.dirty;
    
        // 记录这次尝试执行持久化操作的时间
        server.lastbgsave_try = time(NULL);
    
        start = ustime();
        if ((childpid = fork()) == 0) {
            int retval;
    
            // 取消监听
            /* Child */
            closeListeningSockets(0);
            redisSetProcTitle("redis-rdb-bgsave");
    
            // 执行备份主程序
            retval = rdbSave(filename);
    
            // 脏数据，其实就是子进程所消耗的内存大小
            if (retval == REDIS_OK) {
                // 获取脏数据大小
                size_t private_dirty = zmalloc_get_private_dirty();
    
                // 记录脏数据
                if (private_dirty) {
                    redisLog(REDIS_NOTICE,
                        "RDB: %zu MB of memory used by copy-on-write",
                        private_dirty/(1024*1024));
                }
            }
    
            // 退出子进程
            exitFromChild((retval == REDIS_OK) ? 0 : 1);
        } else {
            /* Parent */
            // 计算 fork 消耗的时间
            server.stat_fork_time = ustime()-start;
    
            // fork 出错
            if (childpid == -1) {
                // 记录执行的结果状态为失败
                server.lastbgsave_status = REDIS_ERR;
                redisLog(REDIS_WARNING,"Can't save in background: fork: %s",
                    strerror(errno));
                return REDIS_ERR;
            }
            redisLog(REDIS_NOTICE,"Background saving started by pid %d",childpid);
    
            // 记录保存的起始时间
            server.rdb_save_time_start = time(NULL);
    
            // 子进程 ID
            server.rdb_child_pid = childpid;
            updateDictResizePolicy();
            return REDIS_OK;
        }
        return REDIS_OK; /* unreached */
    }


如果采用 BGSAVE 策略，且内存中的数据集很大，fork() 会因为要为子进程产生一份虚拟空间表而花费较长的时间；如果此时客户端请求数量非常大的话，会导致较多的写时拷贝操作；在 RDB 持久化操作过程中，每一个数据都会导致 write() 系统调用，CPU 资源很紧张。因此，如果在一台物理机上部署多个 redis，应该避免同时持久化操作。

**那如何知道 BGSAVE 占用了多少内存？**子进程在结束之前，读取了自身私有脏数据 Private_Dirty 的大小，这样做是为了让用户看到 redis 的持久化进程所占用了有多少的空间。在父进程 fork 产生子进程过后，父子进程虽然有不同的虚拟空间，但物理空间上是共存的，直至父进程或者子进程修改内存数据为止，所以脏数据 Private_Dirty 可以近似的认为是子进程，即持久化进程占用的空间。


### RDB 数据的组织方式


RDB 的文件组织方式为：**数据集序号1：操作码：数据1：结束码：校验和----数据集序号2：操作码：数据2：结束码：校验和......**

其中，数据的组织方式为：**过期时间：数据类型：键：值，即 TVL（type，length，value)。**

举两个字符串存储的例子，其他的大概都以至于的形式来组织数据：

[![rdb_datastruct_sample](http://md.daoluan.net/blog/images/2014/03/rdb_datastruct_sample.png)](http://md.daoluan.net/blog/images/2014/03/rdb_datastruct_sample.png)

**可见**，RDB 持久化的结果是一个非常紧凑的文件，几乎每一位都是有用的信息。如果对 redis RDB 数据组织方式的细则感兴趣，可以参看 rdb.h 和 rdb.c 两个文件的实现。

对于每一个键值对都会调用 rdbSaveKeyValuePair()，如下：

    
    int rdbSaveKeyValuePair(rio *rdb, robj *key, robj *val,
                            long long expiretime, long long now)
    {
        // 过期时间
        /* Save the expire time */
        if (expiretime != -1) {
            /* If this key is already expired skip it */
            if (expiretime < now) return 0;
            if (rdbSaveType(rdb,REDIS_RDB_OPCODE_EXPIRETIME_MS) == -1) return -1;
            if (rdbSaveMillisecondTime(rdb,expiretime) == -1) return -1;
        }
    
        /* Save type, key, value */
        // 数据类型
        if (rdbSaveObjectType(rdb,val) == -1) return -1;
    
        // 键
        if (rdbSaveStringObject(rdb,key) == -1) return -1;
    
        // 值
        if (rdbSaveObject(rdb,val) == -1) return -1;
        return 1;
    }


如果对 redis RDB 数据格式细则感兴趣，欢迎访问我的 [github](https://github.com/daoluan) & 欢迎讨论。


### 参考文档


[http://redis.io/topics/persistence](http://redis.io/topics/persistence)

----

捣乱 2014-3-26

[http://daoluan.net](http://daoluan.net)
