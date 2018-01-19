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

 - <a href="http://bibodeng.com/bibodeng/IT_birds/book.html">IT小小鸟外传</a>
 - <a href="http://daoluan.net/redis-source-note/">redis 源码日志</a>
