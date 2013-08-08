#!/bin/bash

set -e

git add .
git commit -m 'Update'

wget http://dygraphs.com/dygraph-combined.js -O dygraph/dygraph-combined.js

JVECTORMAP_VERSION='1.2.2'
filename="jquery-jvectormap-${JVECTORMAP_VERSION}.zip"

rm -rf temp
mkdir temp

wget http://jvectormap.com/binary/${filename} -O temp/${filename}
unzip temp/${filename} -d temp/
mv temp/jquery-jvectormap-${JVECTORMAP_VERSION}.css jvectormap/jquery-jvectormap.css
mv temp/jquery-jvectormap-${JVECTORMAP_VERSION}.min.js jvectormap/jquery-jvectormap.js

rm -rf temp

wget http://jvectormap.com/js/jquery-jvectormap-world-mill-en.js \
    -O jvectormap/jquery-jvectormap-world-mill-en.js

JQUERY_VERSION='1.10.0'
wget http://code.jquery.com/jquery-${JQUERY_VERSION}.min.js -O jvectormap/jquery.js

git add .
git commit -m 'Update'


