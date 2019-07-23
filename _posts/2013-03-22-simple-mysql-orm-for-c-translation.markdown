---
title: "【译】Simple MySQL ORM for C"
date: 2013-03-22 04:48:49 Z
categories:
- cplusplus
- linux
tags:
- C/C++
- GTD项目实录
- linux
- MySQL
- 开源应用
author: daoluan
comments: true
layout: post
wordpress_id: 1613
---

一直不知道有ORM这种东西，直到和 @海坡 交流后才接触。

在项目中，需要将数据存储到数据库中，首先想到的是生成各种raw SQL的解决方法。但随着项目的进展，发现它很不灵活。譬如可能因为有新的需求，在数据库student表中添加dept_no字段，那在各种raw SQ中就需要进行修改了，工程浩大。如果操作（插入\修改\删除）数据库表中的数据，和操作数据对象一样，可以简化很多的操作，便于数据层的变更，而不必修改逻辑层代码。

<!-- more -->

    
    //项目随手摘录的一个构造插入指定对象数据的INSERT语句的方法。
    int gtd_genInsertSql(struct task_t &toinsert,char *sql, int nUserID)
    {
        int curr = 0;
    
        //task_id | user_id | strtext
        curr += sprintf(sql,"insert into task values(%d,%d,'%s',",
            toinsert.id,nUserID/*user_id*/,toinsert.strtext);
    
        //ctime    
        char buffer[32];
        ::memset(buffer,0,sizeof(buffer));
    
        strftime(buffer,32,"'2012-%m-%d %H-%M-%S',",&(toinsert.ctime));
        strncpy(sql+curr,buffer,strlen(buffer));
        curr += strlen(buffer);
    ......
        *(sql + curr) = ')';
        curr++;
        return curr;
    }


ORM，即对象关系映射，ORM的设计就是数据库持久层的设计。目前流行有一些成熟的ORM框架，对应各种语言都有。

因为项目实际需要，挑选了一个轻便的框架：Simple MySQL ORM for C。google了下，只发现有Simple MySQL ORM for C作者的一篇英文博文介绍而已：http://ales.jikos.cz/smorm/。「打米量家底」，因为那篇文章不太长，所以把它翻译过来了。记得年前 @独酌逸醉 有提到过，他有翻译StackOverFlow上的精华帖。现在看来，譬如对C++熟悉，完全可以去看看外国的程序员社区。一方面你本身是程序员，专业对口，认得大多数单词；另一方面，国外高手也多，不为是提高技术的好机会；最后，它确实提高英语的好方法，赞一个。

