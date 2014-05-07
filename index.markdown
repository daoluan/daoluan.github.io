---
layout: name
title: 捣乱小子 - daoluan.net
keywords: 捣乱小子,捣乱,郑思愿,郑思愿daoluan,daoluan,daoluan.net
---

<img class='inset right' src='/images/daoluan.png' title='daoluan' width='120px' />

欢迎
=====
男，程序员，关注 c++，平时喜欢读书，写博客，吉他。

最近的文章
<p>
<ul class="compact recent">
{% for post in site.posts limit:3 %}
<li>
	<a href="{{ post.url }}" title="{{ post.title }}">{{ post.title }}</a>
	<span>{{ post.date | date_to_string }}</span>
</li>
{% endfor %}
</ul>
</p>

我有看过的书

<script type="text/javascript" src="http://www.douban.com/service/badge/daoluan/?selection=random&amp;picsize=medium&amp;hideself=on&amp;show=collection&amp;n=4&amp;hidelogo=on&amp;cat=book&amp;columns=4"></script>
