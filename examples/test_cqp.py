import sys
from CWB.CL import Corpus
import PyCQP_interface

"""
example script that combines a CQP query with additional
processing.
pynlp.de.smor_pos.possible_pos (not included) would return
a list of possible POS tags for a word
"""

registry_dir='/usr/local/share/cwb/registry'

for corpus_name in ["DEWAC01"]: #+['DEWAC%02d'%(x,) for x in range(1,10)]:
    print corpus_name
    cqp=PyCQP_interface.CQP(bin='/usr/local/bin/cqp',options='-c -r '+registry_dir)
    cqp.Exec(corpus_name+";")
    cqp.Query('[word="ist|sind|war|waren|seid"] [pos="ADV|PPER"]* [word=".+[elr]n"] [pos="\$.|KON"];')
    cqp.Exec("sort Last by word;")
    rsize=int(cqp.Exec("size Last;"))
    results=cqp.Dump(first=0,last=rsize)
    cqp.Terminate()

    f=file(corpus_name+'_absentiv.txt','w')
    #f=sys.stdout
    corpus=Corpus(corpus_name,registry_dir=registry_dir);
    words=corpus.attribute("word","p")
    postags=corpus.attribute("pos","p")
    sentences=corpus.attribute("s","s")
    texts=corpus.attribute("text_id","s")
    for line in results:
        start=int(line[0])
        end=int(line[1])
        wn=words[end-1]
        posn=postags[end-1]
        if posn.startswith('VV'):
            s_bounds=sentences.find_pos(end-1)
            text_bounds=texts.find_pos(end-1)
            print >>f,"# %s"%(text_bounds[2],)
            print >>f,"%10d:"%(int(line[1]),),
            for pos in xrange(s_bounds[0],s_bounds[1]+1):
                if pos==end-1:
                    print >>f,"<%s>"%(words[pos],),
                else:
                    print >>f,words[pos],
            #if pos==end-1:
            #    print postags[pos],
            print >>f
    f.close()
