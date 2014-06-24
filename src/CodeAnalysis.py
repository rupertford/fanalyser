''' Fortran Code Analyser 0.2. This version provides filters to allow the user
    to specify the directories and files. It then parses and analyses these
    files building up an internal hierarchy of subroutines and calls. The
    subroutines and calls are then linked together and a call tree returned
    using the dot graph format.

    *** 0.2, when complete, will return a call tree using dot. Currently just creates and links the basic objects ***

    Makes use of the
    `walkdir <http://walkdir.readthedocs.org/en/latest/#obtaining-the-module>`_
    module and requires it to be installed. The tested version is 0.3.

    Makes use of the parser in f2py (more info here ***)

    Funded by the EU FP7 `ISENES2 <https://verc.enes.org/ISENES2>`_ project.

    Author Rupert Ford,
    `STFC Daresbury Laboratory <http://www.stfc.ac.uk/1903.aspx>`_, U.K.

    For example:

    >>> from CodeAnalysis import CodeAnalysis
    >>> c = CodeAnalysis()
    >>> c.add_directory("/home/rupert/proj/jules")
    >>> print c
    >>> c.analyse()
    >>> c.call_tree()
'''

class CodeAnalysis(object):
    ''' Top level analysis class. Sets up the required directory information
        and provides access to the analyser. '''

    def __init__(self):
        self._directory_info = []
        self._files=[]
        self._symbol_table={}

    def __str__(self):
        result = "CodeAnalysis:\n"
        if self._directory_info == []:
            return result + " no directory information specified."
        for idx, dir_info in enumerate(self._directory_info):
            result += "    directory "+str(idx+1) + "\n"
            result += "        path=" + dir_info["directory"] + "\n"
            result += "        included files=" + \
                      str(dir_info["included_files"]) \
                      + "\n"
            result += "        excluded dirs=" + \
                      str(dir_info["excluded_dirs"]) \
                      + "\n"
            if dir_info["depth"] == None:
                result += "        recursion depth='unlimited'"
            else:
                result += "        recursion depth=" + str(dir_info("depth"))
            result += "\n"
        return result

    def add_directory(self, my_directory, recurse_depth = None,
                      included_files = ['*.f90', '*.f'],
                      excluded_dirs = ['.*']):
        ''' Adds a directory for analysis.

        :param my_directory: The directory name to add.
        :type my_directory: str.
        :param recurse_depth: Number of directories to recurse. 'None'
                              (the default) means there is no limit.
        :type recurse_depth: int.
        :param included_files: a list of regexp's determining the file names
                               to examine. The default is all .f90 and .f
                               files.
        :type included_files: list of regexps
        :param excluded_dirs: a list of regexps of directories to ignore.
                              The default is to ignore all dirs starting with
                              "."
        :type excluded_dirs: list of regexps
        '''
        dir_map = {}
        dir_map["directory"] = my_directory
        dir_map["depth"] = recurse_depth
        dir_map["included_files"] = included_files
        dir_map["excluded_dirs"] = excluded_dirs
        self._directory_info.append(dir_map)

    def analyse(self,link=True):
        ''' Parse all of the matched files, print out the path of each one and
            whether the parsing was successful. Print a summary at the end. By
            default also link calls and subroutines together'''
        from walkdir import filtered_walk, file_paths
        for dir_info in self._directory_info:
            files = file_paths(filtered_walk(dir_info["directory"],
                                   included_files = dir_info["included_files"],
                                   excluded_dirs = dir_info["excluded_dirs"],
                                   depth = dir_info["depth"]))
            #print '\n'.join(files)
            list_files = list(files)
            print "Found {0} matching files in directory '{1}'" \
                  .format(str(len(list_files)), dir_info["directory"])
            success = 0
            for idx, file_path in enumerate(list_files):
                my_file=File()
                ok=my_file.parse(file_path)
                if ok:
                    my_file.analyse()
                    self._files.append(my_file)
                    print "[{0}/{1}][ok] {2}".format(idx + 1,
                                                     len(list_files),
                                                     file_path)
                    success += 1
                else:
                    print "[{0}/{1}][failed] {2}".format(idx + 1,
                                                         len(list_files),
                                                         file_path)
            print "{0} out of {1} files successfully parsed". \
                  format(str(success), str(len(list_files)))
        if link:
            self.link()
               
    def link(self):
        for my_file in self._files:
            for subroutine in my_file.subroutines:
                # TODO: check for same symbol more than once?
                self._symbol_table[subroutine.name.lower()]=subroutine

        for my_file in self._files:
            for subroutine in my_file.subroutines:
                for call in subroutine.calls:
                    if call.name.lower() in self._symbol_table.keys():
                        my_subroutine=self._symbol_table[call.name.lower()]
                        call.link=my_subroutine
                        my_subroutine.add_link(call)
        print "link complete"

    def call_tree(self):
        ''' return the call tree as a dot file '''
        print "digraph G {"
        for my_file in self._files:
            for subroutine in my_file.subroutines:
                subroutine.call_tree()
        print "}"

