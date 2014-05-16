---
layout: name
title:  归档
top:    捣乱的个人网站
---

<h2>Categories:</h2>
<ul>
{% for category in site.categories %}
  <li><a href="#{{ category | first }}">{{ category | first }}</a></li>
{% endfor %}
</ul>

<h2>Articles by Category:</h2>
<ul>
{% for category in site.categories %}
  <li><a name="{{ category | first }}">{{ category | first }}</a>
    <ul>
    {% for posts in category %}
      {% for post in posts %}
        <li><a href="{{ post.url }}">{{ post.title }}</a></li>
      {% endfor %}
    {% endfor %}
    </ul>
  </li>
{% endfor %}
</ul>

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

