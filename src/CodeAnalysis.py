''' Fortran Code Analyser 0.1. This version provides filters to allow the user
    to specify the directories and files to be analysed and counts the
    resultant number of files.

    Makes use of the
    `walkdir <http://walkdir.readthedocs.org/en/latest/#obtaining-the-module>`_
    module and requires it to be installed. The tested version is 0.3.

    Funded by the EU FP7 `ISENES2 <https://verc.enes.org/ISENES2>`_ project.

    Author Rupert Ford,
    `STFC Daresbury Laboratory <http://www.stfc.ac.uk/1903.aspx>`_, U.K.

    For example:

    >>> from CodeAnalysis import CodeAnalysis
    >>> c = CodeAnalysis()
    >>> c.add_directory("/home/rupert/proj/jules")
    >>> print c
    >>> c.analyse()
'''

class CodeAnalysis(object):
    ''' Top level analysis class. Sets up the required directory information
        and provides access to the analyser. '''

    def __init__(self):
        self._directory_info = []

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
                      included_files = ['*.[fF]90', '*.[fF]'],
                      excluded_dirs = ['.*']):
        ''' Adds a directory for analysis.

        :param my_directory: The directory name to add.
        :type my_directory: str.
        :param recurse_depth: Number of directories to recurse. 'None'
                              (the default) means there is no limit.
        :type recurse_depth: int.
        :param included_files: a list of regexp's determining the file names
                               to examine. The default is all .f90 .F90 .f
                               and .F files.
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

    def analyse(self):
        ''' Print out the number of files matched.'''
        from walkdir import filtered_walk, file_paths
        for dir_info in self._directory_info:
            files = file_paths(filtered_walk(dir_info["directory"],
                                   included_files = dir_info["included_files"],
                                   excluded_dirs = dir_info["excluded_dirs"],
                                   depth = dir_info["depth"]))
            #print '\n'.join(files)
            print "Found "+str(len(list(files)))+" matching files"
