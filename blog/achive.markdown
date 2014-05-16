---
layout: name
title:  归档
top:    捣乱的个人网站
---

<div>
<h3>标签</h3>
<ul>
{% for tag in site.tags %}
  <span>{{ tag | first }}</span>.
{% endfor %}
</ul>
</div>

<div>
<h3>分类</h3>
<ul>
{% for category in site.categories %}
  <span>{{ category | first }}</span>.
  {% for post in category.last %}
    <span><a href="{{ post.url }}">{{ post.title }}</a></span>.
  {% endfor %}
  <br>
{% endfor %}
</li>
</ul>
</div>

<div>
<ul>
{% for post in site.posts %}
{% unless post.next %}
<h3>{{ post.date | date: '%Y' }} </h3>
{% else %}
{% capture year %}{{ post.date | date: '%Y' }}{% endcapture %}
{% capture nyear %}{{ post.next.date | date: '%Y' }}{% endcapture %}
{% if year != nyear %}
<h3>{{ post.date | date: '%Y' }}</h3>
{% endif %}
{% endunless %}
<li>{{ post.date | date:"%Y-%m-%d" }} &raquo; <a href="{{ post.url }}">{{ post.title }}</a></li>
{% endfor %}
</ul>
</div>

