---
author: daoluan
comments: true
date: 2012-09-11 04:05:53+00:00
layout: post
slug: delete-twice
title: C++ 一不小心被delete两次
wordpress_id: 1019
categories:
- C/C++
- 学习总结
- 随笔
tags:
- C/C++
- 随笔
---

2012-09-11 22:10：更多经常的讨论 [http://www.cnblogs.com/daoluanxiaozi/archive/2012/09/11/2679972.html](http://www.cnblogs.com/daoluanxiaozi/archive/2012/09/11/2679972.html)

2012-09-11 18:04：看到园里朋友们这么热心，有那么一会心里好兴奋。:)

2012-09-11 下午：本文曾出现很严重的错误，但不要紧，感谢园友们的即使指正。

<!-- more -->

不喜欢程序语言的

C++类中，有时候使用到传值调用（对象实体做参数），遇到这种情况，可要小心了！特别是当你所传值的对象生命周期较长，而非临时对象（生命周期段）的时候。来看看下面的情况：

    
    #include <iostream>
    using namespace std;
    
    class Text
    {
    private:
    	char * str;
    
    public:
    	Text(){str = new char[20];::memset(str,0,20);}
    	void SetText(char * str)
    	{
    		strcpy(this->str,str);
    	}
    	char * GetText() const{return str;}
    	~Text()
    	{
    		cout << "~Text Destruction" << endl;
    		delete [] str;
    		cout << "~Text Over" << endl;
    	}
    };
    
    void Print(Text str)
    {
    	cout << str.GetText() << endl;
    }
    
    int main()
    {
    	Text t;
    	t.SetText("abc");
    	Print(t);
    	return 1;
    }


上面执行的结果出现内存泄露。原因：


> Print(Text str)在对str进行复制构造的时候，没有进行深度拷贝；当 Print退出的时候，因为是临时对象（函数初始时构造），对str进行析构，此时还没有任何破绽；但回到main，继而退出main 的时候，又对t进行析构，但此时t内的str中的内容已经被销毁。由于对一内存空间实施了两次销毁，于是出现内存泄漏。


解决方法：



	
  1. 重写浅拷贝。像一下版本，不同的情况要作出适当的调整：

    
    #include <iostream>
    using namespace std;
    
    class Text
    {
    private:
    	char * str;
    
    public:
    	Text(){str = new char[20];::memset(str,0,20);}
    	Text(Text &t)
    	{
    		str = new char[20];
    		strcpy(str,t.GetText());
    	}
    	void SetText(char * str)
    	{
    		strcpy(this->str,str);
    	}
    	char * GetText() const{return str;}
    	~Text()
    	{
    		cout << "~Text Destruction" << endl;
    		delete [] str;
    		cout << "~Text Over" << endl;
    	}
    };
    
    void Print(Text str)
    {
    	cout << str.GetText() << endl;
    }
    
    int main()
    {
    	Text t;
    	t.SetText("abc");
    	Print(t);
    	return 1;
    }




	
  2. （推荐）不使用传值调用。就像下面书写如下Print版本：

    
    void Print(Text &str)
    {
    	cout << str.GetText() << endl;
    }




	
  3. 除非对象内所有的成员读属**非指针内存内容**，那么谨慎使用文章前面的用法。




## 
后记——语言的探讨


C++，以至于其他的程序语言，都是伟大的创造。他们是规则的世界，一愣一脚皆规则。当对某一规则有所熟知之后，就似发现新大陆似的。但想想，这些规则可经不起碰撞打击，殃及的是coder，是我们。这些规则不像1+1=2，“三点定面”来的铁定，总之比起数学理论来说，似乎程序规则脆弱很多，总之在它们身上看到的价值是有限的，总我还是选择了计算机...为之奈何，不得而知。

本文完 2012-09-11

捣乱小子 [http://www.daoluan.net/blog/](http://www.daoluan.net/blog/)