下面是《Simple MySQL ORM for 》的译文，原文链接：[http://ales.jikos.cz/smorm/](http://ales.jikos.cz/smorm/)


### 【译】Simple MySQL ORM for C




作者：alesak


c版本Simple MySQL ORM是用python的脚本完成的，它可以用来连接已经创建的MySQL数据库，读取数据库表所对应的数据结构，当然，也可以通过此数据结构和方法创建表。这些可以让开发者使用c语言很方便的更新/修改/删除数据库中的数据。

之前，笔者需要在强大的数据库里面存储检索结构化数据。笔者更倾向于使用MySQL和c语言。但笔者对自己写的粗糙代码和互联网上找到的巨费资源的解决方案已经很厌烦了，所以干脆自己写了一个。很简单，很天真，下笔粗糙（python不是笔者的母语，抱歉了）。但相信情人眼里出西施，笔者想象着让它更有用一点。还有，关于它的文档。。。

考虑到这只是一个技术文章，而不是一个使用手册。笔者最后取消了此文章提到的项目，所以它有待考验。不支持MySQL里头的一些数据类型。这个项目的起因之一是笔者不喜欢MySQL提供的c api，所以代之以“更时髦”的万事俱备的api~但，笔者发现它有些地方还不够好，因为笔者还没完成。

让我们开始吧。首先，你必须创建你的数据库表。笔者更喜欢一下这种方式，因为只有这样才能更充分使用数据库。

    
    CREATE DATABASE ex1;
    
    CREATE TABLE ex_customer (
      id int NOT NULL auto_increment,
      name char(32),
      PRIMARY KEY  (id)
    );
    
    CREATE TABLE ex_item (
      customer_id int,
      itemname char(32)
    );


接下来，我们创建一个简单的python脚本db.py：

    
    dbname = "ex1"
    name = "db"
    tables = { }


在接下来，让它执行吧 :P

    
    python rdb.py


当然，比起真正的rock，少点听觉享受。可能你会问，笔者到底要怎么连接到数据库啊？当然，那些只是默认用户写的……但看看我们得到的结果。我们可以已经有两个文件产生了，分别是：db.h和db.c。前者包含是象征数据库表的数据结构声明和操作这些数据结构的方法；后者包含了方法的定义，接着的是数据初始化的语句。我们来看看：

    
    typedef struct db_ex_customer {
            int id;
            char * name;
    } db_ex_customer;
    
    typedef struct db_ex_item {
            int customer_id;
            char * itemname;
    } db_ex_item;


相信没有进一步解释这些东西的必要。让我们使用它们吧！笔者新建了ex1.c文件。注意：为了更容易读懂代码，笔者没有处理错误的返回值：

    
    #include <db.h>
    #include <stdio.h>
    #include <string.h>
    #include <time.h>
    
    int main (int argc, char **argv)
    {
    	int ret;
    	MYSQL global_mysql;
    	MYSQL *m;
    
    	db_ex_customer *cust1;
    	db_ex_item *item1, *item2;
    
    	mysql_init (& global_mysql);
    
    	/*
    	 * connect to MySQL as usual
    	 */
    	m = mysql_real_connect (& global_mysql, "localhost", "root", "", "ex1", 3036, NULL, 0);
    
    	/*
    	 * pass the MySQL connection to function, that initializes the "ORM"
    	 */
    	ret = db_init (& global_mysql);
    
    	/*
    	 * the *__new method creates empty structure
    	 */
    	cust1 = db_ex_customer__new ();
    	/*
    	 * setting the structure attribute with allocated string,
    	 * it will be freed during call of *__free method
    	 */
    	cust1->name = strdup ("alesak");
    
    	/*
    	 * this method inserts the structure into according table.
    	 * If it has serial field, its value is reflected into structure
    	 */
    	ret = db_ex_customer__insert (cust1);
    
    	item1 = db_ex_item__new ();
    	/*
    	 * let's use the serial value from newly inserted customer
    	 */
    	item1->customer_id = cust1->id;
    	item1->itemname = strdup ("simple orm");
    
    	ret = db_ex_item__insert (item1);
    
    	item2 = db_ex_item__new ();
    	item2->customer_id = cust1->id;
    	item2->itemname = strdup ("advanced orm");
    
    	ret = db_ex_item__insert (item2);
    
    	db_ex_customer__free (cust1);
    	db_ex_item__free (item1);
    	db_ex_item__free (item2);
    
    	return (0);
    }


编译下：

    
    cc -I `mysql_config --cflags` ex1.c db.c `mysql_config --libs` -o ex1


运行可执行文件，发现它没错。这意味着，它已经一些数据已被存储。至少如果你让评价它，笔者会说很优雅。接下来，怎么去检索这些数据？假设，我们已经知道数据库表中记录的键值，笔者又新建了ex2.c文件。

    
    #define _XOPEN_SOURCE 500
    #include <db.h>
    #include <stdio.h>
    #include <string.h>
    #include <time.h>
    
    int main (int argc, char **argv)
    {
    	int ret;
    	MYSQL global_mysql;
    	MYSQL *m;
    
    	db_ex_customer *cust1;
    	db_ex_item *item1, *item2;
    
    	mysql_init (& global_mysql);
    
    	m = mysql_real_connect (& global_mysql, "localhost", "root", "", "ex1", 3036, NULL, 0);
    
    	ret = db_init (& global_mysql);
    
    	cust1 = db_ex_customer__get_by_id (3);
    	if (cust1) {
    		fprintf (stdout, "I have customer named \'%s\'\n", cust1->name);
    		db_ex_customer__free (cust1);
    	}
    
    	return (0);
    }


跟前边一样，编译，然后执行：

    
    cc -I. `mysql_config --cflags` ex2.c db.c `mysql_config --libs` -o ex2
    ./ex2


最后，笔者不想让ORM自动创建相关数据的查询，因为笔者相信它能做的好。（老实说，如果使用默认的MyISAM,它不可能判断相关数据）。当然，接下来笔者想要新建笔者自己的、超复杂的ex_items表与ex_customer标连接后的SELECT检索。编辑一下db.py：

    
    dbname = "ex1"
    name = "db"
    tables = {
    		"ex_item" :[("get", "get_customer_items",
    			[("INTEGER", "customer_id")], "SELECT ex_item.* FROM ex_item WHERE customer_id = ?")]
    	}


重新执行db.puy脚本会添加新的db_ex_item__get_customer_items_*方法集。这些方法灵活之处在于，可以增加INTEGER类型的参数，在特定的SQL上打开游标：从游标读取一行记录，关闭游标。我们扩展ex2.c：

    
    #define _XOPEN_SOURCE 500
    #include <db.h>
    #include <stdio.h>
    #include <string.h>
    #include <time.h>
    
    int main (int argc, char **argv)
    {
    	int ret;
    	MYSQL global_mysql;
    	MYSQL *m;
    
    	db_ex_customer *cust1;
    	db_ex_item *item1, *item2;
    
    	mysql_init (& global_mysql);
    
    	m = mysql_real_connect (& global_mysql, "localhost", "root", "", "ex1", 3036, NULL, 0);
    
    	ret = db_init (& global_mysql);
    
    	cust1 = db_ex_customer__get_by_id (3);
    	if (cust1) {
    		fprintf (stdout, "I have customer named \'%s\'..\n", cust1->name);
    
    		db_ex_item__get_customer_items_open (cust1->id);
    
    		while ((item1 = db_ex_item__get_customer_items_fetch ()) != NULL) {
    			fprintf (stdout, ".. and found his item named \'%s\'\n", item1->itemname);
    			db_ex_item__free (item1);
    		}
    		db_ex_item__get_customer_items_close ();
    
    		db_ex_customer__free (cust1);
    	}
    
    	return (0);
    }


得偿所愿，它打印的结果：

    
    I have customer named 'alesak'..
    .. and found his item named 'simple orm'
    .. and found his item named 'advanced orm'


以上，朋友们！这里是[http://ales.jikos.cz/smorm/rdb.py](http://ales.jikos.cz/smorm/rdb.py) 脚本。更确切的说，别下载这个破烂东西。但如果你喜欢这个点子，请告诉笔者：alesak#gmail.com。全文完。

感谢作者 @alesak。Simple MySQL ORM for C我没有亲手测试，找时间补上测试篇。另，笔者水平有限，欢迎扶正拍砖。以上。

捣乱 2013-3-22

[http://daoluan.net](http://daoluan.net)
