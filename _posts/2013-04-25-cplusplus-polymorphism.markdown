---
author: daoluan
comments: true
date: 2013-04-25 07:47:48+00:00
layout: post
slug: cplusplus-polymorphism
title: C++ 多态实现机制
wordpress_id: 1720
categories:
- C++
tags:
- C/C++
- 多态
---

本篇从 C++ 初学者遇到的一个有趣的问题开始。


### 有趣的问题


考虑下面的 C++ 程序：

    
    class A
    {
         void func(){}
    };
    
    class B:public A
    {
          void func(){}
    };
    
    int main(void)
    {
         cout << sizeof(A) << " " << sizeof(B) << endl;
         return 0;
    }


输出结果是：1 1

再考虑下面很相似的程序：

    
    class A
    {
         virtual void funcA(){}
    };
    
    class B:public A
    {
         virtual void funcB(){}
    };
    
    int main(void)
    {
         cout << sizeof(A) << " " << sizeof(B) << endl;
         return 0;
    }


输出结果是：4 4

再来考虑下面的形似的程序：

    
    class A
    {
         virtual void funcA(){}
    };
    
    class B:virtual public A
    {
         virtual void funcB(){}
    };
    
    int main(void)
    {
         cout << sizeof(A) << " " << sizeof(B) << endl;
         return 0;
    }


输出结果是：4 12

对于第一种情况，没有出现虚函数，也无任何成员变量，因此是一个空类，空类理论上可以进行实例化，每个实例在内存中都有独一无二的地址来标明，所以会占用 1B 的空间，无可厚非。

但第二种情况和第三种情况加入了虚函数（virtual function），而且在第三种情况当中，引入了虚基类（virtual base class）的概念，所得到的结果大相径庭，这是 C++ 引入了 virtual function 和 virtual base class，即多态，更形象的解释是「以一个 public base class 的指针或者引用，寻址出一个 derived class object」，但多态带了一定空间上的开销，在效率上也有折损。

其实, 多态机制可以归结为下面三这句话:



	
  * 一般而言, 我们无法知道指针 ptr 所指的对象的真正类型. 但经由 ptr 总是可以存取到对象的 virtual table.

	
  * 虚函数 fn() 总是放在 virtual table 中的固定位置, 用一个固定的索引值就可以 fetch 到.

	
  * 唯一一个执行期需要知道的是 ptr 所指的对象.


下面是 C++ 多态机制实现详解.


### 从最简单的对象模块开始


最为简单的对象模型：

