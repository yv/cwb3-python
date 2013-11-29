import sys
import optparse
import codecs
from CWB.CL import Corpus
from gzip import GzipFile
import xml.etree.cElementTree as etree

class CorpusInfo:
    def __init__(self, corpus_name):
        self.name=corpus_name
        self.corpus=Corpus(corpus_name)
        self.words=self.corpus.attribute('word','p')
        self.sentences=self.corpus.attribute('s','s')
        id_to_start={}
        text_ids=self.corpus.attribute('file_id','s')
        for start, end, fname in text_ids:
            id_to_start[fname]=start
        self.id_to_start=id_to_start
    def __getitem__(self,fname):
        return self.sentences.cpos2struc(self.id_to_start[fname])

def parse_xml(fname, corpus1, corpus2, reverse=False,
              f_smap=None, f_dump=None):
    num_tokens=0
    if fname.endswith('.gz'):
        f=GzipFile(fname)
    else:
        f=file(fname)
    if not reverse:
        print "%s\ts\t%s\ts"%(corpus1.name,corpus2.name)
    else:
        print "%s\ts\t%s\ts"%(corpus2.name,corpus1.name)
    offset1=offset2=-1
    lst=[]
    last_alg=-1
    for (ev,elem) in etree.iterparse(f, events=('start','end')):
        if elem.tag=='link':
            if ev=='end':
                tgt1s,tgt2s=elem.attrib['xtargets'].split(';')
                tgt1=[offset1+int(s)-1 for s in tgt1s.split()]
                tgt2=[offset2+int(s)-1 for s in tgt2s.split()]
                #print tgt1, tgt2
                # start1=corpus1.sentences[tgt1[0]][0]
                # end1=corpus1.sentences[tgt1[-1]][1]
                # print corpus1.name, ' '.join([corpus1.words[i]
                #                               for i in xrange(start1,end1+1)])
                # start2=corpus2.sentences[tgt2[0]][0]
                # end2=corpus2.sentences[tgt2[-1]][1]
                # print corpus2.name, ' '.join([corpus2.words[i]
                #                               for i in
                #                               xrange(start2,end2+1)])
                if not tgt1:
                    continue
                if not tgt2:
                    continue
                # output word offsets, not sentence ids
                if not reverse:
                    lst.append((corpus1.sentences[tgt1[0]][0],
                                corpus1.sentences[tgt1[-1]][1],
                                corpus2.sentences[tgt2[0]][0],
                                corpus2.sentences[tgt2[-1]][1]))
                else:
                    lst.append((corpus2.sentences[tgt2[0]][0],
                                corpus2.sentences[tgt2[-1]][1],
                                corpus1.sentences[tgt1[0]][0],
                                corpus1.sentences[tgt1[-1]][1]))
                if (f_smap is not None and
                    len(tgt1)==1 and 
                    len(tgt2)==1):
                    if not reverse:
                        print >>f_smap, "%s\t%s"%(tgt1[0],tgt2[0])
                    else:
                        print >>f_smap, "%s\t%s"%(tgt2[0],tgt1[0])
                if (f_smap is not None and
                    len(tgt1)==1 and 
                    len(tgt2)==1):
                    if not reverse:
                        print >>f_dump, "%s\t%s"%(corpus1.sentences[tgt1[0]][0],
                                                  corpus1.sentences[tgt1[0]][1])
                    else:
                        print >>f_dump, "%s\t%s"%(corpus2.sentences[tgt2[0]][0],
                                                  corpus2.sentences[tgt2[0]][1])
        elif elem.tag=='linkGrp':
            if ev=='start':
                offset1=corpus1[elem.attrib['fromDoc']]
                offset2=corpus2[elem.attrib['toDoc']]
                print >>sys.stderr, "\r%d %s"%(offset1, offset2),
                if lst:
                    if reverse:
                        lst.sort()
                    for tup in lst:
                        if last_alg>=tup[0]:
                            print >>sys.stderr, "Duplicate alignment: %s %s"%(last_alg,tup)
                            continue
                        print "%s\t%s\t%s\t%s"%tup
                        last_alg=tup[1]
                    lst=[]
    f.close()
    if lst:
        if reverse:
            lst.sort()
        for tup in lst:
            if last_alg>=tup[0]:
                print >>sys.stderr, "Duplicate alignment: %s %s"%(last_alg,tup)
                continue
            print "%s\t%s\t%s\t%s"%tup
            last_alg=tup[1]
    print >>sys.stderr, "\ndone."

oparse=optparse.OptionParser()
oparse.add_option('--reverse', dest='reverse',
                  default=False, action='store_true')
oparse.add_option('--smap', dest='smap_fname',
                  default=None)
oparse.add_option('--subcorpus', dest='dump_fname',
                  default=None)

def main(argv=None):
    (opts,args)=oparse.parse_args(argv)
    attnames=[]
    corpus1=CorpusInfo(args[0])
    corpus2=CorpusInfo(args[1])
    if opts.smap_fname:
        f_smap=file(opts.smap_fname,'w')
    else:
        f_smap=None
    if opts.dump_fname:
        f_dump=file(opts.dump_fname,'w')
    else:
        f_dump=None
    for fname in args[2:]:
        parse_xml(fname, corpus1, corpus2, opts.reverse,
                  f_smap, f_dump)
    if f_smap is not None:
        f_smap.close()
    if f_dump is not None:
        f_dump.close()

if __name__=='__main__':
    main()

