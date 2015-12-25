#!/bin/bash

 wget http://maltparser.org/dist/maltparser-1.8.tar.gz
 tar -zxvf maltparser-1.8.tar.gz 
 mv maltparser-1.8 malt
 mv malt/maltparser-1.8.jar malt/malt.jar
 wget -O MaltEval.zip "https://drive.google.com/uc?id=0B1KaZVnBJE8_QnhqNE52T2FZWVE&export=download"
 unzip MaltEval.zip
 mv dist-20141005 meval
 rm -f MaltEval.zip 
 make -C ./libsvmc
