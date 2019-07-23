---
title: 初探单点登录 SSO
date: 2014-03-29 15:12:53 Z
categories:
- 互联网
- 学习总结
- 计算机系统
tags:
- SSO
- 京东单点登录
- 单点登录
- 淘宝网单点登录
author: daoluan
comments: false
layout: post
wordpress_id: 2285
---

### 单点登录


单点登录（Single sign-on，SSO）是一种访问控制，在多个软件应用中，用户只需登录其中一个应用，就可以成功访问其他应用；同样，用户只需注销其中一个应用，就可以成功注销其他应用。

当一个公司产品线越来越复杂，做的东西越来越多，考虑到用户的便利性和业务的交集，单点登录也就变得越来越必然。譬如，阿里巴巴中的淘宝网，天猫，聚划算和一淘，考虑下面的场景：我们用户登录淘宝网购物，紧接着朋友打电话说出去玩，于是打开聚划算的时候你会发现，你已经登了聚划算！可能这些细节都被大多数人忽略了（被谁给惯坏了），但如果要让用户再次手动登录聚划算，用户体验可想而知。这种便利性就是单点登录所带来的。

在单点登录中，认证系统会为每一个应用分配一把钥匙，也就是说有了这把钥匙，账号密码的输入就可以免去了。这把钥匙就藏在浏览器的 cookie 中。应用获取钥匙有两种方法：

一，成功登录应用A 后，认证系统为应用A 分配一把钥匙；同时，应用A 凭借自己已经成功登录，帮其他应用代领钥匙。下一次访问应用B 的时候，应用B 就能成功免登录了。

二，这里认证系统的域名是应用A 的子域名，即如果应用A 是 example.com,认证系统可能是个 passport.example.com。当成功登录应用A 后，认证系统为应用A 分配一把钥匙；下一次访问应用B 的时候，web 页面被重定向到认证系统，因为认证系统的域名是应用A 的子域名，所以应用A 的钥匙，即 cookie 被带上，从而用户的访问得到了信任，认证系统为应用B 分配钥匙，页面被重定向到应用B。

接下来会对淘宝网和京东商城的网站进行单点登录实例分析。


### 淘宝网的单点登录策略


来看看淘宝网做法。

登录了 taobao.com 后，下面是所产生的 cookie，也就是说认证系统已经为应用taobao.com 分配了钥匙，但这里并没有 etao.com 或者 tmall.com 的 cookie，认证系统还未为他们分配钥匙。

