import sys
import optparse
from CWB.CL import Corpus
from collections import defaultdict

try:
    from pcfg_site_config import get_config_var
    CQP_REGISTRY = get_config_var('pycwb.cqp_registry')
except ImportError:
    CQP_REGISTRY = None
except KeyError:
    CQP_REGISTRY=None
    

oparse=optparse.OptionParser()
oparse.add_option('--attr',
                  dest='attr',
                  default='word')
oparse.add_option('--threshold',
                  dest='threshold',
                  type='int',
                  default=10)
oparse.add_option('-O','--output',
                  dest='out_fname',
                  default=None)
oparse.add_option('--encoding',
                  dest='encoding')

def cqp2vocab_main(argv=None):
    opts,args=oparse.parse_args(argv)
    frequencies=defaultdict(int)
    for arg in args:
        crp=Corpus(arg,registry_dir=CQP_REGISTRY)
        att=crp.attribute(opts.attr,'p')
        if opts.encoding is not None and crp.get_encoding()!=opts.encoding:
            print >>sys.stderr, "Recoding %s items from %s to %s"%(
                arg, crp.get_encoding(), opts.encoding)
            to_uni=crp.to_unicode
            enc=opts.encoding
            recode=lambda w: to_uni(w).encode(enc)
        else:
            recode=lambda x: x
        dic=att.getDictionary()
        for i in xrange(len(dic)):
            word=dic.get_word(i)
            frequencies[recode(word)]+=att.frequency(word)
    for word in frequencies.keys():
        if frequencies[word]<opts.threshold:
            del frequencies[word]
    if opts.out_fname is None:
        f_out=sys.stdout
    else:
        f_out=file(opts.out_fname,'w')
    for word in sorted(frequencies):
        print >>f_out, word

if __name__=='__main__':
    cqp2vocab_main()
