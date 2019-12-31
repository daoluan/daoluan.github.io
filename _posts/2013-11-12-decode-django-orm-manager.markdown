---
title: 'Django 源码小剖: Django ORM 查询管理器'
date: 2013-11-12 15:45:26 Z
categories:
- 学习总结
tags:
- Django
- 源代码
author: daoluan
comments: true
layout: post
wordpress_id: 2048
---

### ORM 查询管理器


对于 ORM 定义: 对象关系映射, Object Relational Mapping, ORM, 是一种程序设计技术，用于实现面向对象编程语言里不同类型系统的数据之间的转换。从效果上说，它其实是创建了一个可在编程语言里使用的“虚拟对象数据库”。ORM 能大大简化并抽象数据库的操作.

假设 django 的一个工程中包含一个名为 Book 的模块(model), 在 views.py 的函数中可能会写出查询语句:

    
    # views.py
    def index(request):
        book_set = Book.objects.filter(id=1)
        或者
        book_set = Book.objects.all()
        ......


ORM 的作用就是这样, 并不需要写更复杂的 SQL 语句, 所有的的事情都被 ORM 代劳了.

上面中, Book 实际上是一个 Model 实例, 但先是从 Book.objects 开始说起. Book.objects 实际上是一个 Manager 类实例, 每个 Model 都会有一个, 用户的查询操作几乎是从这里开始的. 万万可以将 Model 实例理解为关系表中的一个表项数据, 而 Manager 实例可以理解数据库查询的入口.

实际上, 无论如何都在 Model 类的源码中找到任何 objects 属性的字眼, 因此它肯定是在某个时间点上增加的. 可以在 django.db.models.manager.py 中找到下面的函数:

    
    这个函数确保每一个 model 都有一个管理器 objects
    def ensure_default_manager(sender, **kwargs):
        ......
    
        if not getattr(cls, '_default_manager', None):
            # Create the default manager, if needed.
            try:
                cls._meta.get_field('objects')
                raise ValueError("Model %s must specify a custom Manager, because it has a field named 'objects'" % cls.__name__)
    
            except FieldDoesNotExist:
                pass
    
            """
            关键的一步, 将一个 Manager 实例挂钩到 cls.objects, 将 model.add_to_class() 方法罗列如下;
            def add_to_class(cls, name, value):
                if hasattr(value, 'contribute_to_class'):
                    value.contribute_to_class(cls, name)
                else:
                    setattr(cls, name, value)
    
            关键是 Manager 有 contribute_to_class() 方法, 由此看来, model.objects 并不是一个 Manager 实例, 实际上他是一个 ManagerDescriptor 实例.
            """
            cls.add_to_class('objects', Manager())
            cls._base_manager = cls.objects
    
        elif not getattr(cls, '_base_manager', None):
    
            default_mgr = cls._default_manager.__class__
    
            if (default_mgr is Manager or
                    getattr(default_mgr, "use_for_related_fields", False)):
                cls._base_manager = cls._default_manager
    
            else:
                # Default manager isn't a plain Manager class, or a suitable
                # replacement, so we walk up the base class hierarchy until we hit
                # something appropriate.
                for base_class in default_mgr.mro()[1:]:
                    if (base_class is Manager or
                            getattr(base_class, "use_for_related_fields", False)):
                        cls.add_to_class('_base_manager', base_class())
                        return


由此可以发现, Model.objects 在这个时候被添加了. 因此用户可以在代码中使用 Book.objects. **至于这个函数在何时被调用, 待后面会详述 django 内部的信号机制. 暂且你可以将其理解为在 django 服务器启动的时候, 这些会被自动调用就好了. **


### Manager 实现


Manager 保护技法

如果可以在 book_set = Book.objects.filter(id=1) 这一句上设置断点, 并 step into 的时候, 发现 Book.objects 实际上的实际上不是一个 Manager 实例, 而是一个 ManagerDescriptor 实例, 这是 django 特意为 Manager 做的一层包装. 为什么要这么做 ?


<blockquote>django 规定, 只有 Model 类可以使用 objects, Model 类实例不可以. 请注意区分类和类实例之间的区别.</blockquote>


**我认为这样做是有道理的.** Book.objects.filter(id=1) 返回的是 QuerySet 对象, 而 QuerySet 对象可以看成是 Model 实例的集合, 也就是 book_set 是 Model 实例的集合. 假使 「Model 类的实例可以使用 objects 属性」, 即「从一本书中查询书」这在语意上不通过. 只能是「从书的集合(Book)中查询书」.

所以 django 用 ManagerDescriptor 特意为 Manager 做的一层包装. 可以在 django.db.models.manager.py 中找到 ManagerDescriptor  的实现:

    
    class ManagerDescriptor(object):
        """
        很经典的掩饰, 为 Manager 特殊设定 Descriptor, 从而, 只能让类访问, 而不能让类的实例来访问. 具体是靠 __get__(self, instance, type=None) 方法来实现来的: 第二个参数 instance, 当 class.attr 的时候, instance 为 None; 当 obj.attr 的时候, instance 为 obj.
        """
        # This class ensures managers aren't accessible via model instances.
        # For example, Poll.objects works, but poll_obj.objects raises AttributeError.
    
        def __init__(self, manager):
            self.manager = manager
    
        def __get__(self, instance, type=None):
            if instance != None:
                raise AttributeError("Manager isn't accessible via %s instances" % type.__name__)
            return self.manager


所要详述的是 __get__() 函数. python 的语法里有修饰器(descriptor)这么一说, 而 python 的属性类型就是这么实现的. descriptor 实现 __get__(), __set__(), 接着将其添加到一个类中. 譬如下面的例子:

    
    class Celsius(object):
        def __init__(self, value=0.0):
            self.value = float(value)
        def __get__(self, instance, owner):
            print instance,owner
            return self.value
        def __set__(self, instance, value):
            print instance,value
            self.value = float(value)
    
    class Temperature(object):
        celsius = Celsius()
    
    t = Temperature()
    t.celsius
    Temperature.celsius


当对 descriptor 赋值的时候, 其本身 __set__ 会被调用, 取值的时候 __get__() 会被调用. __set__,__get__ 函数的 instance 参数即为类实例(所以, t.cellsius 调用 __get__() 的时候, instance 参数是 t, Temperature.celsius 调用 __get__() 的时候, instance 参数是 Temperature).

所以, 可以通过判断 instance 来判断调用者是否是类实例. 也就由此可以拒绝类实例的访问, 发现 ManagerDescriptor 就是这么实现的.


### 总结


Book.objects 实际上是一个 Manager, 实际上的实际上却是一个 ManagerDescriptor, 但真正起作用的还是 Manager, ManagerDescriptor 是修饰器, 是 django 的保护技法.

从 Manager 的实现来看, 它的多数函数会返回 QuerySet 对象, 而且透漏了一个重点: QuerySet 对象可以看成是 Model 实例的集合.

我已经在 github 备份了 Django 源码的注释: [Decode-Django](https://github.com/daoluan/Decode-Django), 有兴趣的童鞋 fork 吧.

Dylan 2013-9-24

[http://daoluan.net](http://daoluan.net/)
