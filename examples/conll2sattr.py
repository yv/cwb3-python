import sys
import simplejson as json
from gzip import GzipFile
from itertools import izip
from collections import defaultdict
import optparse
import codecs
from pcfg_site_config import get_config_var
from CWB.CL import Corpus

oparse = optparse.OptionParser()


def conll2cqp_main(argv=None):
    opts, args = oparse.parse_args(argv)
    token_idx=0
    for fname in args:
        if fname.endswith('.gz'):
            f_in = GzipFile(fname)
        else:
            f_in = file(fname)
        in_sent = False
        for l in f_in:
            line = l.rstrip().split()
            if line:
                if not in_sent:
                    start_idx=token_idx
                    in_sent = True
                    line_idx = 0
                token_idx+=1 
            else:
                if in_sent:
                   print "%s\t%s"%(start_idx,token_idx-1) 
                in_sent = False
        if in_sent:
           print "%s\t%s"%(start_idx,token_idx-1) 
           in_sent=False

if __name__ == '__main__':
    conll2cqp_main()
