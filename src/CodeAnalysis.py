'''Fortran Code Analyser 0.2. This version provides filters to allow
    the user to specify the directories and files. It then parses and
    analyses these files building up an internal hierarchy of
    subroutines and calls. The analysis provides some basic
    information about the code in terms of number of subroutine, lines
    of code etc. The subroutines and calls are then linked
    together. The linking allows a separate call method to return the
    call tree using the dot graph format.

    Makes use of the
    `walkdir <http://walkdir.readthedocs.org/en/latest/#obtaining-the-module>`_
    module and requires it to be installed. The tested version is 0.3.

    Makes use of the parser in `f2py <http://code.google.com/p/f2py>`_

    Funded by the EU FP7 `ISENES2 <https://verc.enes.org/ISENES2>`_ project.

    Author Rupert Ford,
    `STFC Daresbury Laboratory <http://www.stfc.ac.uk/1903.aspx>`_, U.K.

    For example:

    >>> from CodeAnalysis import CodeAnalysis
    >>> c = CodeAnalysis()
    >>> c.add_directory("/home/rupert/proj/jules")
    >>> print c
    >>> parsed = c.parse()

'''

class CodeAnalysis(object):
    ''' Top level analysis class. Sets up the required directory information
        and provides access to the analyser. '''

    def __init__(self):
        self._directory_info = []
        self._files=[]

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

    def parse(self, link = False):
        ''' Parse all of the matched files, print out the path of each one and
            whether the parsing was successful. Print a summary at the end. By
            default also link calls and subroutines together'''
        try:
            from walkdir import filtered_walk, file_paths
        except ImportError:
            raise RuntimeError("CodeAnalysis requires walkdir <http://walkdir.readthedocs.org/en/latest/#obtaining-the-module> to be installed")
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
            print "{0} out of {1} files successfully examined". \
                  format(str(success), str(len(list_files)))
        return self._files

class CodeAnalysisUtilBase(object):

    @property
    def name(self):
        raise NotImplementedError, "name method should be implemented"

    @property
    def description(self):
        raise NotImplementedError, "description method should be implemented"

class CodeAnalysisTransform(CodeAnalysisUtilBase):

    def transform(self,files):
        raise NotImplementedError, "transform method should be implemented"
        return files

class CodeAnalysisOperator(CodeAnalysisUtilBase):

    def apply(self,files):
        raise NotImplementedError, "apply method should be implemented"


class Link(CodeAnalysisTransform):

    def __init__(self):
        self._symbol_table={}
        self._files=None

    @property
    def name(self):
        return "link"

    @property
    def description(self):
        return "links calls and subroutines. Modifies the files object to add link information."

    def transform(self,files):

        print "linking:",
        self._files=files

        # create the symbol table
        for my_file in self._files:
            for subroutine in my_file.subroutines:
                self._symbol_table[subroutine.name.lower()]=subroutine

        for my_file in self._files:
            for subroutine in my_file.subroutines:
                for call in subroutine.calls:
                    if call.name.lower() in self._symbol_table.keys():
                        my_subroutine=self._symbol_table[call.name.lower()]
                        call.link=my_subroutine
                        my_subroutine.add_link(call)

        print "done"
        return files

    def dot(self,sub_name=""):

        if self._files is None:
            raise RuntimeError, "run the apply method first"

        if sub_name not in self._symbol_table and sub_name != "":
            raise RuntimeError, "specified subroutine is not in the code"

        ''' return the call tree as a dot file '''
        if sub_name == "":
            print "digraph G {"
            for my_file in self._files:
                for subroutine in my_file.subroutines:
                    subroutine.call_tree()
                for module in my_file.modules:
                    for subroutine in module.subroutines:
                        subroutine.call_tree()
            print "}"
        else:
            print "digraph G {"
            self._x(self._symbol_table[sub_name],[])
            print "}"

    def _x(self, subroutine, called_names):
        subroutine.call_tree()
        for call in subroutine.calls:
            if call.name not in called_names:
                called_names.append(call.name)
                if call.link is not None:
                    self._x(call.link, called_names)

    def info(self):
        # TBD info about orphans and unresolved calls
        pass

