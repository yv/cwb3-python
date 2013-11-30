import sys
import optparse
from CWB.CL import Corpus

try:
    from pcfg_site_config import get_config_var
    CQP_REGISTRY=get_config_var('pycwb.cqp_registry')
except ImportError:
    CQP_REGISTRY=None
except KeyError:
    CQP_REGISTRY=None

__doc__='''
this module is suitable for converting CQP corpora into
CoNLL(-09) format with some empty columns. This allows
further processing by tools such as the MATE toolchain.
'''

def output_sentences(sent_attr, attrs, sent_start=0, sent_end=None, f_out=None):
    if sent_end is None:
        sent_end=len(sent_attr)
    if f_out is None:
        f_out=sys.stdout
    for sent_no in xrange(sent_start, sent_end):
        (off_start, off_end)=sent_attr[sent_no][:2]
        for i in xrange(off_start,off_end+1):
            line=[str(i+1-off_start)]
            for att in attrs:
                if att is None:
                    line.append('_')
                else:
                    line.append(att[i])
            print '\t'.join(line)
        print

def output_sentences_line(sent_attr, attrs, sent_start=0, sent_end=None, f_out=None):
    if sent_end is None:
        sent_end=len(sent_attr)
    if f_out is None:
        f_out=sys.stdout
    for sent_no in xrange(sent_start, sent_end):
        (off_start, off_end)=sent_attr[sent_no][:2]
        line=attrs[0][off_start:off_end+1]
        print >>f_out,' '.join(line)

def output_sentences_bllip(sent_attr, attrs, sent_start=0, sent_end=None,
                           f_out=None, corpus_name='corpus', max_len=None):
    if sent_end is None:
        sent_end=len(sent_attr)
    if f_out is None:
        f_out=sys.stdout
    for sent_no in xrange(sent_start, sent_end):
        (off_start, off_end)=sent_attr[sent_no][:2]
        if max_len is not None and off_end-off_start >= max_len:
            continue
        line=attrs[0][off_start:off_end+1]
        print >>f_out,'<s %s_%d> %s </s>'%(corpus_name,sent_no,' '.join(line))

oparse=optparse.OptionParser()
oparse.add_option('--fmt', dest='fmt',
                  default='conll',
                  choices=['conll','line','bllip'])
oparse.add_option('-l', '--max-length', dest='max_len')


def main(argv=None):
    (opts,args)=oparse.parse_args(argv)
    corpus_name=args[0]
    if len(args)==3:
        sent_start=int(args[1])
        sent_end=int(args[2])
    elif len(args)==2:
        sent_start=0
        sent_end=int(args[1])
    else:
        sent_start=0
        sent_end=None
    columns=[None]*14
    corpus=Corpus(corpus_name, registry_dir=CQP_REGISTRY)
    columns[0]=corpus.attribute('word','p')
    sent_attr=corpus.attribute('s','s')
    if opts.fmt=='conll':
        output_sentences(sent_attr, columns, sent_start, sent_end)
    elif opts.fmt=='line':
        output_sentences_line(sent_attr, columns, sent_start, sent_end)
    elif opts.fmt=='bllip':
        output_sentences_bllip(sent_attr, columns, sent_start, sent_end,
                               corpus_name=corpus_name, max_len=opts.max_len)

if __name__=='__main__':
    main()
