#! /usr/bin/python
# coding: iso-8859-1

# Name of this module: PyCQP
# Version 2.0 (Febr. 2008)
# Joerg Asmussen, DSL

# for Py3 compatibility
from __future__ import print_function

# Import external standard Python modules used by this module:
import sys
import os
import re
import random
import string
import time
import thread
import logging

# Modules for running CQP as child process and pipe i/o
# (standard in newer Python):
import subprocess
import select

logger = logging.getLogger(__name__)

# GLOBAL CONSTANTS OF MODULE:
cProgressControlCycle = 30  # secs between each progress control cycle
cMaxRequestProcTime = 40  # max secs for processing a user request

# ERROR MESSAGE TYPES:


class ErrCQP:
    '''
    exception thrown by the CQP wrapper
    '''
    def __init__(self, msg):
        self.msg = msg.rstrip()


class ErrKilled:

    def __init__(self, msg):
        self.msg = msg.rstrip()


class CQP:

    """
    Wrapper for CQP.
    """

    def _progressController(self):
        """
        CREATED: 2008-02
        This method is run as a thread.
        At certain intervals (cProgressControlCycle), it controls how long the
        CQP process of the current user has spent on processing this user's
        latest CQP command. If this time exceeds a certain maximun
        (cMaxRequestProcTime), this method kills the CQP process.
        """
        self.runController = True
        while self.runController:
            time.sleep(cProgressControlCycle)
            if self.execStart is not None:
                if time.time() - self.execStart > \
                        cMaxRequestProcTime * self.maxProcCycles:
                    logger.warning('Kill blocking CQP process (id=%d)'%(
                        self.CQP_process.pid))
                    # os.kill(self.CQP_process.pid, SIGKILL) - doesn't work!
                    os.popen("kill -9 " + str(self.CQP_process.pid))  # works!
                    logger.info('Process %d killed.'%(self.CQP_process.pid))
                    self.CQPrunning = False
                    break

    def __init__(self, bin=None, options=''):
        self.execStart = time.time()
        self.maxProcCycles = 1.0
        # start CQP as a child process of this wrapper
        if bin is not None:
            logger.error('You need to give the path to the CQP binary')
            raise RuntimeError()
        self.CQP_process = subprocess.Popen(bin + ' ' + options,
                                            shell=True,
                                            stdin=subprocess.PIPE,
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE,
                                            close_fds=True)
        self.CQPrunning = True
        thread.start_new_thread(self._progressController, ())
        # "cqp -c" should print version on startup:
        version_string = self.CQP_process.stdout.readline()
        version_string = version_string.rstrip()  # Equivalent to Perl's chomp
        logger.info('CQP version: %s'%(version_string))
        version_regexp = re.compile(
            r'^CQP\s+(?:\w+\s+)*([0-9]+)\.([0-9]+)(?:\.b?([0-9]+))?(?:\s+(.*))?$')
        match = version_regexp.match(version_string)
        if not match:
            logger.critical('CQP backend did not start up')
            sys.exit(1)
        self.major_version = int(match.group(1))
        self.minor_version = int(match.group(2))
        self.beta_version = int(match.group(3))
        self.compile_date = match.group(4)

        # We need cqp-2.2.b41 or newer (for query lock):
        if not (
            self.major_version >= 3
            or (self.major_version == 2
                and self.minor_version == 2
                and self.beta_version >= 41)
        ):
            logger.critical('Need at least CQP 2.2.41 (you have %s)'%(
                version_string))
            sys.exit(1)

        # Error handling:
        self.error_handler = None
        self.status = 'ok'
        self.error_message = ''  # we store compound error messages as a STRING
        self.errpipe = self.CQP_process.stderr.fileno()

        # Debugging (prints more or less everything on stdout)
        self.debug = False

        # CQP defaults:
        self.Exec('set PrettyPrint off')
        self.execStart = None

    def terminate(self):
        """
        Terminate controller thread, must be called before deleting CQP
        """
        self.execStart = None
        self.runController = False

    def setProcCycles(self, procCycles):
        logger.info('setting procCycles to %s'%(procCycles,))
        self.maxProcCycles = procCycles
        return int(self.maxProcCycles * cMaxRequestProcTime)

    def __del__(self):
        if self.CQPrunning:
            # print "Deleting CQP with pid", self.CQP_process.pid, "...",
            self.CQPrunning = False
            self.execStart = time.time()
            logger.debug('Shutting down CQP backend')
            self.CQP_process.stdin.write('exit;')  # exits CQP backend
            logger.debug('Done, CQP object deleted')
            self.execStart = None

    def Exec(self, cmd):
        """
        Executes CQP command.
        The method takes as input a command string and sends it
        to the CQP child process
        """
        self.execStart = time.time()
        self.status = 'ok'
        cmd = cmd.rstrip()  # Equivalent to Perl's 'chomp'
        cmd = re.sub(r';\s*$', r'', cmd)
        logger.debug('CQP cmd: "%s"'%(cmd,))
        try:
            self.CQP_process.stdin.write(cmd + '; .EOL.;\n')
        except IOError:
            return None
        # In CQP.pm lines are appended to a list @result.
        # This implementation prefers a string structure instead
        # because output from this module is meant to be transferred
        # accross a server connection. To enable the development of
        # client modules written in any language, the server only emits
        # strings which then are to be structured by the client module.
        # The server does not emit pickled data according to some
        # language dependent protocol.
        result = ''
        while self.CQPrunning:
            response_line = self.CQP_process.stdout.readline()
            response_line = response_line.strip()  # strip off whitespace from start and end of line
            if re.match(r'-::-EOL-::-', response_line):
                if self.debug:
                    logger.debug('CQP eol')
                break
            if self.debug:
                logger.debug('CQP out: "%s"'%(response_line,))
            if response_line != '':
                result = result + response_line + '\n'
        result = result.rstrip()  # strip off whitespace from EOL (\n)
        self.check_for_error_message()
        self.execStart = None
        return result

    def Query(self, query):
        """
        Executes query in safe mode (query lock)
        """
        result = []
        key = str(random.randint(1, 1000000))
        errormsg = ''  # collect CQP error messages AS STRING
        status_ok = True	  # check if any error occurs
        self.Exec('set QueryLock ' + key)  # enter query lock mode
        if self.status != 'ok':
            errormsg = errormsg + self.error_message
            status_ok = False
        result = self.Exec(query)
        if self.status != 'ok':
            errormsg = errormsg + self.error_message
            status_ok = status_ok and False
        self.Exec('unlock ' + key)  # unlock with random key
        if self.status != 'ok':
            errormsg = errormsg + self.error_message
            status_ok = status_ok and False
        # Set error status & error message:
        if status_ok:
            self.status = 'ok'
        else:
            self.status = 'error'
            self.error_message = errormsg
        return result

    def Dump(self, subcorpus='Last', first=None, last=None):
        """
        Dumps named query result into table of corpus positions
        """
        if first is not None and last is None:
            last = first
        elif last is not None and first is None:
            first = last
        if first is not None:
            first = str(first)
            last = str(last)
            regexp = re.compile(r'^[0-9]+$')
            if (not regexp.match(first)) or (not regexp.match(last)):
                logger.error('Dump(): Invalid value for first (%s) or last (%s)'%(
                    first, last))
                sys.exit(1)
        matches = []
        result = re.split(r'\n', self.Exec('dump ' + subcorpus +
                                           " " + first + " " + last))
        for line in result:
            matches.append(re.split(r'\t', line))
        return matches

    def Undump(self, subcorpus='Last', table=[]):
        """
        Undumps named query result from table of corpus positions
        """
        wth = ''  # undump with target and keyword
        n_el = None  # number of anchors for each match
                    # (will be determined from first row)
        n_matches = len(table)  # number of matches (= remaining arguments)
        # We have to read undump table from temporary file:
        #TODO: this sounds like a race condition waiting to happen.
        # replace with something like mkstemp
        filename = '/tmp/pycqp_undump.tmp'
        if os.path.exists(filename):
            os.chmod(filename, 0o666)
        tf = open(filename, 'w')
        tf.write(str(n_matches) + '\n')
        for row in table:
            row_el = len(row)
            if n_el is not None:
                n_el = row_el
                if (n_el < 2) or (n_el > 4):
                    logger.error('Undump: table has %d columns (should be between 2 and 4)'%(
                        n_el,))
                    sys.exit(1)
                if n_el >= 3:
                    wth = 'with target'
                if n_el == 4:
                    wth = wth + ' keyword'
            elif row_el != n_el:
                logger.error('Undump: row has %d instead of %d columns (should be same across rows)'%(
                    row_el, n_el))
                sys.exit(1)
            tf.write(string.join(row, '\t') + '\n')
        tf.close()
        # Send undump command with filename of temporary file:
        self.Exec("undump " + subcorpus + " " + wth + " < '" + filename + "'")
        os.remove(filename)

    def Group(self, subcorpus='Last',
              spec1='match.word', spec2='', cutoff='1'):
        """
        Computes frequency distribution over attribute values
        (single values or pairs) using group command;
        note that the arguments are specified in the logical order,
        in contrast to "group"
        """
        spec2_regexp = re.compile(r'^[0-9]+$')
        if spec2_regexp.match(spec2):
            cutoff = spec2
            spec2 = ''
        spec_regexp = re.compile(
            r'^(match|matchend|target[0-9]?|keyword)\.([A-Za-z0-9_-]+)$')
        match = spec_regexp.match(spec1)
        if not match:
            logger.error('Group: invalid key %s'%(spec1,))
            sys.exit(1)
        spec1 = match.group(1) + ' ' + match.group(2)
        if spec2 != '':
            match = spec_regexp(spec2)
            if not match:
                logger.error('Group: invalid key %s'%(spec2,))
                sys.exit(1)
            spec2 = match.group(1) + ' ' + match.group(2)
            cmd = 'group ' + subcorpus + ' ' + spec2 + ' by ' + spec1 + \
                ' cut ' + cutoff
        else:
            cmd = 'group ' + subcorpus + ' ' + spec1 + ' cut ' + cutoff
        result = self.Exec(cmd)
        rows = []
        for line in result:
            rows.append(re.split(r'\t', line))
        return rows

    def Count(self, subcorpus='Last', sort_clause=None, cutoff=1):
        """
        Computes frequency distribution for match strings,
        based on sort clause
        """
        if sort_clause is None:
            logger.error('Count: sort_clause parameter undefined')
            sys.exit(1)
        return self.Exec('count ' + subcorpus + ' ' + sort_clause +
                         ' cut ' + str(cutoff))
    # We don't want to return a data structure other than a string in order to
    # send it across a server line without pickling.
    # The work of structuring the data must be done by the client part
    #		  rows = []
    #		  for line in result:
    #			  size, first, string = re.split(r'\t', line)
    #			  rows.append([size, string, first, int(first) + int(size) - 1])
    #		  return rows

    def check_for_error_message(self):
        """
        Checks CQP's stderr stream for error messages
        (returns true if there was an error)
        OBS! In CQP.pm the error_message is stored in a list,
        In PyCQP_interface.pm we use a string (which better can be sent
        accross the server line)
        """
        ready = select.select([self.errpipe], [], [], 0)
        if self.errpipe in ready[0]:
            # We've got something on stderr -> an error must have occurred:
            self.status = 'error'
            self.error_message = self.read_error_message()
        return not self.status_ok()

    def read_error_message(self):
        """
        Reads all available lines from CQP's stderr stream
        """
        return os.read(self.errpipe, 16384)

    def get_status(self):
        """
        Reads the CQP object's (error) status
        """
        return self.status

    def status_ok(self):
        """
        Simplified interface for checking for CQP errors
        """
        if self.CQPrunning:
            return (self.get_status() == 'ok')
        else:
            return False

    def get_last_error(self):
        """
        Returns the CQP error message
        """
        if self.CQPrunning:
            return ErrCQP(self.error_message)
        else:
            msgKilled = '**** CQP KILLED ***\n' + \
                'CQP COULD NOT PROCESS YOUR REQUEST\n'
            return ErrKilled(msgKilled + self.error_message)

    def handle_error(self, msg):
        """
        Processes/outputs error messages
        (optionally run through user-defined error handler)
        """
        if self.error_handler is not None:
            self.error_handler(msg)
        else:
            logger.error(msg)

    def set_error_handler(self, handler=None):
        """
        Sets user-defined error handler
        """
        self.error_handler = handler

    def set_debugging(self, on=False):
        """
        Switches debugging output on/off
        """
        prev = self.debug
        self.debug = on
        return prev