class File(object):
    ''' a class containing information about a particular fortran file '''

    def __init__(self):
        self._modules=[] # a list of modules contained in this file
        self._subroutines=[] # a list of subroutines contained in this file
        self._ast=None
        self._parsed=False
        self._parsed_ok=None

    @property
    def subroutines(self):
        return self._subroutines

    def parse(self,file_path):
        ''' parse the file provided using fparser '''
        self._parsed=True
        try:
            import fparser
            from fparser import parsefortran
            from fparser import api as fpapi
            fparser.parsefortran.FortranParser.cache.clear()
            fparser.logging.disable('CRITICAL')
            self._ast = fpapi.parse(file_path, ignore_comments = False,
                              analyze = False)
            if self._ast == None:
                ''' parser does not necessarily throw an error if it fails
                    to parse. Instead it may return an empty ast. '''
                self._parsed_ok=False
            else:
                self._parsed_ok=True
            return self._parsed_ok
        except KeyboardInterrupt:
            print "Control-C pressed, aborting"
            exit(1)
        except:
            self._parsed_ok=False
            return self._parsed_ok

    def analyse(self):
        ''' Creates program, module function and/or subroutine objects as
            appropriate '''
        import fparser

        if not self._parsed:
            raise RuntimeError("Cannot analyse when you have not yet parsed")
        if not self._parsed_ok:
            raise RuntimeError("Cannot analyse when the parsing failed")

        found=False
        for child in self._ast.content:
            # TODO: look for function too
            if isinstance(child,fparser.block_statements.Program):
                found=True
                #print "  FOUND MAIN PROGRAM", child.name
            if isinstance(child,fparser.block_statements.Module):
                found=True
                #print "  FOUND MODULE", child.name
            if isinstance(child,fparser.block_statements.Subroutine):
                found=True
                my_subroutine=Subroutine()
                my_subroutine.parse(child)
                my_subroutine.analyse()
                self._subroutines.append(my_subroutine)
            if isinstance(child,fparser.block_statements.Function):
                found=True
                #print "  FOUND FUNCTION", child.name
            if isinstance(child,fparser.block_statements.BlockData):
                found=True
                #print "  FOUND BLOCK DATA", child.name
        if not found:
            print "Analysis found nothing in the file."


class Module(object):
    def __init__(self):
        self._subroutines=[] # a list of subroutines contained in this module

    def parse(self,ast):
        self._ast=ast

    def analyse(self):
        pass
    
class Subroutine(object):
    def __init__(self):
        self._calls = [] # a list of the calls made by this subroutine
        self._link_calls = [] # a list of calls that call this subroutine

    def parse(self,ast):
        self._ast=ast

    def analyse(self):
        pass
        from fparser import api
        import fparser
        for stmt, depth in api.walk(self._ast, -1):
            if isinstance(stmt,fparser.statements.Call):
                # currently one object per call even if they call the same
                # subroutine
                my_call=Call()
                my_call.parse(stmt)
                my_call.analyse()
                self._calls.append(my_call)

    @property
    def name(self):
        return self._ast.name

    @property
    def calls(self):
        return self._calls

    def add_link(self,call):
        self._link_calls.append(call)

    def call_tree(self):
        unique_names=[]
        self.name+";"
        for call in self.calls:
            if call.link is not None:
                if call.link.name not in unique_names:
                    unique_names.append(call.link.name)
                    print self.name,"->",call.link.name+";"
            

class Call(object):
    def __init__(self):
        self._link_subroutine=None
    def parse(self,stmt):
        self._stmt=stmt
    def analyse(self):
        pass
    @property
    def name(self):
        return self._stmt.designator
    @property
    def link(self):
        return self._link_subroutine
    @link.setter
    def link(self,subroutine):
        self._link_subroutine=subroutine
