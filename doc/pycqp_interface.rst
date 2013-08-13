.. -*- coding: utf-8 -*-

The PyCQP_interface Subprocess wrapper
--------------------------------------

.. py:module:: PyCQP_interface

This module was written by Jørg Asmussen to wrap a CQP subprocess
and allow the querying and processing of corpus data from within Python.

.. py:class:: CQP

   Wraps a CQP subprocess that can execute queries on corpora.

   .. py:method:: __init__(self, bin=None, options)

     Creates the CQP subprocess. The path to the CQP binary
     can be given as the _bin_ parameter.

   .. py:method:: Exec(self, cmd)

      Executes a CQP command.
      The method takes as input a command string and sends it
      to the CQP child process (and does not expect a result
      from CQP).

   .. py:method:: Query(self, cmd)

      Executes the given query with the "query lock" turned on.

   .. py:method:: Dump(self, subcorpus='Last', first=None, last=None)

      Dumps named query result into table of corpus positions (with columns
      for beginning, ending, and the marked part of the match).

   .. py:method:: Undump(self, subcorpus='Last', table=[])

      Undumps named query result from table of corpus positions

   .. py:method::  Count(self, subcorpus='Last', sort_clause=None, cutoff=1)

      Computes frequency distribution for match strings,
      based on sort clause

