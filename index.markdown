---
layout: name
title: Home

<img class='inset right' src='/images/mark_reid.jpg' title='Mark Reid' alt='Photo of Mark Reid drinking a coffee' width='120px' />

Blogs
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

