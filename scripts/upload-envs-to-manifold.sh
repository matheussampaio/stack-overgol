#! /bin/bash

set -e

(cat .env | awk '!/#/' | awk 'NF > 0') | while read line ; do
    echo $line
    manifold config set -t stack-overgol -r envs "$line"
done