[![taobao_cookie](http://daoluan.net/images/blog/2014/03/taobao_cookie.png)](http://daoluan.net/images/blog/2014/03/taobao_cookie.png)

下一步我们尝试去访问 etao.com：

[![etao_network](http://daoluan.net/images/blog/2014/03/etao_network.png)](http://daoluan.net/images/blog/2014/03/etao_network.png)

etao.com 被重定向到了 www.etao.com；访问 www.etao.com 被重定向到 http://jump.taobao.com/，下面是 response HTTP：

    
    HTTP/1.1 302 Moved Temporarily
    Server: Tengine
    Date: Sat, 29 Mar 2014 14:29:41 GMT
    Content-Type: text/html
    Transfer-Encoding: chunked
    Connection: keep-alive
    Location: http://jump.taobao.com/jump?target=http%3A%2F%2Fwww.etao.com%2F%3Ftbpm%3D20140329


浏览器会继续访问 http://jump.taobao.com/jump?target=http%3A%2F%2Fwww.etao.com%2F%3Ftbpm%3D20140329,下面是 request HTTP，这里访问带上了应用taobao.com 的钥匙，即 cookie，**网站后台会验证应用taobao.com 的钥匙：**

    
    GET /jump?target=http%3A%2F%2Fwww.etao.com%2F%3Ftbpm%3D20140329 HTTP/1.1
    Host: jump.taobao.com
    Connection: keep-alive
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
    User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.154 Safari/537.36
    Accept-Encoding: gzip,deflate,sdch
    Accept-Language: zh-CN,zh;q=0.8,en;q=0.6
    Cookie: ...


认证成功，看来钥匙是有效的，又产生一个重定向，下面是和上面对应的 response HTTP：

    
    HTTP/1.1 302 Found
    Date: Sat, 29 Mar 2014 14:29:41 GMT
    Content-Type: text/html
    Content-Length: 260
    Connection: close
    Set-Cookie: _tb_token_=AtWQpv7iedma;domain=.taobao.com;Path=/;HttpOnly
    P3P: CP='CURa ADMa DEVa PSAo PSDo OUR BUS UNI PUR INT DEM STA PRE COM NAV OTC NOI DSP COR'
    Location: http://pass.etao.com/add?uc3=nk2=Dkjr489jrew%3D;id2=Vyu3rko%2FyYdG;vt3=F8dHqR4J6Q2W7ouKdi8%3D;lg2=WqG3DMC9VAQiUQ%3D%3D&lgc=XXXXXX&tracknick=XXXXXX&_l_g_=Ug%3D%3D&cookie1=U7lSAZ5WionEzYGt3e34IvM%2BhHRTBL5Y%2BYTf7E22Ixo%3D&cookie2=007485c12ac6179b824c7656627e806c&cookie17=Vyu3rko%2FyYdG&t=4376b50842a95fbd0464fc1d58fe84c5&unb=479940688&_nk_=XXXXXX&uc1=cookie15=V32FPkk%2Fw0dUvg%3D%3D&_tb_token_=AtWQpv7iedma&target=http%3A%2F%2Fwww.etao.com%2F%3Ftbpm%3D20140329&pacc=_7LwGS9DwiA3O_Iq8iAaMQ==&opi=183.62.180.11&tmsc=1396103381332051


接下来浏览器访问 http://pass.etao.com/add?.......，下面 response HTTP：

    
    HTTP/1.1 302 Found
    Date: Sat, 29 Mar 2014 14:29:41 GMT
    Content-Type: text/html
    Content-Length: 260
    Connection: close
    P3P: CP='CURa ADMa DEVa PSAo PSDo OUR BUS UNI PUR INT DEM STA PRE COM NAV OTC NOI DSP COR'
    Set-Cookie: uc3=nk2=Dkjr489jrew%3D&id2=Vyu3rko%2FyYdG&vt3=F8dHqR4J6Q2W7ouKdi8%3D&lg2=WqG3DMC9VAQiUQ%3D%3D;domain=.etao.com;Path=/
    Set-Cookie: ...;domain=.etao.com;Path=/
    Set-Cookie: ...;domain=.etao.com;Path=/
    Set-Cookie: ...;domain=.etao.com;Path=/
    Set-Cookie: ...
    Set-Cookie: ...
    Set-Cookie: ...
    ...
    Location: http://www.etao.com/?tbpm=20140329


「Set-Cookie」意味着应用etao.com 拿到了认证系统的钥匙，耶斯！

[![etao_cookie](http://daoluan.net/images/blog/2014/03/etao_cookie.png)](http://daoluan.net/images/blog/2014/03/etao_cookie.png)


### 京东商城单点登录策略


来看看京东商城的做法

[![jd_cookie](http://daoluan.net/images/blog/2014/03/jd_cookie.png)](http://daoluan.net/images/blog/2014/03/jd_cookie.png)

登录 jd.com 后发现，它已经给所有的应用代领了钥匙！这里利用了前端里面的 jsonp，对于跨域的问题，jsonp 驾轻就熟。

成功登录 jd.com，会跳转到 jd.com，里面有一小段 js 代码发起了 jsonp 请求：

    
    $.ajax({
        url: ("https:" == document.location.protocol ? "https://" : "http://") + "passport." + pageConfig.FN_getDomain() + "/new/helloService.ashx?m=ls",
        dataType: "jsonp",
        scriptCharset: "gb2312",
        success: function(a) {
                a && a.info && $("#loginbar").html(a.info), a && a.sso && $.each(a.sso, function() {
                    $.getJSON(this)
                })
        }
    })


ajax get 到数据自动调用预设值的回调函数。jsonp 返回的数据是：

    
    jsonp1396084410330({"sso":[
         "http://sso.jd.com/setCookie?t=sso.360buy.com&callback=?",
         "http://sso.jd.com/setCookie?t=sso.wangyin.com&callback=?",
         "http://sso.jd.com/setCookie?t=sso.360top.com&callback=?",
         "http://sso.jd.com/setCookie?t=sso.minitiao.com&callback=?",
         "http://sso.jd.com/setCookie?t=sso.jcloud.com&callback=?"],
         "info":"您好，买东西别坑爹！<a href="http://passport.jd.com/uc/login?ltype=logout" class="link-logout">[退出]</a>"})


回调函数对 a.sso 中每一个连接执行 getJSON()。注：使用 jquery 的 getJSON() 进行跨域读取数据，实际上 getJSON() 方式的根本原理和 ajax 使用 jsonp 的方式一样。

[![jquery jsonp 请求](http://daoluan.net/images/blog/2014/03/jd_jsonp_network_01.png)](http://daoluan.net/images/blog/2014/03/jd_jsonp_network_01.png) jquery jsonp 请求

[![jquery jsonp 请求产生的重定向](http://daoluan.net/images/blog/2014/03/jd_jsonp_network_011.png)](http://daoluan.net/images/blog/2014/03/jd_jsonp_network_011.png) jquery jsonp 请求产生的重定向

以第一个参数为例，所产生的 request HTTP：

    
    GET /setCookie?t=sso.360buy.com&callback=jsonp1396084410335&_=1396084411190 HTTP/1.1
    Host: sso.jd.com
    Connection: keep-alive
    Accept: */*
    User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.154 Safari/537.36
    Referer: http://www.jd.com/
    Accept-Encoding: gzip,deflate,sdch
    Accept-Language: zh-CN,zh;q=0.8,en;q=0.6
    Cookie: ...


结果产生一个重定向到 http://sso.360buy.com 的响应，与上面对应的 response HTTP：

    
    HTTP/1.1 302 Moved Temporarily
    Server: nginx
    Date: Sat, 29 Mar 2014 09:13:26 GMT
    pragma: no-cache
    cache-control: max-age=86400
    Location: http://sso.360buy.com/sign?c=0f5882246bae6fc065e387995680f4d73a03c448a244d27e328ae7abcd3c7fd7fa629605ac516c1903e014b45e906a7bc7bf5d7c237752f85709d12fd9cbe5a81c2602f684d352311de39612555d2fc2b4aa6fffca26d5a7e37e61e9a1b9e7e184cf8b335982c36b39944faf29cb1b61dd6b6a8461000c7661fc881a5daa89ddaaecf062d2e84b96e958534f5a407524596dcce400299487e87060d4ac55d454c36804deca3fd670adca3902d7e05d778fbc135c9a6e491b44ed5954337ac38f5b61e99934a0411b9af695ebbb7f75a4e69da4c24f1b3137ef6cc916af3c62238ee2b3c90f762d9b162239d634928f027585ab13c1e031861fb41a6a83ec2d1fec8b00389b91e5ab5c5db3961f60949c230d5280898d62c9f66f76058c35af78b1781d266ee548bd&callback=jsonp1396084410335&_=1396084411190&t=1396084406861&pin=XXXXXX&unick=%E4%B9%B0%E4%B8%9C%E8%A5%BF%E5%88%AB%E5%9D%91%E7%88%B9
    Content-Length: 0
    Expires: Sun, 30 Mar 2014 09:13:26 GMT
    Connection: Keep-alive
    Keep-Alive: timeout=15, max=100


再次产生新的请求，请求目标为 http://sso.360buy.com：

    
    GET /sign?c=0f5882246bae6fc065e387995680f4d73a03c448a244d27e328ae7abcd3c7fd7fa629605ac516c1903e014b45e906a7bc7bf5d7c237752f85709d12fd9cbe5a81c2602f684d352311de39612555d2fc2b4aa6fffca26d5a7e37e61e9a1b9e7e184cf8b335982c36b39944faf29cb1b61dd6b6a8461000c7661fc881a5daa89ddaaecf062d2e84b96e958534f5a407524596dcce400299487e87060d4ac55d454c36804deca3fd670adca3902d7e05d778fbc135c9a6e491b44ed5954337ac38f5b61e99934a0411b9af695ebbb7f75a4e69da4c24f1b3137ef6cc916af3c62238ee2b3c90f762d9b162239d634928f027585ab13c1e031861fb41a6a83ec2d1fec8b00389b91e5ab5c5db3961f60949c230d5280898d62c9f66f76058c35af78b1781d266ee548bd&callback=jsonp1396084410335&_=1396084411190&t=1396084406861&pin=XXXXXX&unick=%E4%B9%B0%E4%B8%9C%E8%A5%BF%E5%88%AB%E5%9D%91%E7%88%B9 HTTP/1.1
    Host: sso.360buy.com
    Connection: keep-alive
    Accept: */*
    User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.154 Safari/537.36
    Referer: http://www.jd.com/
    Accept-Encoding: gzip,deflate,sdch
    Accept-Language: zh-CN,zh;q=0.8,en;q=0.6


response HTTP 中有 「Set-Cookie」说明已经拿到认证系统的钥匙了：

    
    HTTP/1.1 200 OK
    Server: nginx
    Date: Sat, 29 Mar 2014 09:13:27 GMT
    Content-Type: text/javascript;charset=UTF-8
    pragma: no-cache
    cache-control: max-age=86400
    P3P: CP="CURa ADMa DEVa PSAo PSDo OUR BUS UNI PUR INT DEM STA PRE COM NAV OTC NOI DSP COR"
    SET-COOKIE: ceshi3.com=EA0B41EDE28DC567542D0191B48C74F35CD76AAEBADA867F4879AA3F02B4EA559D6E537ED0BEB4CCD417D4A434A7CC86C30CBA8775BCA96C36AB067034D0E057F9ED0297AFA566954A10E03DFF292089736A8B79554C32CB8FCFAA2F042F547DACCD30BAC81A9815083C9F1071B5B8382968A5A7E82EC0172E6AEE15930A6AA47C6875A1CDEE90118515ED0022909DAE;path=/;domain=.360buy.com;httponly
    Set-Cookie: pin=XXXXXX; Domain=.360buy.com; Path=/
    Set-Cookie: unick=%E4%B9%B0%E4%B8%9C%E8%A5%BF%E5%88%AB%E5%9D%91%E7%88%B9; Domain=.360buy.com; Path=/
    Content-Length: 43
    Expires: Sun, 30 Mar 2014 09:13:27 GMT
    Connection: Keep-alive
    Keep-Alive: timeout=15, max=100


其他应用类似，这里只举例 360buy.com.接着我试图访问 http://360buy.com：

    
    GET / HTTP/1.1
    Host: 360buy.com
    Connection: keep-alive
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
    User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.154 Safari/537.36
    Accept-Encoding: gzip,deflate,sdch
    Accept-Language: zh-CN,zh;q=0.8,en;q=0.6
    // 下面提交的 cookie，即是 360buy.com 的钥匙
    Cookie: ceshi3.com=EA0B41EDE28DC567542D0191B48C74F35CD76AAEBADA867F4879AA3F02B4EA559D6E537ED0BEB4CCD417D4A434A7CC86C30CBA8775BCA96C36AB067034D0E057F9ED0297AFA566954A10E03DFF292089736A8B79554C32CB8FCFAA2F042F547DACCD30BAC81A9815083C9F1071B5B8382968A5A7E82EC0172E6AEE15930A6AA47C6875A1CDEE90118515ED0022909DAE; pin=XXXXXX; unick=%E4%B9%B0%E4%B8%9C%E8%A5%BF%E5%88%AB%E5%9D%91%E7%88%B9
    
    HTTP/1.1 200 OK
    Server: JDWS/1.0.0
    Date: Sat, 29 Mar 2014 11:24:37 GMT
    Content-Type: text/html
    Last-Modified: Wed, 26 Mar 2014 11:54:10 GMT
    Transfer-Encoding: chunked
    Vary: Accept-Encoding
    Expires: Sat, 29 Mar 2014 11:24:37 GMT
    Cache-Control: max-age=0
    Content-Encoding: gzip
    Connection: Keep-alive
    Keep-Alive: timeout=15, max=100


可见访问 http://360buy.com 的时候，并没有特地跑去认证系统索要钥匙，只凭借之前访问 jd.com 时 getJSON() 留下的 cookie。

![360buy_com_network](http://daoluan.net/images/blog/2014/03/360buy_com_network.png)

关于单点登录的问题，还有待更深入讨论。我只是用一些抓包工具和网站的前端代码来猜测单点登录策略如何，后台会是更复杂的技术，譬如分布式存储等。对于上面的两个案例，如果你了解淘宝或者京东商城的单点登录的具体方法，不吝赐教。

上面所说，单点登录所带来的用户体验可能被用户忽略了。说到底用户都是给惯坏了，微信5 出来后被骂几条街，还不是习惯了之前的操作，又要去探索新版本的用法，太懒；再说到底，用户是上帝啊，就这么惯着吧！

—-

捣乱 2014-3-29

[http://daoluan.net](http://daoluan.net/)
