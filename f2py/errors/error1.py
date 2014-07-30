from fparser.readfortran import FortranFileReader
reader = FortranFileReader('error1.f90')
reader.next()
print reader.next()
