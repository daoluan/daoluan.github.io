#!/bin/sh

echo -n "input title:"
read title

echo -n "input title in en:"
read title_in_en

echo -n "input categories:"
read categories

echo -n "input tags:"
read tags

date=`date +%Y-%m-%d`
filename=`echo -n ./_posts/${date}-${title_in_en}.md`

echo 
echo "generate new post..."
echo "---" >> $filename
echo "author: daoluan" >> $filename
echo "layout: post" >> $filename
echo "title: $title" >> $filename
echo "categories:" >> $filename
echo "- $categories" >> $filename
echo "tags:" >> $filename
echo "- $tags" >> $filename
echo "---" >> $filename
echo "" >> $filename
echo "" >> $filename
echo "Enjoy writing!"

