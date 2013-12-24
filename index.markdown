---
layout: name
title: Home
---

<img class='inset right' src='/images/daoluan.png' title='daoluan' width='120px' />

最近的文章：
=====
{% for post in site.categories.iem limit:3 %}
<ul class="compact recent">
<li>
	<a href="{{ post.url }}" title="{{ post.excerpt }}">{{ post.title }}</a>
	<span class="date">{{ post.date | date_to_string }}</span> 
</li>
</ul>
{% endfor %}

[weibo](http://weibo.com/daoluanxiaozi)  
[github](http://github.com/daoluan)  
[email](g.daoluan#gmail.com)  
