---
author: daoluan
comments: true
date: 2013-09-28 16:48:35+00:00
layout: post
slug: rbtree-is-not-difficult-2
title: 红黑树并没有我们想象的那么难(下)
wordpress_id: 2112
categories:
- 学习总结
- 数据结构
- 算法
tags:
- 《STL源码剖析》
- 源代码
- 红黑树
---

### SGI STL map 实现概述


根据上一节的红黑树分析, 结合 sgi stl map 的实现, 看看红黑树的源码是如何实现的. 以下主要以代码的注释为主.

sgi stl map 底层实现是 \_Rb\_tree类, 为了方便管理, \_Rb\_tree 内置了 \_M\_header, 用于记录红黑树中的根节点, 最小节点和最大节点. 在插入删除中都会对其进行维护. 找到一副美艳的图片:

[![rbtree\_header](http://daoluan.net/blog/wp-content/uploads/2013/09/rbtree\_header.jpg)](http://daoluan.net/blog/wp-content/uploads/2013/09/rbtree\_header.jpg)

我只会展开插入和删除的代码. \_Rb\_tree 有 insert\_unique() 和 insert\_equal() 两种, 前者不允许有重复值, 后者可以. insert\_unique() 判断是否有重复值的方法利用了二叉搜索树的性质. 细节请参看下面的代码.


### 为什么选择红黑树作为底层实现


红黑树是一种类平衡树, 但它不是高度的平衡树, 但平衡的效果已经很好了. 补充说明另一种 AVL 树, 我之前的博文: [《编程珠玑，字字珠玑》读书笔记完结篇——AVL树](http://www.cnblogs.com/daoluanxiaozi/archive/2012/04/26/2471256.html)

用过 STL map 么, 你用过 linux 么(这个说大了), 他们都有红黑树的应用. 当你对搜索的效率要求较高，并且数据经常改动的情景，你可以用红黑树, 也就是 map.

至于, 为什么不用 AVL 树作为底层实现, 那是因为 AVL 树是高度平衡的树, 而每一次对树的修改, 都要 rebalance, 这里的开销会比红黑树大. 红黑树插入只要两次旋转, 删除至多三次旋转. 但不可否认的是, AVL 树搜索的效率是非常稳定的. 选取红黑树, 我认为是一种折中的方案.


### 红黑树源代码剖析



    
    // sgi stl \_Rb\_tree 插入算法 insert\_equal() 实现.
    // 策略概述: insert\_equal() 在红黑树找到自己的位置,
    // 然后交由 \_M\_insert() 来处理接下来的工作.
    // \_M\_insert() 会将节点插入红黑树中, 接着调整红黑树,
    // 维持性质.
    template <class \_Key, class \_Value, class \_KeyOfValue,
              class \_Compare, class \_Alloc>
    typename \_Rb\_tree<\_Key,\_Value,\_KeyOfValue,\_Compare,\_Alloc>::iterator
    \_Rb\_tree<\_Key,\_Value,\_KeyOfValue,\_Compare,\_Alloc>
      ::insert\_equal(const \_Value& \_\_v)
    \{
      // 在红黑树中有头结点和根节点的概念, 头结点位于根节点之上,
      // 头结点只为管理而存在, 根节点是真正存储数据的地方. 头结点和根节点互为父节点,
       // 是一种实现的技巧.
      \_Link\_type \_\_y = \_M\_header; // 指向头结点
      \_Link\_type \_\_x = \_M\_root(); // \_M\_header->\_M\_parent, 即指向根节点
    
      // 寻找插入的位置
      while (\_\_x != 0) \{
        \_\_y = \_\_x;
    
        // 小于当前节点要走左边, 大于等于当前节点走右边
        \_\_x = \_M\_key\_compare(\_KeyOfValue()(\_\_v), \_S\_key(\_\_x)) ?
                \_S\_left(\_\_x) : \_S\_right(\_\_x);
      \}
      // \_\_x 为需要插入的节点的位置, \_\_y 为其父节点
      return \_M\_insert(\_\_x, \_\_y, \_\_v);
    \}
    
    // sgi stl \_Rb\_tree 插入算法 insert\_unique() 实现.
    // 策略概述: insert\_unique() 同样也在红黑树中找到自己的位置; 我们知道,
    // 如果小于等于当前节点会往右走, 所以遇到一个相同键值的节点后, 会往右走一步,
    // 接下来一直往左走, 所以下面的实现会对往左走的情况做特殊的处理.
    template <class \_Key, class \_Value, class \_KeyOfValue,
              class \_Compare, class \_Alloc>
    pair<typename \_Rb\_tree<\_Key,\_Value,\_KeyOfValue,\_Compare,\_Alloc>::iterator,
         bool>
    \_Rb\_tree<\_Key,\_Value,\_KeyOfValue,\_Compare,\_Alloc>
      ::insert\_unique(const \_Value& \_\_v)
    \{
      \_Link\_type \_\_y = \_M\_header; // 指向头结点
      \_Link\_type \_\_x = \_M\_root(); // 指向根节点, 可能为空
      bool \_\_comp = true;
    
      // 寻找插入的位置
      while (\_\_x != 0) \{
        \_\_y = \_\_x;
        \_\_comp = \_M\_key\_compare(\_KeyOfValue()(\_\_v), \_S\_key(\_\_x));
    
        // 小于当前节点要走左边, 大于等于当前节点走右边
        \_\_x = \_\_comp ? \_S\_left(\_\_x) : \_S\_right(\_\_x);
      \}
    
      iterator \_\_j = iterator(\_\_y); // 在 \_\_y 上建立迭代器
    
      // 我认为下面判断树中是否有存在键值的情况有点绕,
      // 它充分利用了二叉搜索树的性质, 如此做很 hack, 但不易理解.
      // 要特别注意往左边插入的情况.
    
      // HACKS:
      // 下面的 if 语句是比 \_\_x 小走左边的情况: 会发现, 如果插入一个已存在的键的话,
      // \_\_y 最终会定位到已存在键的右子树的最左子树.
      // 譬如, 红黑树中已经存在一个键为 100 的节点, 其右孩子节点为 101,
      // 此时如果再插入键为 100 的节点, 因为 100<=100, 所以会往右走到达 101 节点,
      // 有 100<101, 继而往左走, 会一直往左走.大家稍微画一个例子就能理解.
      if (\_\_comp)
        // 特殊情况, 如果 \_\_j 指向了最左孩子, 那么肯定要插入新节点.
        if (\_\_j == begin())
          return pair<iterator,bool>(\_M\_insert(\_\_x, \_\_y, \_\_v), true);
        // 其他情况, 这个时候也是往左边插入, 如果存在重复的键值,
        // 那么 --\_\_j 能定位到此重复的键的节点.
        else
          --\_\_j;
    
      // HACKS: 这里比较的是 \_\_j 和 \_\_v, 如果存在键值, 那么 \_\_j == \_\_v,
      // 会跳过 if 语句. 否则执行插入. 也就是说如果存在重复的键, 那么 \_\_j
      // 的值肯定是等于 \_\_v
      if (\_M\_key\_compare(\_S\_key(\_\_j.\_M\_node), \_KeyOfValue()(\_\_v)))
        return pair<iterator,bool>(\_M\_insert(\_\_x, \_\_y, \_\_v), true);
    
      // 此时 \_\_y.value = \_\_v, 不允许插入, 返回键值所在位置
      return pair<iterator,bool>(\_\_j, false);
    \}
    
    // \_M\_insert() 是真正执行插入的地方.
    // 策略概述: 插入策略已经在上篇中详述, 可以根据上篇文章的描述,
    // 和下面代码的注释, 加深对红黑树插入算法里理解
    template <class \_Key, class \_Value, class \_KeyOfValue,
              class \_Compare, class \_Alloc>
    typename \_Rb\_tree<\_Key,\_Value,\_KeyOfValue,\_Compare,\_Alloc>::iterator
    \_Rb\_tree<\_Key,\_Value,\_KeyOfValue,\_Compare,\_Alloc>
      ::\_M\_insert(\_Base\_ptr \_\_x\_, \_Base\_ptr \_\_y\_, const \_Value& \_\_v)
    \{
      \_Link\_type \_\_x = (\_Link\_type) \_\_x\_; // 新节点插入的位置.
      // 关于 \_\_x 的疑问:
      // 1. 它被放到下面的, 第一个 if 语句中, 我觉得是没有必要的,
      // 因为从调用 \_M\_insert() 的函数来看, \_\_x 总是为空.
      // 2. 既然 \_\_x 是新节点插入的位置, 那么为什么不直接在 \_\_x 上创建节点,
      // 还要在下面通过比较来决定新节点是左孩子还是右孩子;
      // 不如直接用指针的指针或者指针的引用来完成, 省去了下面的判断.
    
      \_Link\_type \_\_y = (\_Link\_type) \_\_y\_; // 新节点的父节点
      \_Link\_type \_\_z; // 新节点的位置
    
      if (\_\_y == \_M\_header || \_\_x != 0 ||
          \_M\_key\_compare(\_KeyOfValue()(\_\_v), \_S\_key(\_\_y))) \{
      // 新节点应该为左孩子
        \_\_z = \_M\_create\_node(\_\_v);
        \_S\_left(\_\_y) = \_\_z;               // also makes \_M\_leftmost() = \_\_z
                                          //    when \_\_y == \_M\_header
        if (\_\_y == \_M\_header) \{
          \_M\_root() = \_\_z;
          \_M\_rightmost() = \_\_z;
        \}
        else if (\_\_y == \_M\_leftmost())
          \_M\_leftmost() = \_\_z;   // maintain \_M\_leftmost() pointing to min node
      \}
      // 新节点应该为右孩子
      else \{
        \_\_z = \_M\_create\_node(\_\_v);
        \_S\_right(\_\_y) = \_\_z;
        if (\_\_y == \_M\_rightmost())
          \_M\_rightmost() = \_\_z;  // maintain \_M\_rightmost() pointing to max node
      \}
      \_S\_parent(\_\_z) = \_\_y;
      \_S\_left(\_\_z) = 0;
      \_S\_right(\_\_z) = 0;
    
      // 重新调整
      \_Rb\_tree\_rebalance(\_\_z, \_M\_header->\_M\_parent);
    
      // 更新红黑树节点数
      ++\_M\_node\_count;
    
      // 返回迭代器类型
      return iterator(\_\_z);
    \}
    
    // 插入新节点后, 可能会破坏红黑树性质, \_Rb\_tree\_rebalance() 负责维持性质.
    // 其中:
    // \_\_x 新插入的节点
    // \_\_root 根节点
    // 策略概述: 红黑树插入重新调整的策略已经在上篇中讲述,
    // 可以结合上篇文章和这里的代码注释,
    // 理解红黑树的插入算法.
    inline void
    \_Rb\_tree\_rebalance(\_Rb\_tree\_node\_base* \_\_x, \_Rb\_tree\_node\_base*& \_\_root)
    \{
      // 将新插入的节点染成红色
      \_\_x->\_M\_color = \_S\_rb\_tree\_red;
    
      while (\_\_x != \_\_root && \_\_x->\_M\_parent->\_M\_color == \_S\_rb\_tree\_red) \{
        // \_\_x 的父节点也是红色的情况. 提示: 如果是黑色节点, 不会破坏红黑树性质.
    
        if (\_\_x->\_M\_parent == \_\_x->\_M\_parent->\_M\_parent->\_M\_left) \{
          // 叔父节点
          \_Rb\_tree\_node\_base* \_\_y = \_\_x->\_M\_parent->\_M\_parent->\_M\_right;
    
          if (\_\_y && \_\_y->\_M\_color == \_S\_rb\_tree\_red) \{
            // 第 1 种情况, N,P,U 都红(G 肯定黑).
            // 策略: G->红, N,P->黑. 此时, G 红, 如果 G 的父亲也是红, 性质又被破坏了,
            // HACK: 可以将 GPUN 看成一个新的红色 N 节点, 如此递归调整下去;
            // 特俗的, 如果碰巧将根节点染成了红色, 可以在算法的最后强制 root->红.
            \_\_x->\_M\_parent->\_M\_color = \_S\_rb\_tree\_black;
            \_\_y->\_M\_color = \_S\_rb\_tree\_black;
            \_\_x->\_M\_parent->\_M\_parent->\_M\_color = \_S\_rb\_tree\_red;
            \_\_x = \_\_x->\_M\_parent->\_M\_parent;
          \}
          else \{
    
            if (\_\_x == \_\_x->\_M\_parent->\_M\_right) \{
            // 第 2 种情况, P 为红, N 为 P 右孩子, U 为黑或缺少.
            // 策略: 旋转变换, 从而进入下一种情况:
              \_\_x = \_\_x->\_M\_parent;
              \_Rb\_tree\_rotate\_left(\_\_x, \_\_root);
            \}
            // 第 3 种情况, 可能由第二种变化而来, 但不是一定: P 为红, N 为红.
            // 策略: 旋转, 交换 P,G 颜色, 调整后, 因为 P 为黑色, 所以不怕
            // P 的父节点是红色的情况. over
            \_\_x->\_M\_parent->\_M\_color = \_S\_rb\_tree\_black;
            \_\_x->\_M\_parent->\_M\_parent->\_M\_color = \_S\_rb\_tree\_red;
            \_Rb\_tree\_rotate\_right(\_\_x->\_M\_parent->\_M\_parent, \_\_root);
          \}
        \}
        else \{ // 下面的代码是镜像得出的, 脑补吧.
          \_Rb\_tree\_node\_base* \_\_y = \_\_x->\_M\_parent->\_M\_parent->\_M\_left;
          if (\_\_y && \_\_y->\_M\_color == \_S\_rb\_tree\_red) \{
            \_\_x->\_M\_parent->\_M\_color = \_S\_rb\_tree\_black;
            \_\_y->\_M\_color = \_S\_rb\_tree\_black;
            \_\_x->\_M\_parent->\_M\_parent->\_M\_color = \_S\_rb\_tree\_red;
            \_\_x = \_\_x->\_M\_parent->\_M\_parent;
          \}
          else \{
            if (\_\_x == \_\_x->\_M\_parent->\_M\_left) \{
              \_\_x = \_\_x->\_M\_parent;
              \_Rb\_tree\_rotate\_right(\_\_x, \_\_root);
            \}
            \_\_x->\_M\_parent->\_M\_color = \_S\_rb\_tree\_black;
            \_\_x->\_M\_parent->\_M\_parent->\_M\_color = \_S\_rb\_tree\_red;
            \_Rb\_tree\_rotate\_left(\_\_x->\_M\_parent->\_M\_parent, \_\_root);
          \}
        \}
      \}
      \_\_root->\_M\_color = \_S\_rb\_tree\_black;
    \}
    
    // 删除算法, 直接调用底层的删除实现 \_Rb\_tree\_rebalance\_for\_erase().
    template <class \_Key, class \_Value, class \_KeyOfValue,
              class \_Compare, class \_Alloc>
    inline void \_Rb\_tree<\_Key,\_Value,\_KeyOfValue,\_Compare,\_Alloc>
      ::erase(iterator \_\_position)
    \{
      \_Link\_type \_\_y =
        (\_Link\_type) \_Rb\_tree\_rebalance\_for\_erase(\_\_position.\_M\_node,
                                                  \_M\_header->\_M\_parent,
                                                  \_M\_header->\_M\_left,
                                                  \_M\_header->\_M\_right);
      destroy\_node(\_\_y);
      --\_M\_node\_count;
    \}
    
    // 删除节点底层实现, 删除可能会破坏红黑树性质,
    // \_Rb\_tree\_rebalance()
    // 负责维持性质. 其中:
    // \_\_z 需要删除的节点
    // \_\_root 根节点
    // \_\_leftmost 红黑树内部数据, 即最左子树
    // \_\_rightmost 红黑树内部数据, 即最右子树
    // 策略概述: \_Rb\_tree\_rebalance\_for\_erase() 会根据
    // 删除节点的位置在红黑树中找到顶替删除节点的节点,
    // 即无非是删除节点左子树的最大节点或右子树中的最小节点,
    // 此处用的是有一种策略. 接着, 会调整红黑树以维持性质.
    // 调整的算法已经在上篇文章中详述, 可以根据上篇文章的描述
    // 和此篇的代码注释, 加深对红黑树删除算法的理解.
    inline \_Rb\_tree\_node\_base*
    \_Rb\_tree\_rebalance\_for\_erase(\_Rb\_tree\_node\_base* \_\_z,
                                 \_Rb\_tree\_node\_base*& \_\_root,
                                 \_Rb\_tree\_node\_base*& \_\_leftmost,
                                 \_Rb\_tree\_node\_base*& \_\_rightmost)
    \{
      // \_\_z 是要删除的节点
    
      // \_\_y 最终会指向要删除的节点
      \_Rb\_tree\_node\_base* \_\_y = \_\_z;
      // N 节点
      \_Rb\_tree\_node\_base* \_\_x = 0;
      // 记录 N 节点的父节点
      \_Rb\_tree\_node\_base* \_\_x\_parent = 0;
    
      // 只有一个孩子或者没有孩子的情况
      if (\_\_y->\_M\_left == 0)     // \_\_z has at most one non-null child. y == z.
        \_\_x = \_\_y->\_M\_right;     // \_\_x might be null.
      else
        if (\_\_y->\_M\_right == 0)  // \_\_z has exactly one non-null child. y == z.
          \_\_x = \_\_y->\_M\_left;    // \_\_x is not null.
    
        // 有两个非空孩子
        else \{                   // \_\_z has two non-null children.  Set \_\_y to
          \_\_y = \_\_y->\_M\_right;   //   \_\_z's successor.  \_\_x might be null.
    
          // \_\_y 取右孩子中的最小节点, \_\_x 记录他的右孩子(可能存在右孩子)
          while (\_\_y->\_M\_left != 0)
            \_\_y = \_\_y->\_M\_left;
          \_\_x = \_\_y->\_M\_right;
        \}
    
      // \_\_y != \_\_z 说明有两个非空孩子的情况,
      // 此时的删除策略就和文中提到的普通二叉搜索树删除策略一样:
      // \_\_y 记录了 \_\_z 右子树中最小的节点
      // \_\_x 记录了 \_\_y 的右孩子
      // 用 \_\_y 顶替 \_\_z 的位置, \_\_x 顶替 \_\_y 的位置, 最后用 \_\_y 指向 \_\_z,
      // 从而 \_\_y 指向了要删除的节点
      if (\_\_y != \_\_z) \{          // relink y in place of z.  y is z's successor
    
        // 将 \_\_z 的记录转移至 \_\_y 节点
        \_\_z->\_M\_left->\_M\_parent = \_\_y;
        \_\_y->\_M\_left = \_\_z->\_M\_left;
    
        // 如果 \_\_y 不是 \_\_z 的右孩子, \_\_z->\_M\_right 有左孩子
        if (\_\_y != \_\_z->\_M\_right) \{
    
          \_\_x\_parent = \_\_y->\_M\_parent;
    
          // 如果 \_\_y 有右孩子 \_\_x, 必须有那个 \_\_x 替换 \_\_y 的位置
          if (\_\_x)
            // 替换 \_\_y 的位置
            \_\_x->\_M\_parent = \_\_y->\_M\_parent;
    
          \_\_y->\_M\_parent->\_M\_left = \_\_x;      // \_\_y must be a child of \_M\_left
          \_\_y->\_M\_right = \_\_z->\_M\_right;
          \_\_z->\_M\_right->\_M\_parent = \_\_y;
        \}
        // \_\_y == \_\_z->\_M\_right
        else
          \_\_x\_parent = \_\_y;
    
        // 如果 \_\_z 是根节点
        if (\_\_root == \_\_z)
          \_\_root = \_\_y;
    
        // \_\_z 是左孩子
        else if (\_\_z->\_M\_parent->\_M\_left == \_\_z)
          \_\_z->\_M\_parent->\_M\_left = \_\_y;
    
        // \_\_z 是右孩子
        else
          \_\_z->\_M\_parent->\_M\_right = \_\_y;
    
        \_\_y->\_M\_parent = \_\_z->\_M\_parent;
        // 交换需要删除节点 \_\_z 和 替换节点 \_\_y 的颜色
        \_\_STD::swap(\_\_y->\_M\_color, \_\_z->\_M\_color);
        \_\_y = \_\_z;
        // \_\_y now points to node to be actually deleted
      \}
      // \_\_y == \_\_z 说明至多一个孩子
      else \{                        // \_\_y == \_\_z
        \_\_x\_parent = \_\_y->\_M\_parent;
        if (\_\_x) \_\_x->\_M\_parent = \_\_y->\_M\_parent;
    
        // 将 \_\_z 的父亲指向 \_\_x
        if (\_\_root == \_\_z)
          \_\_root = \_\_x;
        else
          if (\_\_z->\_M\_parent->\_M\_left == \_\_z)
            \_\_z->\_M\_parent->\_M\_left = \_\_x;
          else
            \_\_z->\_M\_parent->\_M\_right = \_\_x;
    
        // \_\_leftmost 和 \_\_rightmost 是红黑树的内部数据, 因为 \_\_z 可能是
        // \_\_leftmost 或者 \_\_rightmost, 因此需要更新.
        if (\_\_leftmost == \_\_z)
          if (\_\_z->\_M\_right == 0)        // \_\_z->\_M\_left must be null also
            // \_\_z 左右孩子都为空, 没有孩子
            \_\_leftmost = \_\_z->\_M\_parent;
        // makes \_\_leftmost == \_M\_header if \_\_z == \_\_root
          else
            \_\_leftmost = \_Rb\_tree\_node\_base::\_S\_minimum(\_\_x);
    
        if (\_\_rightmost == \_\_z)
          if (\_\_z->\_M\_left == 0)         // \_\_z->\_M\_right must be null also
            \_\_rightmost = \_\_z->\_M\_parent;
        // makes \_\_rightmost == \_M\_header if \_\_z == \_\_root
          else                      // \_\_x == \_\_z->\_M\_left
            \_\_rightmost = \_Rb\_tree\_node\_base::\_S\_maximum(\_\_x);
    
        // \_\_y 同样已经指向要删除的节点
      \}
    
      // \_\_y 指向要删除的节点
      // \_\_x 即为 N 节点
      // \_\_x\_parent 指向 \_\_x 的父亲, 即 N 节点的父亲
      if (\_\_y->\_M\_color != \_S\_rb\_tree\_red) \{
        // \_\_y 的颜色为黑色的时候, 会破坏红黑树性质
    
        while (\_\_x != \_\_root && (\_\_x == 0 || \_\_x->\_M\_color == \_S\_rb\_tree\_black))
          // \_\_x 不为红色, 即为空或者为黑. 提示: 如果 \_\_x 是红色, 直接将 \_\_x 替换成黑色
    
          if (\_\_x == \_\_x\_parent->\_M\_left) \{ // 如果 \_\_x 是左孩子
    
            \_Rb\_tree\_node\_base* \_\_w = \_\_x\_parent->\_M\_right; // 兄弟节点
    
            if (\_\_w->\_M\_color == \_S\_rb\_tree\_red) \{
              //第 2 情况, S 红, 根据红黑树性质P,SL,SR 一定黑.
              // 策略: 旋转, 交换 P,S 颜色.
    
              \_\_w->\_M\_color = \_S\_rb\_tree\_black;
              \_\_x\_parent->\_M\_color = \_S\_rb\_tree\_red; // 交换颜色
              \_Rb\_tree\_rotate\_left(\_\_x\_parent, \_\_root); // 旋转
              \_\_w = \_\_x\_parent->\_M\_right; // 调整关系
            \}
    
            if ((\_\_w->\_M\_left == 0 ||
                 \_\_w->\_M\_left->\_M\_color == \_S\_rb\_tree\_black) &&
                (\_\_w->\_M\_right == 0 ||
                 \_\_w->\_M\_right->\_M\_color == \_S\_rb\_tree\_black)) \{
              // 提示: 这是 第 1 情况和第 2.1 情况的合并, 因为处理的过程是一样的.
              // 但他们的情况还是要分门别类的. 已经在文章中详细支出,
              // 似乎大多数的博文中没有提到这一点.
    
              // 第 1 情况, N,P,S,SR,SL 都黑.
              // 策略: S->红. 通过 PN,PS 的黑色节点数量相同了, 但会比其他路径多一个,
              // 解决的方法是在 P 上从情况 0 开始继续调整.
              // 为什么要这样呢? HACKS: 因为既然 PN,PS
              // 路径上的黑节点数量相同而且比其他路径会少一个黑节点,
              // 那何不将其整体看成了一个 N 节点! 这是递归原理.
    
              // 第 2.1 情况, S,SL,SR 都黑.
              // 策略: P->黑. S->红, 因为通过 N 的路径多了一个黑节点,
              // 通过 S 的黑节点个数不变, 所以维持了性质 5. over
    
              // 可能大家会有疑问, 不对啊, 2.1 的情况,
              // 策略是交换父节点和兄弟节点的颜色, 此时怎么没有对父节点的颜色赋值呢?
              // HACKS: 这就是合并情况的好处, 因为就算此时父节点是红色,
              // 而且也将兄弟节点颜色改为红色, 你也可以将 PS,PN 看成一个红色的 N 节点,
              // 这样在下一个循环当中, 这个 N 节点也会变成黑色. 因为此函数最后有一句话:
              // if (\_\_x) \_\_x->\_M\_color = \_S\_rb\_tree\_black;
              // 合并情况, 节省代码量
    
              // 当然是可以分开写的
    
              // 兄弟节点染成红色
              \_\_w->\_M\_color = \_S\_rb\_tree\_red;
    
              // 调整关系
              \_\_x = \_\_x\_parent;
              \_\_x\_parent = \_\_x\_parent->\_M\_parent;
            \} else \{
              if (\_\_w->\_M\_right == 0 ||
                  \_\_w->\_M\_right->\_M\_color == \_S\_rb\_tree\_black) \{
                // 第 2.2.1 情况, S,SR 黑, SL 红.
                // 策略: 旋转, 变换 SL,S 颜色.
    
                if (\_\_w->\_M\_left) \_\_w->\_M\_left->\_M\_color = \_S\_rb\_tree\_black;
                \_\_w->\_M\_color = \_S\_rb\_tree\_red;
                \_Rb\_tree\_rotate\_right(\_\_w, \_\_root);
    
                // 调整关系
                \_\_w = \_\_x\_parent->\_M\_right;
              \}
    
              // 第 2.2.2 情况, S 黑, SR 红.
              // 策略: 旋转, 交换 S,P 颜色, SR->黑色, 重新获得平衡.
              \_\_w->\_M\_color = \_\_x\_parent->\_M\_color;
              \_\_x\_parent->\_M\_color = \_S\_rb\_tree\_black;
              if (\_\_w->\_M\_right) \_\_w->\_M\_right->\_M\_color = \_S\_rb\_tree\_black;
              \_Rb\_tree\_rotate\_left(\_\_x\_parent, \_\_root);
              break;
            \}                        // 下面的代码是镜像得出的, 脑补吧.
          \} else \{                  // same as above, with \_M\_right <-> \_M\_left.
            \_Rb\_tree\_node\_base* \_\_w = \_\_x\_parent->\_M\_left;
            if (\_\_w->\_M\_color == \_S\_rb\_tree\_red) \{
              \_\_w->\_M\_color = \_S\_rb\_tree\_black;
              \_\_x\_parent->\_M\_color = \_S\_rb\_tree\_red;
              \_Rb\_tree\_rotate\_right(\_\_x\_parent, \_\_root);
              \_\_w = \_\_x\_parent->\_M\_left;
            \}
            if ((\_\_w->\_M\_right == 0 ||
                 \_\_w->\_M\_right->\_M\_color == \_S\_rb\_tree\_black) &&
                (\_\_w->\_M\_left == 0 ||
                 \_\_w->\_M\_left->\_M\_color == \_S\_rb\_tree\_black)) \{
              \_\_w->\_M\_color = \_S\_rb\_tree\_red;
              \_\_x = \_\_x\_parent;
              \_\_x\_parent = \_\_x\_parent->\_M\_parent;
            \} else \{
              if (\_\_w->\_M\_left == 0 ||
                  \_\_w->\_M\_left->\_M\_color == \_S\_rb\_tree\_black) \{
                if (\_\_w->\_M\_right) \_\_w->\_M\_right->\_M\_color = \_S\_rb\_tree\_black;
                \_\_w->\_M\_color = \_S\_rb\_tree\_red;
                \_Rb\_tree\_rotate\_left(\_\_w, \_\_root);
                \_\_w = \_\_x\_parent->\_M\_left;
              \}
              \_\_w->\_M\_color = \_\_x\_parent->\_M\_color;
              \_\_x\_parent->\_M\_color = \_S\_rb\_tree\_black;
              if (\_\_w->\_M\_left) \_\_w->\_M\_left->\_M\_color = \_S\_rb\_tree\_black;
              \_Rb\_tree\_rotate\_right(\_\_x\_parent, \_\_root);
              break;
            \}
          \}
        if (\_\_x) \_\_x->\_M\_color = \_S\_rb\_tree\_black;
      \}
      return \_\_y;
    \}


捣乱 2013-9-29

[http://daoluan.ne](http://daoluan.net/)


