file_path="error3.f90"
from fparser import api as fpapi
ast = fpapi.parse(file_path, ignore_comments = False,
                  analyze = False)

