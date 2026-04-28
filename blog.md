---
layout: page
title: Blog
permalink: /blog/
seo_title: Blog | Dispatches from Discharge Hell
description: Recent Dispatches from Discharge Hell posts and family-facing discharge planning guides.
sidebar_tagline: Making complex discharges make sense.
---

Use this page when you want the newest posts first. The [archives]({{ '/archives/' | relative_url }}) are still there when you want the full date-ordered list.

<div class="blog-index" aria-label="Latest blog posts">
  {% assign visible_posts = site.posts | where_exp: 'post', 'post.hidden != true' %}
  {% for post in visible_posts limit: 30 %}
    <article class="blog-index-item">
      <p class="blog-index-meta">{{ post.date | date: '%b %-d, %Y' }}</p>
      <h2><a href="{{ post.url | relative_url }}">{{ post.title }}</a></h2>
      <p class="blog-index-summary">{% include post-summary.html max_length=180 %}</p>
    </article>
  {% endfor %}
</div>
