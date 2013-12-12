import optparse
from CWB.CL import Corpus
from collections import defaultdict

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
                  dest='encoding',
                  default='UTF-8')

def cqp2vocab_main(argv=None):
    opts,args=oparse.parse_args(argv)
    frequencies=defaultdict(int)
    for arg in args:
        crp=Corpus(arg)
        att=crp.attribute(opts.attr)
        if crp.get_encoding()!=opts.encoding:
            print >>sys.stderr, "Recoding %s items from %s to %s"%(
                arg, crp.get_encoding(), opts.encoding)
            to_uni=crp.to_unicode
            enc=opts.encoding
            recode=lambda w: to_uni(w).encode(enc)
        else:
            recode=id
        for word in att.getDictionary():
            frequencies[word]+=att.frequency(recode(word))
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
