import codecs

cdef extern from "stdlib.h":
  void *malloc(int size)
  void free(void *)

cdef extern from "string.h":
  int strcmp(char *, char *)

cdef extern from "cwb/cl.h":
  int ATT_NONE
  int ATT_POS
  int ATT_STRUC
  int ATT_ALIGN
  int CDA_ESTRUC
  int CDA_EALIGN
  char *cdperror_string(int error_num)
  union c_Attribute "_Attribute"
  struct c_Corpus "TCorpus":
    pass
  c_Attribute *cl_new_attribute(c_Corpus *corpus,
                               char *attribute_name,
                               int type)
  c_Corpus *cl_new_corpus(char *registry_dir, char *registry_name)
  char *cl_corpus_charset(c_Corpus *corpus)
  void cl_delete_corpus(c_Corpus *corpus)
  char *cl_cpos2str(c_Attribute *attribute, int position)
  int cl_cpos2id(c_Attribute *attribute, int position)
  char *cl_struc2str(c_Attribute *attribute, int position)
  bint cl_struc2cpos(c_Attribute *attribute, int position,
                     int *start, int *end)
  int cl_str2id(c_Attribute *attribute, char *str)
  char *cl_id2str(c_Attribute *attribute, int id)
  int cl_cpos2struc(c_Attribute *attribute, int offset)
  int cl_max_struc(c_Attribute *attribute)
  int cl_max_id(c_Attribute *attribute)
  int cl_max_cpos(c_Attribute *attribute)
  bint cl_struc_values(c_Attribute *attribute)
  int *cl_id2cpos(c_Attribute *attribute, int tagid, int *result_len)
  int cl_id2freq(c_Attribute *attribute, int tagid)
  int cl_max_alg(c_Attribute *attribute)
  int cl_cpos2alg(c_Attribute *attribute, int cpos)
  int cl_alg2cpos(c_Attribute *attribute, int alg,
                  int *source_start, int *source_end,
                  int *target_start, int *target_end)
  int *collect_matching_ids(c_Attribute *attribute, char *pattern,
                            int canonicalize, int *number_of_matches)
  int *cl_idlist2cpos(c_Attribute *attribute,
                      int *ids, int number_of_ids,
                      int sort,
                      int *size_of_table)
  int get_struc_attribute(c_Attribute *attribute, int cpos, int *s_start, int *s_end)
  int get_num_of_struc(c_Attribute *attribute, int cpos, int *s_num)
  int get_bounds_of_nth_struc(c_Attribute *attribute, int struc_num, int *s_start, int *s_end)

cdef public object registry

registry="/usr/local/share/cwb/registry/"

cdef class PosAttrib
cdef class AttStruc
cdef class AlignAttrib

# TBD:
# list_corpora => gives a list of all corpora

cdef class Corpus:
  cdef c_Corpus *corpus
  cdef object name
  cdef object charset_decoder
  cdef object charset_encoder
  def __cinit__(self, cname, encoding='ISO-8859-15', registry_dir=None):
    if registry_dir is None:
      registry_dir=registry
    self.corpus=cl_new_corpus(registry_dir,cname)
    if self.corpus==NULL:
      raise KeyError(cname)
    self.name=cname
    self.charset_decoder=codecs.getdecoder(encoding)
    self.charset_encoder=codecs.getencoder(encoding)
  cpdef bytes to_str(self, s):
    if isinstance(s,unicode):
      return self.charset_encoder(s)[0]
    else:
      return s
  cpdef unicode to_unicode(self, s):
    if isinstance(s,unicode):
      return s
    else:
      return self.charset_decoder(s)[0]
  def __repr__(self):
      return "cwb.CL.Corpus('%s')"%(self.name)
  def __dealloc__(self):
    if self.corpus!=NULL:
      cl_delete_corpus(self.corpus)
    self.corpus=NULL
  def attribute(self, name, atype):
    if atype=='s':
      return AttStruc(self,name)
    elif atype=='p':
      return PosAttrib(self,name)
    elif atype=='a':
      return AlignAttrib(self,name)

