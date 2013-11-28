import sys
import optparse
import codecs
from gzip import GzipFile
import xml.etree.cElementTree as etree

def parse_xml(fname, attrnames, ff_out=None, encoding='UTF-8',
              unfilled='--'):
    num_tokens=0
    if fname.endswith('.gz'):
        f=GzipFile(fname)
    else:
        f=file(fname)
    if ff_out is None:
        f_out=codecs.getwriter(encoding)(sys.stdout)
    else:
        f_out=codecs.getwriter(encoding)(ff_out)
    print '<file id="%s">'%(fname,)
    for (ev,elem) in etree.iterparse(f, events=('start','end')):
        if elem.tag=='w':
            if ev=='end':
                if elem.text is None:
                    continue
                line=[elem.text]
                if unfilled=='word':
                    default=elem.text
                else:
                    default=unfilled
                for att in attrnames:
                    line.append(elem.attrib.get(att,unfilled))
                print >>f_out, u'\t'.join(line)
                num_tokens+=1
        else:
            if ev=='start':
                line=[]
                for att,val in elem.attrib.iteritems():
                    line.append('%s="%s"'%(att,val))
                print >>f_out, '<%s %s>'%(elem.tag, ' '.join(line))
            elif ev=='end':
                print >>f_out, '</%s>'%(elem.tag,)
            else:
                print ev
    f.close()
    print "</file>"
    return num_tokens

oparse=optparse.OptionParser()
oparse.add_option('--attrs',dest='attrs')
oparse.add_option('--default',dest='unfilled')
oparse.add_option('--write_ids',dest='offsets')

def main(argv=None):
    (opts,args)=oparse.parse_args(argv)
    attnames=[]
    if opts.attrs is not None:
        attnames+=opts.attrs.split(',')
    num_tokens=0
    if opts.offsets:
        f_offsets=file(opts.offsets,'w')
    else:
        f_offsets=None
    for fname in args:
        if f_offsets:
            print >>f_offsets, num_tokens, fname
        num_tokens+=parse_xml(fname, attnames, unfilled=opts.unfilled)
    print >>sys.stderr, "%s tokens written"%(num_tokens,)

if __name__=='__main__':
    main()

