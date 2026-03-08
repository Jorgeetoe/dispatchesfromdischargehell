#!/bin/bash
cd hugo
git submodule init
git submodule update
hugo --gc --minify
