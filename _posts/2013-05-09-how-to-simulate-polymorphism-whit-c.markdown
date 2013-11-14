---
author: daoluan
comments: true
date: 2013-05-09 09:43:51+00:00
layout: post
slug: how-to-simulate-polymorphism-whit-c
title: C 语言实现 C++ 多态
wordpress_id: 1746
categories:
- C/C++
tags:
- C/C++
---

## C 还是 C++？


C++ 中的多态是指「通过基类对象的指针或者基类对象的引用调用虚函数」，表现更多派生类的特性，但[根据 C++ 多态的实现](http://daoluan.net/blog/cplusplus-polymorphism/)，我们发现这种方法存在一定的空间和效率的折损。不可否认，多态轻松解决了很多工程中遇到的问题，这与 pure C 的解决方法比起来，更为优雅。

在考虑移植性上，C 的光芒要盖过 C++，但 C++ 的多态是可借鉴的，于是用 pure C 来模仿 C++ 中多态行为。


## C 如何实现多态


在 C 中没有类的概念，但有 struct，而且 C 中的 struct 是不允许有函数的，只允许存在变量，那是不是**函数变量**就允许存在了？！所以，**函数指针**可以给我们一些提示。

假定有一个结构体 struct Animal 声明如下：

    
    struct Animal
    \{
         void (*move)();
    \};


此时 Animal 中的 move 只是一个指针，并没有赋值，也就是说它不能代表任何的行为，但我们可以在 main 函数中对其进行赋值，赋予相应的行为。

    
    void Animal\_move()
    \{
         printf("Animal move.\n");
    \}


再假定一个结构体 struct Rabbit，我们可以暂且把它看作（因为 C 中没有继承概念）struct Animal 的派生类，声明如下：

    
    struct Rabbit
    \{
         void (*move)();
    \};


同样我们可以给 Rabbit 的 move 预定义一个行为：

    
    void Rabbit\_move()
    \{
         printf("Rabbit move.\n");
    \}


struct Animal 和 struct Rabbit 在内容上完全一致，而且变量对齐上也完全一致，可以通过将 struct Rabbit 类型的指针强制转换为 struct Animal 类型的指针，即：

    
         Animal *panimal;
         Rabbit rabbit;
    
         //...
    
         panimal = (Animal*)&rabbit;


这样，我们就可以通过 struct Animal 类型的指针或者引用来操纵 struct Rabbit 类型的对象了。

    
    int main(void)
    \{
         Animal *panimal;
    
         Rabbit rabbit;
    
         rabbit.move=Rabbit\_move;
    
         panimal = (Animal*)&rabbit;
    
         panimal->move();
    \}


Rabbit move.
请按任意键继续. . .


## C 多态有什么问题


是不是有需要注意的问题？为什么刚才特别提出「在内容上完全一致，而且变量对齐上也完全一致」？倘若把 struct Animal 的声明作稍微的改变：

    
    struct Animal
    \{
         int age;
         void (*move)();
    \};


**运行崩溃了**，并不能得到上面的执行结果，原因是 move 函数指针 在struct Animal 中和 struct Rabbit 中的偏移量不同，结构体是根据变量在结构体的偏移量来读取或者修改变量的。当执行 panimal->move(); 的时候，实际上引用了非法的地址：

panimal->move();

可以被形象的转化为：

( * (panimal+sizeof(age)) ) ();

但发现 panimal 是指向 struct Rabbit 实体的，panimal+sizeof(age) 已经指向了非法地址：








struct Rabbit 结构


调用






void (*move )();


<------ rabbit.move();






非法地址


<------ panimal->move();




因此需要模拟多态，必须**保持函数指针变量对齐**。

在一些 c 开源项目中经常用到这种设计，譬如 libevent。

捣乱 2013-05-09

[http://daoluan.net](http://daoluan.net/)
