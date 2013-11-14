---
author: daoluan
comments: true
date: 2013-08-17 04:59:59+00:00
layout: post
slug: why-is-processing-a-sorted-array-faster-than-an-unsorted-array
title: 程序处理已排序数据为什么比未排序的快？
wordpress_id: 1850
categories:
- 计算机系统
tags:
- 分支预测
---

sof 上的帖子，原文链接：[Why is processing a sorted array faster than an unsorted array?](http://stackoverflow.com/questions/11227809/why-is-processing-a-sorted-array-faster-than-an-unsorted-array).在 [RabbitOverCarrot](http://rabbitovercarrot.sinaapp.com/) 有更多的内容。下面是翻译正文：


## 问题描述：


下面的 C++ 代码，执行结果很诡异。不知道为什么，已排序的数据居然能神奇的让这段代码的执行速度提升六倍之多：

    
    #include <algorithm>
    #include <ctime>
    #include <iostream>
    
    int main()
    \{
        // Generate data
        const unsigned arraySize = 32768;
        int data[arraySize];
    
        for (unsigned c = 0; c < arraySize; ++c)
            data[c] = std::rand() % 256;
    
        // !!! With this, the next loop runs faster
        std::sort(data, data + arraySize);
    
        // Test
        clock\_t start = clock();
        long long sum = 0;
    
        for (unsigned i = 0; i < 100000; ++i)
        \{
            // Primary loop
            for (unsigned c = 0; c < arraySize; ++c)
            \{
                if (data[c] >= 128)
                    sum += data[c];
            \}
        \}
    
        double elapsedTime = static\_cast<double>(clock() - start) / CLOCKS\_PER\_SEC;
    
        std::cout << elapsedTime << std::endl;
        std::cout << "sum = " << sum << std::endl;
    \}





	
  * 在没有调用 `std::sort(data,data+arrSize);` 的情况下，执行时间是**11.54**秒

	
  * 调用过后，执行时间是**1.93**秒





* * *



起初，我以为这可能只是语言或者编译器上导致的异常，于是我用 `Java` 去实现：

    
    public class Main
    \{
        public static void main(String[] args)
        \{
            // Generate data
            int arraySize = 32768;
            int data[] = new int[arraySize];
    
            Random rnd = new Random(0);
            for (int c = 0; c < arraySize; ++c)
                data[c] = rnd.nextInt() % 256;
    
            // !!! With this, the next loop runs faster
            Arrays.sort(data);
    
            // Test
            long start = System.nanoTime();
            long sum = 0;
    
            for (int i = 0; i < 100000; ++i)
            \{
                // Primary loop
                for (int c = 0; c < arraySize; ++c)
                \{
                    if (data[c] >= 128)
                        sum += data[c];
                \}
            \}
    
            System.out.println((System.nanoTime() - start) / 1000000000.0);
            System.out.println("sum = " + sum);
        \}
    \}


虽然时间少点，但差别不大，数量级是一样的。



* * *



我第一反应是已排序数据被放入到了缓存当中，但后来又有一个思路，是不是因为数组是刚被生成的。（这里可能翻译有误：but my next thought was how silly that is because the array was just generated.）

这里面是什么原因？为什么已排序数据会比未排序的快那么多？代码思路是一样的，数据的顺序应该不影响。


## 答案


是分支把你给坑了。



* * *



考虑一个铁路的交合处：

![铁路的交合处](http://i.stack.imgur.com/muxnt.jpg)

图片网址：[http://commons.wikimedia.org/wiki/File:Entroncamento\_do\_Transpraia.JPG](http://commons.wikimedia.org/wiki/File:Entroncamento\_do\_Transpraia.JPG)

为了方便讨论，假设回到 19 世纪，即在长途无线通信之前。

你是铁路交合处的工作人员，现在听到火车来了。你并不知道火车会往哪个方向走。你让这个火车停下，问车长想去哪个方向，然后按下正确的开关。

火车很笨重，动力也很大。火车的一生就是不停的启动停下，启动停下。

还有更好的方法吗？答案是你可以猜测火车的方向！



	
  * 如果猜对了，火车不用停下继续走。

	
  * 如果猜错了，车长会停下火车，倒车，吼叫着要你掰好开关；这样，火车才能重新启动，驶向另一个方向。


**如果每次都猜对了**，火车永远都不会在这里停下来了。

**如果经常猜错**，火车停下，倒车，重新开车，频率很高。



* * *



考虑一个 if 语句：在处理器层面，这是一个分支指令：

![分支指令](http://i.stack.imgur.com/pyfwC.png)

汇编程序设计中jl是一个条件跳转指令，全名jump less，意为小于跳转。

假设你是处理器，你看见了这个分支。你不知道程序将要往哪边走。你会怎么做？你会停止执行，等待前面的指令执行完毕，然后你才能继续执行正确的分支。

现代的处理器很复杂，有着很长的流水线。它们的一生不停的启动停下，启动停下。

还有更好的方法吗？答案是你可以猜测分支要往那边走！



	
  * 如果猜对了，继续执行

	
  * 如果猜错了，必须放弃当前执行的流水线，回滚到分支的地方，然后你才能在另一个分支上执行。


**如果每次都猜对了**，执行不会停下，CPU 被充分利用。

**如果经常猜错**，CPU 停止运算，回滚，重新执行，频率高。



* * *



这就是分支预测。我承认，这是个蹩脚的比喻，因为火车客运发送行驶方向的信号。但在计算机里边，处理器知道最后一刻，才能确定分支的走向。

你如何在策略上减少火车停下，倒车，重新启动的次数？你会根据你的历史数据统计。如果火车 99% 向左边行驶，你就会猜测火车向左行驶；如果向右，你就会猜测火车向右边行驶。所以，当火车 3 次都走同一个方向，就可以预测火车下一次也是同一个方向。

换句话说，尽可能的得到可循的规律，紧接着用这个结论指导你。分支预测大概是这么工作的。

好多应用的分支预测表现不错。现在的分支预测可以达到 90% 的命中率。但面对未知的数据，无迹可寻，分支预测就没用了。

延伸阅读：[http://en.wikipedia.org/wiki/Branch\_predictor](http://en.wikipedia.org/wiki/Branch\_predictor)



* * *





#### 从上面可以得出，zuikui罪魁祸首的是 if 语句：



    
    if (data[c] >= 128)
        sum += data[c];


数据的范围在 0~25 之间。当数据已被排序，前一半的数据不会进入 if 语句内，后一半数据会进入 if 语句内。

这对 CPU 内的分支预测很友好，因为数据连续在分支的同一个执行方向上处理。即便是一个边界计数器也能够很好的预测分支，除非几个迭代过后，程序的走向改变了。

举个例子：
T = branch taken
N = branch not taken

    
    data[] = 0, 1, 2, 3, 4, ... 126, 127, 128, 129, 130, ... 250, 251, 252, ...
    branch = N  N  N  N  N  ...   N    N    T    T    T  ...   T    T    T  ...
    
           = NNNNNNNNNNNN ... NNNNNNNTTTTTTTTT ... TTTTTTTTTT  (easy to predict)


然而，当数据随机，分支预测就成花瓶了，因为不能预测随机数据。因此，有百分之五十的命中，但有百分之五十失败了。

    
    data[] = 226, 185, 125, 158, 198, 144, 217, 79, 202, 118,  14, 150, 177, 182, 133, ...
    branch =   T,   T,   N,   T,   T,   T,   T,  N,   T,   N,   N,   T,   T,   T,   N  ...
    
           = TTNTTTTNTNNTTTN ...   (completely random - hard to predict)





* * *





#### 我们该怎么办？


如果编译器不能优化而进行预测分支，又如果不介意写点晦涩的程序，你可以试试奇技淫巧：

用

    
    int t = (data[c] - 128) >> 31;
    sum += ~t & data[c];


代替：

    
    if (data[c] >= 128)
        sum += data[c];


上面的程序消除了分支，取而代之的是位操作。

（这个 trick 和原来的 if 语句并不是完全等价的。但在这里，无论是排序与否，都有效，都跑得很快）

测试： Core i7 920 @ 3.5 GHz

C++ - Visual Studio 2010 - x64 Release

    
    //  Branch - Random
    seconds = 11.777
    
    //  Branch - Sorted
    seconds = 2.352
    
    //  Branchless - Random
    seconds = 2.564
    
    //  Branchless - Sorted
    seconds = 2.587


Java - Netbeans 7.1.1 JDK 7 - x64

    
    //  Branch - Random
    seconds = 10.93293813
    
    //  Branch - Sorted
    seconds = 5.643797077
    
    //  Branchless - Random
    seconds = 3.113581453
    
    //  Branchless - Sorted
    seconds = 3.186068823


发现：



	
  * 带分支的：数据排序与否结果有很大差别

	
  * 带位操作的：数据排序与否不影响结果

	
  * 在 C++ 的例子中，已经排序的数据，带位操作的确实比分支的快（分支预测非常成功，位操作消耗了点时间，但微乎其微）


--

分支预测算是一种硬件层级的优化，是 CPU 的一部分，就如文中所提到的 trick，往往一些时候可以耍点小聪明，帮助 CPU 避开分支预测。有关分支预测，可以阅读《深入理解计算机系统》。而**软件层级的优化**交由编译器来完成，譬如下面的代码：

    
    for (int i=0; i<1000000; i++);
        print ("over");


编译器选择等级优化的时候，就会忽略 for 语句，以前曾经写过一篇代码优化的文章：[《编程珠玑，字字珠玑》910读书笔记——代码优化](http://www.cnblogs.com/daoluanxiaozi/archive/2012/04/15/2450134.html).

（完）捣乱 2013-08-17

[http://daoluan.net/](http://daoluan.net/)