[![Image](http://daoluan.net/blog/wp-content/uploads/2013/04/Image_thumb.png)](http://daoluan.net/blog/wp-content/uploads/2013/04/Image.png)

静态/非静态 成员函数 和 静态/非静态 成员变量 的地址都存储在一个表当中，通过表内存储的地址指向相应的部分。这样的设计简易，便于理解，类的实例只需要维护这张表就好了，赔上的是空间和执行效率：

空间上：没必要为每一个实例都存储静态成员变量和成员函数

效率上：每次执行实例的一个成员函数都要在表内进行搜索

这是最初的假设，实际的实现肯定没有那么简单，下面是将变量和函数分割存储的模型（表格驱动对象模型）：

[![Image(1)](http://daoluan.net/blog/wp-content/uploads/2013/04/Image1_thumb.png)](http://daoluan.net/blog/wp-content/uploads/2013/04/Image1.png)

简易对象模型经改良后可以的得到这种。sizeof(A) 的结果是 8。

为支撑 virtual function ，引入了现在的 C++ 对象模型：

[![Image(2)](http://daoluan.net/blog/wp-content/uploads/2013/04/Image2_thumb.png)](http://daoluan.net/blog/wp-content/uploads/2013/04/Image2.png)

**非静态成员变量同指向虚拟函数表的指针（vptr），**和**静态成员变量/函数，非静态成员函数**分离存储。类的每一个实例都存有 vptr 和 非静态成员函数，他们独立拥有这些数据，并不和其他的实例共享。这时候，回到第二种情况，class A 和 继承自 A 的 class B 都拥有虚函数，因此都会有一个 vptr，因此 sizeof 运算得到的结果都为 4.然而，如果往里面添加一个非静态 int 型变量，那么相应可以得到 8B 的大小；但往里面添加静态 int 型变量，大小却没有改变。


### **单一继承**


下面是单一继承里经常看到的一个程序：

    
    class A
    {
    public:
    	int a;
    	void foo(){}
    	virtual void funcA(){}
    	virtual void func()
    	{cout << "class A's func." << endl;}
    };
    
    classB : public A
    {
    public:
    	int b;
    	void foo(){}
    	virtual void funcB(){}
    	virtual void func()
    	{cout << "class B's func." << endl;}
    };
    
    int main(void)
    {
    	A *pa = newB;
    	pa->func();
    }


输出结果是：class B'sfunc.

多态就是多种状态，一个事物可能有多种表现形式，譬如动物，有十二生肖甚至更多的表现形式。当基类里实现了某个虚函数，但派生类没有实现，那么类 B 的实例里的虚函数表中放置的就是 &A::func。此外，派生类也实现了虚函数，那么类 B 实例里的虚函数表中放置的就是 B::func。A *pa = new B; 因为 B 实现了 func，那么它被放入 A 实例的虚拟函数表中，从而代替 A 实例本身的虚拟函数。pa->func(); 调用的结果就不稀奇了，这是虚函数机制带来的。

class A 和 class B 的内存布局和 vptr 可能是下面的样子：



	
  1. ----------

	
  2. |   int a |

	
  3. ----------

	
  4. |    vptr | -------->|      &A::funcA()

	
  5. ----------             -------------------------------------------------

	
  6.                           |      &A::func()

	
  7.                          -------------------------------------------------



	
  1. ----------

	
  2. |   int a |

	
  3. ----------

	
  4. |    vptr | -------->|     &A::funcA() 依旧是 A 的虚函数

	
  5. ----------             -------------------------------------------------

	
  6. |   int b |              |     &B::func() A::func()

	
  7. ----------             -------------------------------------------------

	
  8.                           |     &B::funcB()

	
  9.                           -------------------------------------------------


倘若 虚函数 以外的就没有「多态」效果了，除非进行强制类型转换：

	
  * pa->a;          //     成功，因为 pa 的类型就是 A

	
  * pa->b;          //     失败，因为 B::b

	
  * pa->funcB();  //     失败，因为B::funcB() 不是虚函数

	
  * pa->funcA();  //     成功，因为A::funcA()


**总结一下：**



	
  * 当引入虚函数的时候，会添加 vptr 和 其指向的一个虚拟函数表从而增加额外的空间，这些信息在编译期间就已经确定，而且在执行期不会插足修改任何内容。

	
  * 在类的构造和析构函数当中添加对应的代码，从而能够为 vptr 设定初值或者调整 vptr，这些动作由编译器完成，class 会产生膨胀。

	
  * 当出现继承关系时，虚拟函数表可能需要改写，即当用基类的指针指向一个派生类的实体地址，然后通过这个指针来调用虚函数。这里要分两种情况，当派生类已经改写同名虚函数时，那么此时调用的结果是派生类的实现；而如果派生类没有实现，那么调用依然是基类的虚函数实现，而且仅仅在多态仅仅在虚函数上表现。

	
  * 多态仅仅在虚函数上表现，意即倘若同样用基类的指针指向一个派生类的实体地址，那么这个指针将不能访问和调用派生类的成员变量和成员函数。

	
  * 所谓执行期确定的东西，就是基类指针所指向的实体地址是什么类型了，这是唯一执行期确定的。以上是单一继承的情况，在多重继承的情况会更为复杂。




### **多重继承**


下面是少有看到的程序代码：

    
    class A
    {
    public:
    	virtual ~A(){cout << "A destruction" << endl;}
    	int a;
    	void fooA(){}
    	virtual void func(){cout << "A func." << endl;};
    	virtual void funcA(){cout << "funcA." << endl;}
    };
    
    class B
    {
    public:
    	virtual ~B(){cout << "B destruction" << endl;}
    	int b;
    	void fooB(){}
    	virtual void func(){cout << "B func." << endl;};
    	virtual void funcB(){cout << "funcB." << endl;}
    };
    
    class C : public A,public B
    {
    public:
    	virtual ~C(){cout << "C destruction" << endl;}
    	int c;
    	void fooC(){}
    	virtual void func(){cout << "C func." << endl;};
    	virtual void funcC(){cout << "funcC." << endl;}
    };
    
    int main(void) 
    {  
    	return 0;
    }


当用基类的指针指向一个派生类的实体地址，基类有两种情况，一种是 class A 和 class B，如果是 A，问题容易解决，几乎和上面单一继承情况类似；但倘若是 B，要做地址上的转换，情况会比前者复杂。先展现class A，B，C 的内存布局和 vptr：



	
  1. ----------

	
  2. |   int a |

	
  3. ----------

	
  4. |    vptr | -------->|      &A::~A()

	
  5. ----------             -------------------------------------------------

	
  6.                             |      &A::func()

	
  7.                             -------------------------------------------------

	
  8.                             |      &A::funcA()

	
  9.                             -------------------------------------------------



	
  1. ----------

	
  2. |   int b |

	
  3. ----------

	
  4. |    vptr | -------->|     &B::~B()

	
  5. ----------             -------------------------------------------------

	
  6.                             |     &B::func()

	
  7.                             -------------------------------------------------

	
  8.                             |     &B::funcB()

	
  9.                             --------------------------------------------------




	
  1.                             |      &C::~C() &A::~A()

	
  2. ----------             -------------------------------------------------

	
  3. |   int a |               |      &C::func() &A::func()

	
  4. ----------             -------------------------------------------------

	
  5. ----------             |      &C::funcC()

	
  6. |    vptr | -------->-------------------------------------------------

	
  7. ----------             |      &A::funcA()

	
  8. ----------             -------------------------------------------------

	
  9. |   int b |               |      &B::funcB() 跳

	
  10. ----------             -------------------------------------------------

	
  11. ----------

	
  12. |    vptr | -------->|     &C::~C() &B::~B() 跳

	
  13. ----------             -------------------------------------------------

	
  14. |   int c |               |     &C::func() &B::func() 跳

	
  15. ----------             -------------------------------------------------

	
  16.                            |     &B::funcB()

	
  17.                             --------------------------------------------------


多重继承中，会有保留两个虚拟函数表，一个是与 A 共享的，一个是与 B 相关的，他们都在原有的基础上进行了修改：

对于 A 的虚拟函数表：

	
  * 覆盖派生类实现的同名虚函数，并用派生类实现的析构函数覆盖原有虚函数

	
  * 添加了派生类独有的虚函数

	
  * 添加了右端父类即 B 的独有虚函数，需跳转


对于 B 的虚拟函数表：

	
  * 覆盖派生类实现的同名虚函数，并用派生类实现的析构函数覆盖原有虚函数，但需跳转



	
  1. int main(void)

	
  2. {

	
  3.      A *pa = new C;

	
  4.      B *pb = new C;

	
  5.      C *pc = new C;

	
  6. 
	
  7.      pa->func();

	
  8.      pb->func();

	
  9.      pc->funcC();

	
  10. 
	
  11.      delete pb;

	
  12.      delete pa;

	
  13.      delete pc;

	
  14. }


输出结果是：

_C func.
C func.
funcC.
C destruction
B destruction
A destruction
C destruction
B destruction
A destruction
C destruction
B destruction
A destruction_

7 行和 8 行的行为有很大的区别，7 行的调用和上面的单一继承的情况类似，不赘述。8 行的 pb->func(); 中，pb 所指向的是上图第 9 行的位置，编译器已在内部做了转换，也就是 pa 和 pb 所指的位置不一样，pa 指向的是上图第 3 行的位置。接着需要注意的是，pb->func(); 调用时，在虚拟函数表中找到的地址需要再进行一次跳转，目标是 A 的虚拟函数表中的 &C::func()，然后才真正执行此函数。所以，上面的情况作了指针的调整。

那什么时候会出现跳，常见的有两种情况：



	
  1. 右端基类，对应上面的具体是 B，调用派生类虚拟函数，比如 pb->~C() 和 pb->func()

	
  2. 派生类调用右端基类的虚拟函数，比如 pc->funcB()


所以 delete pa; 和 delete pa; 的操作是不一样的，pb->funcB(); 和 pc->funcB(); 也不一样。

C++ 为实现多态引入虚函数机制，带来了空间和执行上的折损。


### **单一/多重继承的构造和析构**


单一继承中，构造函数调用顺序是从上到下（单一继承），从左到右（多重继承），析构函数调用顺序反过来。在上一段程序中，



	
  1.      delete pa;

	
  2.      delete pb;

	
  3.      delete pc;


都自动调用了基类和派生类的析构函数，其中只有 delete pc; 涉及了虚拟函数机制。《Effective C++》中07条款中有这样一句话：**当derived class 对象经由一个 base 指针被删除，而该对象带有一个 non-virtual 析构函数，其结果未有定义---实际执行时通常发生的是对象的 derived 成分未被销毁。**

特地，写了下面的程序：

    
    class A
    {
    public:
    	~A(){cout << "A destruction" << endl;}
    	int a;
    };
    
    class B
    {
    public:
    	~B(){cout << "B destruction" << endl;}
    };
    
    class C : public A,public B
    {
    public:
    	~C(){cout << "C destruction" << endl;}
    };
    
    int main(void)
    {
    	A *pa = new C;
    	B *pb = new C;
    	C *pc = new C;
    	delete pa;     // 没有问题
    	delete pb;     // 出错
    	delete pc;     // 没有问题
    }


所说的「未定义」就在 delete pa; 和 delete pb; 体现出来。

强烈建议，在设计继承关系的时候，为每一个基类实现 virtual 析构函数。

回到开始的问题：



	
  1. 第一种情况是因为编译器安插了一个字节，为的是一个类的对象能再内存有独一无二的地址，无可厚非。

	
  2. 第二种情况是因为编译器安插了 vptr。

	
  3. 第三种情况是因为编译器除了安插 A 和 B 的 vptr 外，还有一个指向虚基类的指针。


另外，虚拟继承在应用比较少应用，一个例子就是：

    
    class ios {...};
    
    class istream : public virtual ios {...};
    
    calss ostream : public virtual ios {...};
    
    class iostream : public istream,public ostream {...};


这里 istream，ostream，iostream 共享同一份 ios。要和下面的情况区分开来：

    
    class ios {...};
    
    class istream : public ios {...};
    
    calss ostream : public ios {...};
    
    class iostream : public istream,public ostream {...};


这里实际有两份 ios ！全文完。[daoluan.net](http://daoluan.net)
