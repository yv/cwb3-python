import sys
import optparse
import codecs
from simplejson import json
from CWB.CL import Corpus
from gzip import GzipFile

__doc__='''
Tools to write a JSON-format aligned corpus
(with original word forms and sentence ID hints)
from the output of PostCAT or fast_align
'''

try:
    from pcfg_site_config import get_config_var
    CQP_REGISTRY=get_config_var('pycwb.cqp_registry')
except ImportError:
    CQP_REGISTRY=None
except KeyError:
    CQP_REGISTRY=None

class CorpusInfo:
    def __init__(self, corpus_name):
        self.name=corpus_name
        self.corpus=Corpus(corpus_name, registry_dir=CQP_REGISTRY)
        self.words=self.corpus.attribute('word','p')
        self.sentences=self.corpus.attribute('s','s')
        id_to_start={}
        text_ids=self.corpus.attribute('file_id','s')
        for start, end, fname in text_ids:
            id_to_start[fname]=start
        self.id_to_start=id_to_start
    def __getitem__(self,fname):
        return self.sentences.cpos2struc(self.id_to_start[fname])

def get_alignments(corpus1, corpus2,
                   att1='word', att2='word',
                   max_len=None):
    att_align=corpus1.corpus.attribute(corpus2.name.lower(),'a')
    seq1=corpus1.corpus.attribute(att1,'p')
    seq2=corpus2.corpus.attribute(att2,'p')
    words1=corpus1.words
    words2=corpus2.words
    sent=corpus1.sentences
    for start1, end1, start2, end2 in att_align:
        if max_len is not None and (end1-start1>=max_len or
                                    end2-start2>=max_len):
            continue
        yield {'seq1':seq1[start1:end1+1],
               'seq2':seq2[start2:end2+1],
               'words1':words1[start1:end1+1],
               'words2':words2[start2:end2+1],
               '_id':sent.cpos2struc(start1)}

def read_alignments(f_lang1, f_lang2, f_align):
    for l_align in f_align:
        align=[map(int,x.split('-')) for x in l_align().strip().split()]
        words1=f_lang1.readline().strip().split()
        words2=f_lang2.readline().strip().split()
        yield {'align':align,
               'seq1':words1,
               'seq2':words2}

def maybe_write(fname):
    if fname is None:
        return None
    else:
        return file(fname,'w')

def merge_alignments(seq1, seq2):
    for s1,s2 in izip(seq1, seq2):
        assert s1['seq1']==s2['seq1']
        assert s1['seq2']==s2['seq2']
        yield {'words1':s2['words1'],
               'words2':s2['words2'],
               'align':s1['align'],
               '_id':s2['_id']}

oparse=optparse.OptionParser()
oparse.add_option('--e',dest='lang1_fname',
                  default=None)
oparse.add_option('--f',dest='lang2_fname',
                  default=None)
oparse.add_option('--align',dest='align_fname',
                  default=None)
oparse.add_option('--json',dest='json_fname',
                  default=None)
oparse.add_option('--eatt', dest='attr_e',
                  default='word')
oparse.add_option('--fatt', dest='attr_f',
                  default='word')
oparse.add_option('--maxlen', dest='maxlen',
                  default=None)
def main(argv=None):
    (opts,args)=oparse.parse_args(argv)
    attnames=[]
    corpus1=CorpusInfo(args[0])
    corpus2=CorpusInfo(args[1])
    f_lang1=file(opts.lang1_fname)
    f_lang2=file(opts.lang2_fname)
    f_align=file(opts.align_fname)
    f_json=maybe_write(opts.json_fname)
    if f_json is None:
        f_json=sys.stdout
    seq1=read_alignments(f_lang1, f_lang2, f_align)
    seq2=get_alignments(corpus1, corpus2,
                        att1=opts.attr_e,
                        att2=opts.attr_f,
                        max_len=opts.maxlen)
    for json_obj in merge_alignments(seq1, seq2):
        print >>f_json, json.dumps(json_obj)

if __name__=='__main__':
    main()

