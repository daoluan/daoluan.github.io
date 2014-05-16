---
layout: name
title:  归档
top:    捣乱的个人网站
---

<div>
{% for category in page.categories %}
<span>{{ category | first }}</span>
{% endfor %}
</div>

<div>
<ul>
{% for post in site.posts %}
{% unless post.next %}
<h2>{{ post.date | date: '%Y' }} </h2>
{% else %}
{% capture year %}{{ post.date | date: '%Y' }}{% endcapture %}
{% capture nyear %}{{ post.next.date | date: '%Y' }}{% endcapture %}
{% if year != nyear %}
<h2>{{ post.date | date: '%Y' }}</h2>
{% endif %}
{% endunless %}
<li>{{ post.date | date:"%Y-%m-%d" }} &raquo; <a href="{{ post.url }}">{{ post.title }}</a></li>
{% endfor %}
</ul>
</div>