class Stats(CodeAnalysisOperator):

    def __init__(self):
        self._n_files_ok = 0
        self._n_files_empty = 0
        self._n_files_failed = 0
        self._n_modules = 0
        self._n_modules_no_subroutines = 0
        self._n_subroutines_outside_modules = 0
        self._n_subroutines_in_modules = 0
        self._n_statements = 0
        self._statement_count_bin = {}
        self._applied = False
        self._n_comments = 0
        self._n_type_decls = 0
        self._n_code_statements = 0

    @property
    def name(self):
        return "Statistics"

    @property
    def description(self):
        return "Statistics about the code"

    def apply(self,files):
        ''' determine stats about the code '''

        print "Creating stats:",
        import sys
        sys.stdout.flush()
        for my_file in files:
            if not my_file.parsed_ok:
                self._n_files_failed += 1            
            else:
                self._n_files_ok += 1
                if my_file.is_empty:
                    self._n_files_empty += 1
                else:
                    self._n_modules += len(my_file.modules)
                    self._n_subroutines_outside_modules += len(my_file.subroutines)
                    for my_module in my_file.modules:
                        if len(my_module.subroutines) == 0:
                            self._n_modules_no_subroutines += 1
                        else:
                            self._n_subroutines_in_modules += len(my_module.subroutines)

                    # walk through all statements in the current file
                    from fparser import api
                    for statement, depth in api.walk(my_file._ast, -1):
                        self._n_statements += 1
                        type_statement = type(statement)
                        if type_statement not in self._statement_count_bin:
                            self._statement_count_bin[type_statement] = 1
                        else:
                            self._statement_count_bin[type_statement] += 1
                        if "fparser.statements.Comment" in str(type_statement):
                            self._n_comments += 1
                        elif "fparser.typedecl_statements." in str(type_statement):
                            self._n_type_decls += 1
                        elif "fparser.statements." in str(type_statement) or "fparser.block_statements." in str(type_statement):
                            self._n_code_statements += 1
        self._applied=True
        print "done"
        sys.stdout.flush()

    @property
    def info(self):
        if not self._applied:
            raise RuntimeError("method info must be called first")

        print "Total number of ..."
        print "    files                       {0}".format(self._n_files_ok + self._n_files_failed)
        print "    files successfully parsed   {0}".format(self._n_files_ok-self._n_files_empty)
        print "    files failed to parse       {0}".format(self._n_files_failed)
        print "    files that are empty        {0}".format(self._n_files_empty)
        print ""
        # TBD print "    programs              {0}".format(0)
        print "    modules                     {0}".format(self._n_modules)
        print "    modules with subroutines    {0}".format(self._n_modules - self._n_modules_no_subroutines)
        print "    modules without subroutines {0}".format(self._n_modules_no_subroutines)
        print ""
        print "    subroutines                 {0}".format(self._n_subroutines_outside_modules+self._n_subroutines_in_modules)
        print "    subroutines outside modules {0}".format(self._n_subroutines_outside_modules)
        print "    subroutines inside modules  {0}".format(self._n_subroutines_in_modules)
        print ""
        print "    statements                  {0}".format(self._n_statements)
        print "    comments                    {0}".format(self._n_comments)
        print "    declarations                {0}".format(self._n_type_decls)
        print "    code statements             {0}".format(self._n_code_statements)
        print ""
        print "   ",
        for statement in sorted(self._statement_count_bin, key=self._statement_count_bin.__getitem__, reverse = True):
            print str(statement).split("'")[1].split(".")[2],self._statement_count_bin[statement],
        print ""

class File(object):
    ''' a class containing information about a particular fortran file '''

    def __init__(self):
        self._modules=[] # a list of modules contained in this file
        self._subroutines=[] # a list of subroutines contained in this file
        self._ast=None
        self._parsed=False
        self._parsed_ok=None
        self._is_empty=False

    @property
    def parsed(self):
        return self._parsed

    @property
    def is_empty(self):
        if not self._parsed:
            raise RuntimeError("Error")
        return self._is_empty

    @property
    def parsed_ok(self):
        if not self._parsed:
            raise RuntimeError("Error")
        return self._parsed_ok

    @property
    def subroutines(self):
        if not self._parsed:
            raise RuntimeError("Error")
        return self._subroutines

    @property
    def modules(self):
        if not self._parsed:
            raise RuntimeError("Error")
        return self._modules

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
        from fparser import api

        if not self._parsed:
            raise RuntimeError("Cannot analyse when you have not yet parsed")
        if not self._parsed_ok:
            raise RuntimeError("Cannot analyse when the parsing failed")

        if len(self._ast.content)==0:
            print "Analysis found nothing in the file."
            self._is_empty=True
            return

        for child, depth in api.walk(self._ast, -1):
            if isinstance(child,fparser.block_statements.Program):
                pass
                #print "  FOUND MAIN PROGRAM", child.name
            if isinstance(child,fparser.block_statements.Module):
                my_module=Module()
                my_module.parse(child)
                my_module.analyse()
                self._modules.append(my_module)
                #print "  FOUND MODULE", child.name
            if isinstance(child,fparser.block_statements.Subroutine):
                my_subroutine=Subroutine()
                my_subroutine.parse(child)
                my_subroutine.analyse()
                self._subroutines.append(my_subroutine)
            if isinstance(child,fparser.block_statements.Function):
                pass
                #print "  FOUND FUNCTION", child.name
            if isinstance(child,fparser.block_statements.BlockData):
                pass
                #print "  FOUND BLOCK DATA", child.name

class Module(object):
    def __init__(self):
        self._subroutines=[] # a list of subroutines contained in this module

    @property
    def name(self):
        return self._ast.name
    @property
    def subroutines(self):
        return self._subroutines

    def parse(self,ast):
        self._ast=ast

    def analyse(self):
        from fparser import api
        import fparser
        for stmt, depth in api.walk(self._ast, -1):
            if isinstance(stmt,fparser.block_statements.Subroutine):
                my_subroutine=Subroutine()
                my_subroutine.parse(stmt)
                my_subroutine.analyse()
                self._subroutines.append(my_subroutine)
    
class Subroutine(object):
    def __init__(self):
        self._calls = [] # a list of the calls made by this subroutine
        self._link_calls = [] # a list of calls that call this subroutine

    def parse(self,ast):
        self._ast=ast

    def analyse(self):
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
