cdef extern from "stdlib.h":
  void free(void *)

cdef extern from "string.h":
  int strcmp(char *, char *)

cdef extern from "cwb/cl.h":
  int ATT_NONE
  int ATT_POS
  int ATT_STRUC
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
  char *cl_struc2str(c_Attribute *attribute, int position)
  bint cl_struc2cpos(c_Attribute *attribute, int position,
                     int *start, int *end)
  int cl_str2id(c_Attribute *attribute, char *str)
  int cl_cpos2struc(c_Attribute *attribute, int offset)
  int cl_max_struc(c_Attribute *attribute)
  int cl_max_cpos(c_Attribute *attribute)
  bint cl_struc_values(c_Attribute *attribute)
  int *cl_id2cpos(c_Attribute *attribute, int tagid, int *result_len)
  int get_struc_attribute(c_Attribute *attribute, int cpos, int *s_start, int *s_end)
  int get_num_of_struc(c_Attribute *attribute, int cpos, int *s_num)
  int get_bounds_of_nth_struc(c_Attribute *attribute, int struc_num, int *s_start, int *s_end)

cdef public object registry

registry="/usr/local/share/cwb/registry/"

cdef class PosAttrib
cdef class AttStruc

# TBD:
# list_corpora => gives a list of all corpora

cdef class Corpus:
  cdef c_Corpus *corpus
  cdef object name
  def __cinit__(self,cname):
    self.corpus=cl_new_corpus(registry,cname)
    self.name=cname
  def __repr__(self):
      return "cwb.corpus('%s')"%(self.cname)
  def __del__(self):
      cl_delete_corpus(self.corpus)
      self.corpus=NULL
  def attribute(self, name, atype):
    if atype=='s':
      return AttStruc(self,name)
    elif atype=='p':
      return PosAttrib(self,name)

cdef class IDList:
  cdef int *ids
  cdef int length
  def __cinit__(self):
    self.ids=NULL
    self.length=0
  def __len__(self):
    return self.length
  def __getitem__(self,i):
    if i<0 or i>=self.length:
      raise IndexError
    return self.ids[i]
  def __del__(self):
    free(self.ids)

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
  def __getitem__(self,offset):
    cdef int i
    if isinstance(offset,int):
      return cl_cpos2str(self.att,offset)
    else:
      result=[]
      for i from offset.start<=i<offset.stop:
        result.append(cl_cpos2str(self.att,i))
      return result
  def find(self,tag):
    cdef int tagid
    cdef IDList lst
    tagid=cl_str2id(self.att,tag)
    if tagid<0:
      raise KeyError
    lst=IDList()
    lst.ids=cl_id2cpos(self.att,tagid,&lst.length)
    return lst
  def __len__(self):
    return cl_max_cpos(self.att)

cdef class AttStruc:
  cdef c_Attribute *att
  cdef bint has_values
  cdef Corpus parent
  cdef object attname
  def __repr__(self):
    return "cwb.AttrStruct(%s,'%s')"%(self.parent,self.attname)
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
    return cl_cpos2struc(self.att,offset)
  def __getitem__(self,index):
    cdef int start, end
    if index>=cl_max_struc(self.att):
       raise IndexError
    cl_struc2cpos(self.att,index,&start,&end)
    if self.has_values:
      return (start,end,cl_struc2str(self.att,index))
    else:
      return (start,end)
  def __len__(self):
    return cl_max_struc(self.att)

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
