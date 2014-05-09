---
author: daoluan
comments: true
date: 2013-07-23 12:36:43+00:00
layout: post
slug: csrf-attack
title: CSRF 攻击
wordpress_id: 1799
categories:
- 互联网
- 学习总结
tags:
- CSRF 攻击
---

在 Django 的表单（或 POST）中硬性添加 **{% raw %}{% csrf_token %}{% endraw %}** 标记如下，否则在提交表单的时候会出错，目的就是为了防止 CSRF 攻击：

    
    <form action="/summit_question" method="pos)t"> 
    。。。。。。
    </form>
    
    <!-- error -->
    Forbidden (403)
    CSRF verification failed. Request aborted.


CSRF 全称是 Cross-site request forgery，即跨站点请求伪造。当恶意的网站被访问时，会产生伪造的请求发送给服务器，伪造请求中可能存留了用户的 cookie，服务器也无法区分请求真伪，因此数据被提交甚至修改，给用户带来损失。

小明如果遭受 CSRF 攻击严重的有如下现象，情景假设：

小明早上起来登录了 shopping.com 购物网站；

在登录后同时在新的标签中打开了一个恶意（malicious）网站，并点击了里面的一个按钮或者图片；

回到 shopping.com 的时候发现，他账户里的钱少了 ￥1000。

上面的只是情景假设，一般的购物网站不会这样单纯。试着看看里面它是如何工作的：

小明成功登录了 shopping.com 网站，他的浏览器保存了浏览器产生的一个 cookie，注意此 cookie 中保存了某些登录信息或者授权信息。同时我们假设：shopping.com 服务器向账户 「123456」转账 ￥1000 的接口是：

    
    http://shopping.cm/Transfer.html?toAccount=123456&money=1000
    
    产生的 HTTP 请求可能是：
    
    GET http://shopping.cm/Transfer.html?toAccount=123456&money=1000
    ...
    Cookie:XXXXXXXXXX
    ...


未名攻击者特地写了个带图片的链接，可以是下面的形式：

    
    <a href="daoluan.net"><img height="185" width="185" alt="" src="http://shopping.cm/Transfer.html?toAccount=123456&money=1000"></a>


小明傻乎乎的点击打开，于是浏览器尝试装载图片的时候，同时提交了小明的 cookie。服务器收到此请求，验证 cookie 正确后，于是修改了数据，即给账户「123456」转账 ￥1000.没错，在装载图片过程中会产生上面形式的 HTTP 请求。

电商 shopping.com 不会简单的发送 HTTP GET 请求转账，HTTP GET 本身基因就决定他必须把参数暴露在链接中。那采用安全点的 POST 如何？编写一个 method 为 POST 的表单就达到目标。以上的情况严重点，CSRF 稍微好一点的情景是通由小明在某个站点上的登录，提交一个评论。

有两种方法可以防止 CSRF：



	
  * 检测 HTTP header 中的 referer 字段。服务器可以查看 referer 是否为自己的站点，如果不是，则拒绝服务。

	
  * 在 form 表单中嵌入隐藏域（tpye="hidden"），当表单被提交的时候检测隐藏域的值。隐藏域的值可以是用 md5 hash 产生的值，表单的一些信息，或是服务器上的一个密码。另一个可行的方案是服务器给每一个表单产生一次性的串。Django 就是用这种方法。表单提交后，服务器检测一下是不是有效的值。

	
  * 两者的结合。


第一种方法很容易攻破，修改 HTTP header 中的 referer 字段就好了，另外据说用户可以设置浏览器忽略 referer；第二种方法服务器数据库或文件读写方面会添加点压力，而且要设定隐藏域值的过期时间。综合来看，第二种方法更可取。

CSRF 攻击通常会调用 JavaScript 自动提交跨站表单，然而，不用 JavaScript 一个恶意的站点也能让用户向另一个站点提交表单，因为表单是可以隐藏的，并且按钮可以伪装成一个链接。 说白了，**HTTP 是无状态协议，对于前一个请求和后一个请求，web 服务器无法区分是否来自同一个浏览器（用户）。**现在还有很多网站是这么做的：在服务器中使用 session 保存会话，结合着客户端浏览器的 cookie，简单来说客户端浏览器保存的 cookie 和 服务器中的 session 存在一一对应的关系，于是只要有第三方获取了客户端浏览器保存的 cookie 值，接下来的攻击就好办了。

最近在威信公众平台上做了一个学校图书馆应用，可以搜书和查询用户在图书馆的借阅情况，和学校沟通开放接口这个应该是不可能的了，这个其实就是类似 CSRF 的攻击。如果华师的同学，可以关注 betalife 这个公众帐号。

参考：[http://www.squarefree.com/securitytips/web-developers.html#CSRF](http://www.squarefree.com/securitytips/web-developers.html#CSRF)

捣乱 2013-07-23

http://daoluan.net/blog
