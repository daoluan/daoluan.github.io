---
layout: name
title: 捣乱小子 - daoluan.net
keywords: 捣乱小子,捣乱,郑思愿,郑思愿daoluan,daoluan,daoluan.net
---

<img class='inset right' src='/images/daoluan.png' title='daoluan' width='120px' />

欢迎
=====
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
 - [Redis 源码日志](http://daoluan.net/redis-source-note/), [Redis 源码日志-极客学院Wiki](http://wiki.jikexueyuan.com/project/redis/)

赞助：
<img src='/images/payment_code_zhifubao.jpeg' title='daoluan' width='120px' />
<img src='/images/payment_code_wechat.jpeg' title='daoluan' width='120px' />
