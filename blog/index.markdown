---
layout: name
title: Dylan - daoluan.net
keywords: Dylan,Dylan,郑思愿,郑思愿daoluan,daoluan,daoluan.net

---
<img class='inset right' src='/images/daoluan.png' title='daoluan' width='120px' />

# 欢迎

最近的文章
<p>
<ul class="compact recent">
{% for post in site.posts limit:5 %}
<li>
<a href="{{ post.url }}" title="{{ post.title }}">{{ post.title }}</a>
<span>{{ post.date | date_to_string }}</span>
</li>
{% endfor %}
</ul>
</p>

作品

 - [IT 小小鸟外传](http://bibodeng.com/bibodeng/IT_birds/book.html)
 - [Redis 源码日志](http://daoluan.net/redis-source-notes/)(会保持更新), ~~[Redis 源码日志-极客学院Wiki](http://wiki.jikexueyuan.com/project/redis/)~~
 - [理解 STL](http://daoluan.net/cplusplus/%E5%AD%A6%E4%B9%A0%E6%80%BB%E7%BB%93/%E7%AE%97%E6%B3%95/2012/12/01/confidential-stl.html)
 - [理解 Django](https://github.com/daoluan/decode-Django)
 - [理解 memcache](https://github.com/daoluan/decode-memcached)

赞助(主要用作本站维护使用)：

<img src='/images/payment_code_zhifubao.jpeg' title='支付宝支付' width='120px' />
<img src='/images/payment_code_wechat.jpeg' title='微信支付' width='120px' />
