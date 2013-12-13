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
                    print "<s>"
                    in_sent = True
                    line_idx = 0
                line_idx += 1
                result = []
                result.append(line[1])
                result.append(line[5])
                result.append(line[3])
                result.append(line[7])
                if line[9]=='_':
                    parent_idx='_'
                else:
                    parent_idx = int(line[9])
                    if parent_idx != 0:
                        parent_idx -= line_idx
                result.append(str(parent_idx))
                result.append(line[11])
                print '\t'.join(result)
            else:
                if in_sent:
                    print "</s>"
                in_sent = False
        if in_sent:
            print "</s>"
            in_sent=False

if __name__ == '__main__':
    conll2cqp_main()