cdef class IDList:
  cdef int *ids
  cdef int length
  def __cinit__(self, seq=None):
    cdef int i, old_val, is_sorted
    if seq is None:
      self.ids=NULL
      self.length=0
    else:
      self.length=len(seq)
      self.ids=<int *>malloc(self.length*sizeof(int))
      old_val=-1
      is_sorted=True
      for i from 0<=i<self.length:
        if seq[i]<old_val:
          is_sorted=False
        old_val=seq[i]
        self.ids[i]=seq[i]
      assert sorted
  def __len__(self):
    return self.length
  def __getitem__(self,i):
    if i<0 or i>=self.length:
      raise IndexError
    return self.ids[i]
  def __contains__(self,v):
    cdef int lo,hi,mid,val
    lo=0
    hi=self.length
    while hi-lo>1:
      mid=(hi+lo)/2
      val=self.ids[mid]
      if val==v:
        return True
      elif val<v:
        lo=mid+1
      else:
        hi=mid
    if lo<hi:
      return self.ids[lo]==v
    else:
      return False
  def __and__(IDList self, IDList other):
    return self.join(other,0)
  def __or__(IDList self, IDList other):
    cdef int *result
    cdef int k1, k2, k
    cdef int val1, val2
    cdef IDList r
    # allocate once, using a conservative estimate on
    # how big the result list is
    result=<int *>malloc((self.length+other.length)*sizeof(int))
    k1=k2=k=0
    while k1<self.length and k2<other.length:
      val1=self.ids[k1]
      val2=other.ids[k2]
      if val1<val2:
        result[k]=val1
        k+=1
        k1+=1
      elif val2<val1:
        result[k]=val2
        k+=1
        k2+=1
      else:
        result[k]=val1
        k+=1
        k1+=1
        k2+=1
    while k1<self.length:
      val1=self.ids[k1]
      result[k]=val1
      k+=1
      k1+=1
    while k2<other.length:
      val2=other.ids[k2]
      result[k]=val2
      k+=1
      k2+=1
    r=IDList()
    r.length=k
    r.ids=result
    return r
  def __sub__(IDList self, IDList other):
    cdef int *result
    cdef int k1, k2, k
    cdef int val1, val2
    cdef IDList r
    # allocate once, using a conservative estimate on
    # how big the result list is
    result=<int *>malloc(self.length*sizeof(int))
    k1=k2=k=0
    while k1<self.length and k2<other.length:
      val1=self.ids[k1]
      val2=other.ids[k2]
      if val1<val2:
        result[k]=val1
        k+=1
        k1+=1
      elif val2<val1:
        k2+=1
      else:
        k1+=1
        k2+=1
    while k1<self.length:
      result[k]=self.ids[k1]
      k+=1
      k1+=1
    r=IDList()
    r.length=k
    r.ids=result
    return r    
  cpdef IDList join(self, IDList other, int offset):
    cdef int *result
    cdef int k1, k2, k
    cdef int val1, val2
    cdef IDList r
    # allocate once, using a conservative estimate on
    # how big the result list is
    if other.length<self.length:
      result=<int *>malloc(other.length*sizeof(int))
    else:
      result=<int *>malloc(self.length*sizeof(int))
    k1=k2=k=0
    while k1<self.length and k2<other.length:
      val1=self.ids[k1]
      val2=other.ids[k2]-offset
      if val1<val2:
        k1+=1
      elif val2<val1:
        k2+=1
      else:
        result[k]=val1
        k+=1
        k1+=1
        k2+=1
    r=IDList()
    r.length=k
    r.ids=result
    return r
  def __dealloc__(self):
    free(self.ids)

cdef class AttrDictionary

cdef class PosAttrib:
  cdef c_Attribute *att
  cdef Corpus parent
  cdef object attname
  def __repr__(self):
    return "cwb.Attribute(%s,'%s')"%(self.parent,self.attname)
  def __cinit__(self,Corpus parent,attname):
    self.parent=parent
    self.att=cl_new_attribute(parent.corpus,attname,ATT_POS)
    if self.att==NULL:
      raise KeyError
    self.attname=attname
  def getName(self):
    return self.attname
  def getDictionary(self):
    return AttrDictionary(self)
  def __getitem__(self,offset):
    cdef int i
    if isinstance(offset,int):
      if offset<0 or offset>=len(self):
        raise IndexError('P-attribute offset out of bounds')
      return cl_cpos2str(self.att,offset)
    else:
      result=[]
      if offset.start<0 or offset.stop<offset.start or offset.stop>len(self):
        raise IndexError('P-attribute offset out of bounds')
      for i from offset.start<=i<offset.stop:
        result.append(cl_cpos2str(self.att,i))
      return result
  cpdef cpos2id(self,int offset):
    return cl_cpos2id(self.att,offset)
  def find(self,tag):
    cdef int tagid
    cdef IDList lst
    cdef object tag_s=self.parent.to_str(tag)
    tagid=cl_str2id(self.att,tag_s)
    if tagid<0:
      raise KeyError
    lst=IDList()
    lst.ids=cl_id2cpos(self.att,tagid,&lst.length)
    return lst
  def find_list(self, tags):
    cdef int tagid
    cdef bytes tag_s
    cdef IDList lst, lst_result
    ids_set=set()
    for tag in tags:
      tag_s=self.parent.to_str(tag)
      tagid=cl_str2id(self.att,tag_s)
      if tagid<0:
        continue
      ids_set.add(tagid)
    lst=IDList(sorted(ids_set))
    lst_result=IDList()
    lst_result.ids=cl_idlist2cpos(self.att, lst.ids, lst.length, 1, &lst_result.length)
    return lst_result
  def find_pattern(self, pat, flags=0):
    cdef IDList lst, lst_result
    cdef bytes pat_s=self.parent.to_str(pat)
    lst=IDList()
    lst.ids=collect_matching_ids(self.att, pat_s, flags, &lst.length)
    lst_result=IDList()
    lst_result.ids=cl_idlist2cpos(self.att, lst.ids, lst.length, 1, &lst_result.length)
    return lst_result
  def frequency(self, tag):
    cdef bytes tag_s=self.parent.to_str(tag)
    cdef int tagid=cl_str2id(self.att,tag_s)
    if tagid<0:
      raise KeyError(cdperror_string(tagid))
    return cl_id2freq(self.att,tagid)
  def __len__(self):
    return cl_max_cpos(self.att)

