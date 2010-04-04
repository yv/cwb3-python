import sys
import CWB.CL as cwb
import PyCQP_interface
import pynlp.de.smor_pos as smor_pos

"""
example script that combines a CQP query with additional
processing.
pynlp.de.smor_pos.possible_pos (not included) would return
a list of possible POS tags for a word
"""

for corpus_name in ["TUEPP"]: #+['DEWAC%02d'%(x,) for x in range(1,10)]:
    print corpus_name
    cqp=PyCQP_interface.CQP(bin='/usr/local/bin/cqp',options='-c')
    cqp.Exec(corpus_name+";")
    cqp.Query('[word="ist|sind|war|waren|seid"] [pos="ADV|PPER"]* [word=".+[elr]n"] [pos="\$.|KON"];')
    cqp.Exec("sort Last by word;")
    rsize=int(cqp.Exec("size Last;"))
    results=cqp.Dump(first=0,last=rsize)
    cqp.Terminate()

    f=file(corpus_name+'_absentiv.txt','w')
    #f=sys.stdout
    corpus=cwb.Corpus(corpus_name);
    words=corpus["word"]
    postags=corpus["pos"]
    sentences=corpus["s"]
    texts=corpus["text_id"]
    for line in results:
        start=int(line[0])
        end=int(line[1])
        wn=words[end-1]
        posn=postags[end-1]
        poss=smor_pos.possible_pos(wn)
        if (posn.startswith('VV') and
            [pos for pos in poss if pos.startswith('VVINF')] and not
            [pos for pos in poss if pos.startswith('VVPP') or pos.startswith('VVIZU')]):
            s_bounds=sentences.find(end-1)
            text_bounds=texts.find(end-1)
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
