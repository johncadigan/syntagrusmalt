#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on Nov 1, 2015

@author: john
'''
import codecs
import os
import xml.sax
import sys

import re
import subprocess
from collections import defaultdict
from time import sleep

MAX_SENTS = 1000000000
WRITE_GRAMMAR_TAGS = False
LOWERCASE = True


class SynTagRus2MaltHandler(xml.sax.handler.ContentHandler):
    def __init__(self, out_destination):
        self.__out = out_destination
        self.__in_word = False
        self.__word_features = {}

    def characters(self, content):
        if self.__in_word:
            if 'FORM' not in self.__word_features:
                self.__word_features['FORM'] = content
            else:
                self.__word_features['FORM'] += content

    def startDocument(self):
        pass

    def endDocument(self):
        pass

    def startElement(self, tag, in_attrs):
        if tag == 'W':
            self.__in_word = True
            self.__word_features = {attr_name: in_attrs[attr_name] for attr_name in in_attrs._attrs}
            if self.__word_features['DOM'] == '_root':
                self.__word_features['DOM'] = '0'

    def endElement(self, tag):
        if tag == 'S':
            self.__out.write('\n')
        if tag == 'W':
            self.__flush_word()
        self.__in_word = False

    def __flush_word(self):
        self.__word_features['FEAT'] = syntagrus2rusc.convert_grammar(self.__word_features.get('FEAT', '-'))
        for key in self.__word_features:
            if LOWERCASE:
                self.__word_features[key] = self.__word_features[key].lower()
            if key == 'FEAT' and not WRITE_GRAMMAR_TAGS:
                self.__word_features[key] = self.__word_features[key].split(',')[0]

        # this particular order is for compatibility for Malt (it ignores lemmas, but we may not)
        string_to_flush = '\t'.join([self.__word_features.get('FORM', '-'),
                                     self.__word_features.get('FEAT', '-'), #+ self.__word_features.get('LEMMA', '-'),
                                     self.__word_features.get('DOM', '-'),
                                     self.__word_features.get('LINK', '_'),
                                     ])
        print >>self.__out, string_to_flush



class RuscorporaSynTagRus2CONLL(xml.sax.handler.ContentHandler):
    def __init__(self, out_destination):
        self.__out = out_destination
        self.__in_word = False
        self.__word_features = {}
        self.sentences_number = 0
        s = u"(несов|страд|сов|изъяв|прев|кр|пов|неправ|нестанд|сл|неод)"
        self.redux = re.compile(s, re.UNICODE)

    def characters(self, content):
        if self.__in_word:
            if 'FORM' not in self.__word_features:
                self.__word_features['FORM'] = content
            else:
                self.__word_features['FORM'] += content

    def startDocument(self):
        pass

    def endDocument(self):
        pass

    def startElement(self, tag, in_attrs):
        if tag == 'W':
            self.__in_word = True
            self.__word_features = {attr_name: in_attrs[attr_name] for attr_name in in_attrs._attrs}
            if self.__word_features['DOM'] == '_root':
                self.__word_features['DOM'] = '0'
        #if tag == 'W':
        #    self.__in_word = True
        #if tag == '':
        #    self.__word_features = {attr_name: in_attrs[attr_name] for attr_name in in_attrs._attrs}
        #    if self.__word_features['dom'] == '_root':
        #        self.__word_features['dom'] = '0'
    
    def map_to_key(self, wfs, new_key, wv, mapping):
        wv[new_key] = "_"
        for k in mapping.keys():
            if k in wfs: wv[new_key] = mapping[k]
        return wv

    def endElement(self, tag):
        if tag == 'S':
            self.__out.write('\n')
            self.sentences_number += 1
        if tag == 'W':
            self.__flush_word()
            self.__in_word = False

    def __flush_word(self):
        if self.sentences_number > MAX_SENTS:
            return
        for key in self.__word_features:
            if LOWERCASE:
                self.__word_features[key] = self.__word_features[key].lower()
            if key == 'FEAT' and not WRITE_GRAMMAR_TAGS:
                self.__word_features[key] = self.__word_features[key].split(',')[0]
        lemma = "_"
        TABS = u"{id}\t{form}\t{lemma}\t{cpos}\t{pos}\t{case}|{gen}|{num}|{tense}\t{head}\t{deprel}"
        
        wv = {"id" : self.__word_features.get("ID"),"head": self.__word_features.get('DOM', '-'),"deprel" : self.__word_features.get("LINK", "_"), "lemma": "_", "form": self.__word_features.get('FORM', '-')}
        wf = self.__word_features.get('FEAT', '-')
        wfs = self.redux.sub(u"", wf.lower()).split(u" ")
        
       
        cases = {
    u'им': 'nom',
    u'род': 'gen',
    u'дат': 'dat', # 'dat2',
    u'вин': 'acc',
    u'твор': 'ins',
    u'пр': 'loc',
    u'парт': 'gen', # 'acc2',
    u'местн': 'loc',
    u'зв': 'voc', # 'adnum'
        }
        wv = self.map_to_key(wfs, "case", wv, cases)
        #case
        genders = {
        # gender
    u'муж': 'm',
    u'жен': 'f',
    u'муж-жен': 'mf', #works for both
    u'сред': 'n',
        }
        wv = self.map_to_key(wfs, "gen", wv, genders)
        # number
        numbers = {
    u'ед': 'sg',
    u'мн': 'pl',
        }
        wv = self.map_to_key(wfs, "num", wv, numbers)
            # verb form
        times = {
            u'непрош': 'pres',
            u'наст': 'pres',
            u'прош': 'past',
        }
        wv = self.map_to_key(wfs, "tense", wv, times)   
        dform = {
    u's': 'n',
    u'a': 'a',
    u'v': 'v',
    u'adv': 'adv',
    u'num': 'num',
    u'pr': 'pr',
    u'com': 'com',
    u'conj': 'conj',
    u'part': 'part',
    u'p': 'p',
    u'intj': 'intj',
    u'nid': 'nid',
        }
        wv = self.map_to_key(wfs, "pos", wv, dform) 
        wv = self.map_to_key(wfs, "cpos", wv, dform)
        wv["lemma"]=self.__word_features.get('LEMMA', '-') #v1.3
        string_to_flush = TABS.format(**wv)
        print >>self.__out, string_to_flush


class RuscorporaSynTagRus2MaltInputHandler(xml.sax.handler.ContentHandler):
    def __init__(self, out_destination):
        self.__out = out_destination
        self.__in_word = False
        self.__word_features = {}
        self.sentences_number = 0

    def characters(self, content):
        if self.__in_word:
            if 'FORM' not in self.__word_features:
                self.__word_features['FORM'] = content
            else:
                self.__word_features['FORM'] += content

    def startDocument(self):
        pass

    def endDocument(self):
        pass

    def startElement(self, tag, in_attrs):
        if tag == 'W':
            self.__in_word = True
            self.__word_features = {attr_name: in_attrs[attr_name] for attr_name in in_attrs._attrs}
            if self.__word_features['DOM'] == '_root':
                self.__word_features['DOM'] = '0'
        #if tag == 'W':
        #    self.__in_word = True
        #if tag == '':
        #    self.__word_features = {attr_name: in_attrs[attr_name] for attr_name in in_attrs._attrs}
        #    if self.__word_features['dom'] == '_root':
        #        self.__word_features['dom'] = '0'

    def endElement(self, tag):
        if tag == 'S':
            self.__out.write('\n')
            self.sentences_number += 1
        if tag == 'W':
            self.__flush_word()
            self.__in_word = False

    def __flush_word(self):
        if self.sentences_number > MAX_SENTS:
            return
        for key in self.__word_features:
            if LOWERCASE:
                self.__word_features[key] = self.__word_features[key].lower()
            if key == 'FEAT' and not WRITE_GRAMMAR_TAGS:
                self.__word_features[key] = self.__word_features[key].split(',')[0]

        string_to_flush = '\t'.join([self.__word_features.get('FORM', '-'),
                                    self.__word_features.get('FEAT', '-'),
                                    ])
        print >>self.__out, string_to_flush

def convert(in_source, out_destination, in_format):
    out = out_destination
    if isinstance(out_destination, str):
        out = codecs.getwriter('utf-8')(open(out_destination, 'wb'))
    if in_format == 'syntagrus':
        handler = SynTagRus2MaltHandler(out)
    elif in_format == 'ruscorpora_syntagrus':
        handler = RuscorporaSynTagRus2CONLL(out)
    else:
        handler = RuscorporaSynTagRus2MaltInputHandler(out)
    parser = xml.sax.make_parser()
    parser.setContentHandler(handler)
    parser.parse(in_source)


def convert_directory(in_texts_root, in_result_root, in_format):
    if not os.path.isdir(in_result_root):
        os.makedirs(in_result_root)
    for root, dirs, files in os.walk(in_texts_root, followlinks=True):
        local_root = root[len(in_texts_root) + 1:]
        result_root = os.path.join(in_result_root, local_root)
        if not os.path.isdir(result_root):
            os.makedirs(result_root)
        train = (0, len(files)/10*8, 'tgt')
        dev = (len(files)/10*8,len(files)/10*9, "igt")
        test = (len(files)/10*9,len(files), "fgt")
        for group in [train, dev, test]:
            for filename in files[group[0]: group[1]]:
                if os.path.splitext(filename)[1] == '.tgt':
                    tgt_file_name = os.path.join(root, filename)
                    out_file_name = os.path.join(result_root, re.sub("tgt", group[2],filename))
                    print '%s -> %s' % (tgt_file_name, out_file_name)
                    out_stream = codecs.getwriter('utf-8')(open(out_file_name, 'w'))
                    convert(tgt_file_name, out_stream, in_format)
                    out_stream.close()
        #=======================================================================
        # for group in [dev, test]:
        #     for filename in files[group[0]: group[1]]:
        #         if os.path.splitext(filename)[1] == '.tgt':
        #             tgt_file_name = os.path.join(root, filename)
        #             out_file_name = os.path.join(result_root, re.sub("tgt", group[2],filename))
        #             print '%s -> %s' % (tgt_file_name, out_file_name)
        #             out_stream = codecs.getwriter('utf-8')(open(out_file_name, 'w'))
        #             convert(tgt_file_name, out_stream, "input")
        #             out_stream.close()
        #=======================================================================
            


def main():
    if len(sys.argv) < 5:
        print 'Usage: syntagrus2rusc.py <source> <destination> syntagrus/ruscorpora_syntagrus'
        exit()
    source, destination, output_format, new_dir = sys.argv[1:5]
    subprocess.call("rm -f {0}/*gt".format(destination), shell=True)
    subprocess.call("rm -f {0}/*gt".format(destination), shell=True)
    if os.path.isdir(source):
        convert_directory(source, destination, output_format)
    else:
        convert(source, destination, output_format)
    train_name = "train"
    dev_name = "dev"
    cmd = 'mkdir {0}'.format(new_dir)
    subprocess.Popen(cmd.split())
    sleep(1)   
    subprocess.call("rm -f {0}.tab {1}.tab".format(train_name, dev_name), shell=True)
    subprocess.call("cat {0}/*.tgt > {2}/{1}.conll".format(destination, train_name, new_dir), shell=True)
    subprocess.call("cat {0}/*.igt > {2}/{1}.conll".format(destination, dev_name, new_dir), shell=True)

if __name__ == '__main__':
    main()
