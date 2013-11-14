---
author: daoluan
comments: true
date: 2012-09-20 01:15:13+00:00
layout: post
slug: mysql-entry
title: MySQL入门教程
wordpress_id: 1063
categories:
- Linux
- 学习总结
tags:
- Linux
- MySQL
---

环境：Linux  2.6.32-28-generic


### MySQL数据库安装


最懒的方法：

    
    root@daoluan:~# apt-get install mysql-server


安装过程中会要求输入数据库密码。安装结束后，可以通过命令：

    
    root@daoluan:~# mysql –u root –p


登录数据库。

<!-- more -->


### 实例操作



    
    root@daoluan:~# mysql -u root -p 
    Enter password: 
    Welcome to the MySQL monitor.  Commands end with ; or \g. 
    Your MySQL connection id is 66 
    Server version: 5.1.63-0ubuntu0.10.04.1 (Ubuntu)
    
    Copyright (c) 2000, 2011, Oracle and/or its affiliates. All rights reserved.
    
    Oracle is a registered trademark of Oracle Corporation and/or its 
    affiliates. Other names may be trademarks of their respective 
    owners.
    
    Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.
    
    mysql>


可以直接输入MySQL命令。

    
    mysql> SHOW DATABASE;
    
    mysql> create database library;
    
    mysql> use library;
    
    mysql> create table members (member\_id int(11) not null auto\_increment,fname varchar(50) not null,lname varchar(50) not null,tel varchar(15),email varchar(50) not null,primary key (member\_id);
    
    。。。。




### MySQL Connector C


MySQL提供C接口的数据库连接器。最懒的方法：

root@daoluan:~# apt-get install libmysqlclient16-dev

16是版本号。安装完毕过后在所需要使用数据库功能的源码文件里头添加：




    
    #include<mysql.h>







### c语言MySQL连接示例



    
    #include <stdio.h>
    #include <mysql/mysql.h>
    
    int main(int argc, char *argv[])
    \{
    	/* declare structures and variables */
        MYSQL *conn\_ptr;
    	MYSQL\_ROW  row;
        MYSQL\_FIELD * fields; 
    	MYSQL\_RES * result;
        unsigned int i,num\_fields;
    
    	/* initialize MySQL structure  */
        conn\_ptr = mysql\_init(NULL);
    
    	/* connect to database */
        conn\_ptr = mysql\_real\_connect(conn\_ptr, "localhost", "root", "123456",
                "library", 0, NULL, 0);
    
    	/* execute query */		
        mysql\_query(conn\_ptr,"select * from members");
    
    	/* get result set */
        result = mysql\_store\_result(conn\_ptr);
    
    	/* get the number of fields */
    	num\_fields = mysql\_num\_fields(result);
    
    	/* print result set */
        while((row = mysql\_fetch\_row(result)) != NULL)
        \{
            for(i=0; i<num\_fields; i++)
            \{
                printf("%s ",row[i]!=NULL?row[i]:"NULL");
            \}// for
            printf("\n");
        \}// while
    
    	/* clean up */
    	mysql\_free\_result(result);
        mysql\_close(conn\_ptr);
        return EXIT\_SUCCESS;
    \}


将上面的代码存档为sample.c

    
    root@daoluan:/code/sample\_mysql# gcc -o sample sample.c -lmysqlclient


关于gcc的“-l”选项等诸多选项，[http://www.cppblog.com/SEMAN/archive/2005/11/30/1440.html](http://www.cppblog.com/SEMAN/archive/2005/11/30/1440.html)。执行 结果（数据库中已经预存了三条数据）：

    
    root@daoluan:/code/sample\_mysql# ./sample
    1 John Doe 1234567 jdoe@somewhere.com
    2 aaa aaa 1234567 aaa@aaa.com
    3 bbb bbb 1234567 bbb@bbb.com
    root@daoluan:/code/sample\_mysql#


下面是有用的链接：

[ttp://www.zhangliancheng.com/2011/04/build\_mysql\_c\_develop\_environment\_in\_ubuntu/](http://www.zhangliancheng.com/2011/04/build\_mysql\_c\_develop\_environment\_in\_ubuntu/)

[Ubuntu安装配置Mysql - 武侯 - 博客园](http://www.cnblogs.com/wuhou/archive/2008/09/28/1301071.html)

[MySQL C API](http://dev.mysql.com/doc/refman/5.6/en/c.html)

[ubuntu下安装MySQL和connector过程 - ArtMath------数学是一门艺术 - 博客大巴](http://artmath.blogbus.com/logs/76621657.html)

[Linux下安装使用mysql connector（C++） - cscmaker的专栏 - 博客频道 - CSDN.NET](http://blog.csdn.net/cscmaker/article/details/7468374)

reference:《MySQL 完全手册》

本文完 2012-09-20

捣乱小子 [http://www.daoluan.net/blog/](http://www.daoluan.net/blog/)
