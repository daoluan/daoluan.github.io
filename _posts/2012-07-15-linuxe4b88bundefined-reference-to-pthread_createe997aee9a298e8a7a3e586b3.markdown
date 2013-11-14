---
author: daoluan
comments: true
date: 2012-07-15 07:42:30+00:00
layout: post
slug: linux%e4%b8%8bundefined-reference-to-pthread_create%e9%97%ae%e9%a2%98%e8%a7%a3%e5%86%b3
title: Linux下undefined reference to 'pthread_create'问题解决
wordpress_id: 657
categories:
- Linux
tags:
- apue 学习总结
- Linux
---

接触了Linux系统编程中的线程编程模块，可gcc sample.c（习惯把书上的sample代码写进sample.c文件中）出现“undefined reference to 'pthread\_create'”，所有关于线程的函数都会有此错误，导致无法编译通过。

问题的原因：pthread不是Linux下的默认的库，也就是在链接的时候，无法找到phread库中哥函数的入口地址，于是链接会失败。

解决：在gcc编译的时候，附加要加 -lpthread参数即可解决。

<!-- more -->

    
    #include <stdio.h> 
    #include <pthread.h> 
    #include <unistd.h> 
    pthread\_t ntid; 
    void printids(const char * s) 
    \{ 
        pid\_t pid; 
        pthread\_t tid; 
        pid = getpid(); 
        tid = pthread\_self(); 
        printf("%s pid %u tid %u (0x%x)\n",s,(unsigned int)pid, 
                (unsigned int)tid,(unsigned int)tid); 
    \} 
    void * thr\_fn(void * arg) 
    \{ 
        printids("new thread:"); 
        return ((void *)0); 
    \} 
    int main(void) 
    \{ 
        int err; 
        err = pthread\_create(&ntid,NULL,thr\_fn,NULL); 
        if(err != 0) 
            printf("pthread\_create error \n"); 
        printids("main thread:"); 
        sleep(1); 
        return 0; 
    \}


**root@daoluan:/code/pthreadid# gcc sample.c**
/tmp/cc1WztL9.o: In function `main':
sample.c:(.text+0x83): undefined reference to `pthread\_create'
collect2: ld returned 1 exit status

**root@daoluan:/code/pthreadid# gcc -lpthread sample.c**
root@daoluan:/code/pthreadid# ./a.out
main thread: pid 7059 tid 3078141632 (0xb778b6c0)
new thread: pid 7059 tid 3078138736 (0xb778ab70)

本文完 2012-07-15

捣乱小子 [http://www.daoluan.net/blog/](http://www.daoluan.net/blog/)
