CWB.CL: The Lowlevel Interface
------------------------------

.. py:module:: CWB.CL

The Cython module CWB.CL is modeled after the Perl low-level interface
for CQP, CWB::CL, and allows direct access to the attributes of a corpus.

CQP organizes access to a corpus in terms of *corpus positions*, which involve
a numbering of all tokens in the corpus from 0 to *max_cpos*. Sentences or
text boundaries are modeled as a non-overlapping sequence of *spans* over
these corpus positions.

.. py:class:: Corpus

   The *Corpus* class represents one CQP corpus and its (positional and span)
   attributes.

   .. py:method:: __init__(self, cname, encoding="ISO-8859-15", registry_dir=None)

      Loads the corpus named *cname*. By using a non-*None* value for the *registry_dir*
      parameter, it is possible to use corpus description files in other locations than
      the default ``/usr/local/share/cwb/registry``.

   .. py:method:: attribute(self, name, atype)

      Retrieves the corpus attribute named *name*, which can either be
      a positional attribute (``atype='p'``) with information for each token,
      or a structural attribute (``atype='s'``) with spans of tokens (which can
      optionally be labeled). Positional attributes usually include word forms,
      POS tags and such, whereas structural attributes are typically used to
      represent sentence or text boundaries.

      Depending on the type of attribute, this returns either a :py:class:`PosAttrib`,
      a :py:class:`AttStruc` or an :py:class:`AlignAttrib` object.

.. py:class:: PosAttrib

   This class represents a positional attribute. This can be accessed like a sequence of
   strings: A ``len(attr)`` returns the length of the corpus in tokens, and an ``attr[idx]``
   returns the attribute for the *idx*-th token.

   .. py:method:: getName(self)

      returns the name of the attribute

   .. py:method:: getDictionary(self)
   
      returns the :py:class:`AttrDictionary` object related to this
      attribute, wich contains string-to-number mapping and frequency
      information.

   .. py:method:: get_encoding(self)

      returns a string describing the encoding of the corpus
      (based on the information in the CQP registry)

   .. py:method:: to_unicode(self, s)

      if s is a raw string, it will decoded to a Unicode object

   .. py:method:: __getitem__(self, offset)

      returns the attribute value at position *offset* as a string.

   .. py:method:: cpos2id(self, offset)

      gives the number-coded attribute value at position *offset*.

   .. py:method:: find(self, tag)
 
      returns an :py:class:`IDList` with the occurrence positions
      of the value *tag*. Raises a :class:`KeyError` if the value is not
      present in the corpus at all.

   .. py:method:: find_list(self, tags)

      returns an :py:class:`IDList` with the occurrence positions
      for a token that has any of the attribute values in *tags*.

   .. py:method:: find_pattern(self, pat, flags=0)
      
      Matches the regular expression *pat* against corpus attributes
      and returns an :py:class:`IDList` with any matching tokens.

   .. py:method:: frequency(self, tag)

      returns the frequency of the attribute value *tag*
      in the corpus.

   .. py:method:: __len__(self)

      returns the size of the attribute (i.e., the size of the corpus in tokens).

.. py:class:: AttStruc

   represents a structural attribute. These attributes behave like a
   sequence of tuples, either tuples of ``(first,last)`` positions or
   as triples of ``(first,last,val)`` with a string attribute.

   .. py:method:: getName(self)

      returns the name of the attribute

   .. py:method:: find_all(self, tags)

      For structural attributes with a string value,
      returns an :py:class:`IDList` with the structure indices
      with all attributes whose string values match *tags*.

   .. py:method:: find_pos(self,offset)

      returns the start/end tuple for the structure
      spanning the corpus position *offset*.

   .. py:method:: cpos2struc(self,offset)

      returns the structure number for the structure
      spanning the corpus position *offset* (e.g.,
      matches a word position to its sentence number).

   .. py:method:: map_idlist(self, IDList lst not None)

      maps an :py:class:`IDList` with corpus positions to
      an :py:class:`IDList` with the corresponding structure offsets,
      removing duplicates.

   .. py:method:: __len__(self)

      returns the size of the attribute (here: the number of
      annotated spans in the corpus).

.. py:class:: AlignAttrib

   For aligned parallel corpora, an *alignment attribute* contains
   spans ``(a1,a2,b1,b2)`` that correspond to an alignment between
   positions ``a1..a2`` of the source corpus with positions ``b1..b2``
   of the aligned corpus.

   .. py:method:: getName(self)

      returns the name of the attribute

   .. py:method:: cpos2alg(self, cpos)

      finds the aligned span that corresponds to this
      corpus position. Raises a :class:`KeyError` if the corpus
      position is unaligned.

   .. py:method::  __len__(self)

      returns the size of the attribute (here: the number of
      aligned spans in the corpus).

.. py:class:: IDList

   An *IDList* corresponds to a set of corpus positions, or a set of structure
   indices. An IDList behaves like a sorted sequence of numbers (i.e.,
   ``lst[1]`` yields the second position, and ``len(lst)`` yields the size
   of the set). Boolean operations, such as ``lst1+lst2`` to get the union
   of the corpus positions, or ``lst1&lst2`` to get the intersection of corpus
   positions, are supported.

   .. py:method:: join(self, other, offset)

      returns the intersection of this IDList with *other*, shifted
      by *offset*. This can be used to find sequences of one word
      following another, or of one sentence containing a match for
      *X* and the next containing a match for *Y*.

.. py:class:: AttrDictionary

   An *AttrDictionary* corresponds to the set of values that an
   attribute can take. It is useful to retrieve IDs or frequencies
   for the possible values of that attribute.

   .. py:method:: __len__(self)

   returns the number of possible values. This and the ``__getitem``
   method make it possible to iterate over the attribute dictionary.

   .. py:method:: get_word(self, n)

   returns the attribute value corresponding to the numeric ID *n*.

   .. py:method:: get_matching(self, pat)

   returns a :py:class:`IDList` containing the numerical IDs of
   matching values.

   .. py:method:: expand_pattern(self, pat, flags=0)

   returns a list of strings for values matching the pattern.
