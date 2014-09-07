from __future__ import print_function

import sys
import os
import argparse
from CWB.CL import Corpus

CQP_REGISTRY = os.getenv('CORPUS_REGISTRY')

__doc__ = '''
this module is suitable for converting CQP corpora into
CoNLL(-09) format with some empty columns. This allows
further processing by tools such as the MATE toolchain.
'''


def output_sentences(sent_attr, attrs, sent_start=0, sent_end=None, f_out=None):
    if sent_end is None:
        sent_end = len(sent_attr)
    if f_out is None:
        f_out = sys.stdout
    for sent_no in xrange(sent_start, sent_end):
        (off_start, off_end) = sent_attr[sent_no][:2]
        for i in xrange(off_start, off_end + 1):
            line = [str(i + 1 - off_start)]
            for (k, att) in enumerate(attrs):
                if att is None:
                    line.append('_')
                else:
                    s = att[i]
                    if k in [7, 8]:
                        if s[0] in '-+':
                            s = str(i + 1 - off_start + int(s))
                        elif s == 'ROOT':
                            s = '0'
                    line.append(s)
            print('\t'.join(line))
        print


def output_sentences_line(sent_attr, attrs, sent_start=0, sent_end=None, f_out=None):
    if sent_end is None:
        sent_end = len(sent_attr)
    if f_out is None:
        f_out = sys.stdout
    for sent_no in xrange(sent_start, sent_end):
        (off_start, off_end) = sent_attr[sent_no][:2]
        line = attrs[0][off_start:off_end + 1]
        print (' '.join(line), file=f_out)

def output_sentences_bllip(sent_attr, attrs, sent_start=0, sent_end=None,
                           f_out=None, corpus_name='corpus', max_len=None):
    if sent_end is None:
        sent_end = len(sent_attr)
    if f_out is None:
        f_out = sys.stdout
    for sent_no in xrange(sent_start, sent_end):
        (off_start, off_end) = sent_attr[sent_no][:2]
        if max_len is not None and off_end - off_start >= max_len:
            continue
        line = attrs[0][off_start:off_end + 1]
        print('<s %s_%d> %s </s>' % (
            corpus_name, sent_no, ' '.join(line)),
            file=f_out)

oparse = argparse.ArgumentParser(
    description='''extracts parts of a corpus in CoNLL (or other) format''')
oparse.add_argument('--fmt', dest='fmt',
                    help='output format (default: conll)',
                    default='conll',
                    choices=['conll', 'line', 'bllip'])
## oparse.add_option('--encoding', dest='encoding',
##                  default=None)
oparse.add_argument('-P', dest='xcolumns',
                    help='add an attribute to print out (with N=ATT for Nth column)',
                    default=[], action='append')
oparse.add_argument('-l', '--max-length', dest='max_len',
                    help='do not print sentences longer than MAX_LEN')
oparse.add_argument('CORPUS', dest='corpus',
                    help='the CQP corpus to use')
oparse.add_argument('start', dest='start', nargs='?', type='int',
                    help='first position to extract')
oparse.add_argument('end', dest='end', nargs='?', type='int',
                    help='end of extracted range')


def main(argv=None):
    args = oparse.parse_args(argv)
    corpus_name = args.corpus
    if args.end is not None:
        sent_start = args.start
        sent_end = args.end
    elif args.start is not None:
        sent_start = 0
        sent_end = args.start
    else:
        sent_start = 0
        sent_end = None
    columns = [None] * 14
    corpus = Corpus(corpus_name, registry_dir=CQP_REGISTRY)
    columns[0] = corpus.attribute('word', 'p')
    sent_attr = corpus.attribute('s', 's')
    if args.fmt == 'conll':
        idx = 1
        for col in args.xcolumns:
            if '=' in col:
                s_idx, att_name = col.split('=')
                s_idx = int(s_idx)
            else:
                s_idx = idx
                att_name = col
            columns[s_idx] = corpus.attribute(att_name, 'p')
            idx = s_idx + 1
        output_sentences(sent_attr, columns, sent_start, sent_end)
    elif args.fmt == 'line':
        output_sentences_line(sent_attr, columns, sent_start, sent_end)
    elif args.fmt == 'bllip':
        output_sentences_bllip(sent_attr, columns, sent_start, sent_end,
                               corpus_name=corpus_name, max_len=args.max_len)

if __name__ == '__main__':
    main()