cdef class AttrDictionary:
  cdef PosAttrib attr
  def __cinit__(self,d):
    self.attr=d
  def __len__(self):
    return cl_max_id(self.attr.att)
  def __getitem__(self,s):
    cdef int val
    val=cl_str2id(self.attr.att,s)
    if val>=0:
      return val
    else:
      raise KeyError(cdperror_string(val))
  def get_word(self,n):
    cdef char *s
    s=cl_id2str(self.attr.att,n)
    return s
  def get_matching(self,pat,flags=0):
    cdef IDList lst
    lst=IDList()
    lst.ids=collect_matching_ids(self.attr.att,pat,flags,&lst.length)
    return lst
  def expand_pattern(self,pat,flags=0):
    cdef IDList lst
    cdef i
    result=[]
    lst=self.get_matching(pat)
    for i from 0<=i<lst.length:
      result.append(cl_id2str(self.attr.att,lst.ids[i]))
    return result

cdef class AttStruc:
  cdef c_Attribute *att
  cdef bint has_values
  cdef Corpus parent
  cdef object attname
  def __repr__(self):
    return "CWB.CL.AttrStruct(%s,'%s')"%(self.parent,self.attname)
  def __cinit__(self,Corpus parent,attname):
    self.parent=parent
    self.att=cl_new_attribute(parent.corpus,attname,ATT_STRUC)
    if self.att==NULL:
      raise KeyError
    self.has_values=cl_struc_values(self.att)
    self.attname=attname
  def getName(self):
    return self.attname
  def find_all(self,tags):
    # s-attr string attributes are not indexed
    # so we just do the stupid thing here.
    cdef int i
    strucs=[]
    if not self.has_values: raise TypeError
    for i from 0<=i<cl_max_struc(self.att):
      struc_id=cl_struc2str(self.att,i)
      if struc_id in tags:
        strucs.append(i)
    return strucs
  def find_pos(self,offset):
    return self[cl_cpos2struc(self.att,offset)]
  def cpos2struc(self,offset):
    cdef int val
    val=cl_cpos2struc(self.att,offset)
    if val==CDA_ESTRUC:
      raise KeyError("no structure at this position")
    return val
  def map_idlist(self, IDList lst):
    """returns an IDList with (unique) struc offsets instead of
       corpus positions"""
    cdef IDList result=IDList()
    cdef int i, k, val, lastval
    result.ids=<int *>malloc(lst.length*sizeof(int))
    k=0
    lastval=-1
    for i from 0<=i<lst.length:
      val=cl_cpos2struc(self.att,lst.ids[i])
      if val>=0 and val!=lastval:
        result.ids[k]=val
        k+=1
        lastval=val
    result.length=k
    return result
  def __getitem__(self,index):
    cdef int start, end
    if index<0 or index>=cl_max_struc(self.att):
       raise IndexError
    cl_struc2cpos(self.att,index,&start,&end)
    if self.has_values:
      return (start,end,cl_struc2str(self.att,index))
    else:
      return (start,end)
  def __len__(self):
    return cl_max_struc(self.att)

cdef class AlignAttrib:
  cdef c_Attribute *att
  cdef bint has_values
  cdef Corpus parent
  cdef object attname
  def __repr__(self):
    return "CWB.CL.AlignAttrib(%s,'%s')"%(self.parent,self.attname)
  def __cinit__(self,Corpus parent,attname):
    self.parent=parent
    self.att=cl_new_attribute(parent.corpus,attname,ATT_ALIGN)
    if self.att==NULL:
      raise KeyError
    self.has_values=cl_struc_values(self.att)
    self.attname=attname
  def getName(self):
    return self.attname
  def cpos2alg(self,cpos):
    cdef int val
    val=cl_cpos2alg(self.att,cpos)
    if val==CDA_EALIGN:
      raise KeyError("no alignment at this position")
    return val
  def __getitem__(self,index):
    cdef int start_a,end_a,start_b,end_b
    if index<0 or index>=cl_max_alg(self.att):
      raise IndexError
    cl_alg2cpos(self.att,index,
                &start_a,&end_a,
                &start_b,&end_b)
    return (start_a,end_a,start_b,end_b)
  def __len__(self):
    return cl_max_alg(self.att)
  

def test():
    cdef Corpus corpus
    cdef c_Attribute *att
    cdef int i
    corpus=Corpus("FEMME")
    print repr(corpus)
    print corpus.get_P_attributes()
    print corpus.get_S_attributes()
    attr=corpus["word"]
    print attr[0:4]
    attr2=AttStruc(corpus,"s")
    print len(attr2), attr2[23]
    rng=attr2[23]
    print attr[rng[0]:rng[1]]
    print list(attr.find("femme"))
