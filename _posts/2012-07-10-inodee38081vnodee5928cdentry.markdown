---
author: daoluan
comments: true
date: 2012-07-10 06:57:39+00:00
layout: post
slug: inode%e3%80%81vnode%e5%92%8cdentry
title: Linux/Unix inode、vnode和dentry
wordpress_id: 626
categories:
- Linux
tags:
- apue 学习总结
---

传统的Unix既有v节点（vnode）也有i节点（inode），vnode的数据结构中包含了inode信息。但在Linux中没有使用vnode，而使用了通用inode。“实现虽不同，但在概念上是一样的。”

vnode ("virtual node")仅在文件打开的时候，才出现的；而inode定位文件在磁盘的位置，它的信息本身是存储在磁盘等上的，当打开文件的时候从磁盘上读入内存。

[![fs](http://www.daoluan.net/blog/wp-content/uploads/2012/07/fs_thumb.jpg)](http://www.daoluan.net/blog/wp-content/uploads/2012/07/fs.jpg)

<!-- more -->

inode信息就存储在磁盘的某个分区上。下图是上图的一个扩展：inode指示了文件在数据块中的物理位置。所以仅仅存在inode无法描述一个完整的文件系统，比如：目录与目录的树状结构，这一点在inode上无法体现。

延伸：



	
  * 如果多个 inode 指向同一个数据块的时候，是不是就可以实现熟悉的链接了？！这就是软连接的原理，新建一个文件（一个符号链接文件，文件的属性中有明确说明它是一个符号链接文件），为需要链接的文件分配一个新的 inode ，然后指向同一个文件。所以删除软连接文件不会真正删除源文件，而删除源文件过后，软连接文件将失效。

	
  * 多个文件共用一个 inode ，同样可以实现链接？！这就是硬链接的原理， inode 中有链接计数器，当增加一个文件指向这个 inode 时，计数器增1。特别的，当计数器为 0 时候，即所有的文件都删除，文件才真正从磁盘删除；当然，修改其中任何一个文件，都会作用在其他硬链接文件上。


[![较详细的柱面组的i节点和数据块](http://www.daoluan.net/blog/wp-content/uploads/2012/07/i_thumb.png)](http://www.daoluan.net/blog/wp-content/uploads/2012/07/i.png)

ext3_inode上的数据结构如下：它记录了很多关于文件的信息，比如文件长度，文件所在的设备，文件的物理位置，创建、修改和更新时间等等，**特别的，它不包含文件名！**

    
    struct ext3_inode {
    	__le16 i_mode; File mode
    	__le16 i_uid; Low 16 bits of Owner Uid
    	__le32 i_size; Size in bytes
    	__le32 i_atime; Access time 
    	__le32 i_ctime; Creation time
    	__le32 i_mtime; Modification time
    
    	__le32 i_dtime; Deletion Time
    	__le16 i_gid; Low 16 bits of Group Id
    	__le16 i_links_count; Links count
    	......
    	__le32 i_block[EXT2_N_BLOCKS]; Pointers to blocks
    	......
    };


引入vnode：早期版本的Unix是这样做的，但是Linux并没有。vnode一般包含了文件类型和对此文件进行各种操作的函数的指针。[![打开文件的内核数据结构](http://www.daoluan.net/blog/wp-content/uploads/2012/07/thumb.jpg)](http://www.daoluan.net/blog/wp-content/uploads/2012/07/2f1e41c3b813.jpg)



Linux上有dentry，中文的意思就是目录项，它粘合了内存中文件和磁盘中文件，同时它保存是经常访问的目录信息。


> [http://unix.stackexchange.com/questions/4402/what-is-a-superblock-inode-dentry-and-a-file](http://unix.stackexchange.com/questions/4402/what-is-a-superblock-inode-dentry-and-a-file)

A dentry is the glue that holds inodes and files together by relating inode numbers to file names. Dentries also play a role in directory caching which, ideally, keeps the most frequently used files on-hand for faster access. File system traversal is another aspect of the dentry as it maintains a relationship between directories and their files.下面是一副很有趣的图片：

[![inode和dentry](http://www.daoluan.net/blog/wp-content/uploads/2012/07/inodedentry_thumb.jpg)](http://www.daoluan.net/blog/wp-content/uploads/2012/07/inodedentry.jpg)



    
    struct dentry {
    	atomic_t d_count; 目录项对象使用计数器
    	unsigned int d_flags; 目录项标志
    	struct inode * d_inode; 与文件名关联的索引节点
    	struct dentry * d_parent; 父目录的目录项对象
    	struct list_head d_hash; 散列表表项的指针
    	struct list_head d_lru; 未使用链表的指针
    	struct list_head d_child; 父目录中目录项对象的链表的指针
    	struct list_head d_subdirs;对目录而言，表示子目录目录项对象的链表
    	struct list_head d_alias; 相关索引节点（别名）的链表
    	int d_mounted; 对于安装点而言，表示被安装文件系统根项
    	struct qstr d_name; 文件名
    	unsigned long d_time; // used by d_revalidate
    	struct dentry_operations *d_op; 目录项方法
    	struct super_block * d_sb; 文件的超级块对象
    	vunsigned long d_vfs_flags;
    	void * d_fsdata;与文件系统相关的数据
    	unsigned char d_iname [DNAME_INLINE_LEN]; 存放短文件名
    };


诸如文件名，父目录等。dentry可以描述目录的树状结构。

ps：本文只对inode，vnode和dentry作简单的介绍，具体的实现还有深入的原理并未做详细的解释。**欢迎斧正！**

本文完 2012-07-10

捣乱小子 [http://www.daoluan.net/blog/](http://www.daoluan.net/blog/)
