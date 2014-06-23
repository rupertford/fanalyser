from CodeAnalysis import CodeAnalysis
c = CodeAnalysis()
c.add_directory("/home/rupert/proj/jules/build/VN7.3_HadGEM3-r2.0_JULES/build/ppsrc",included_files=['*.f90','*.f'])
#c.add_directory("/home/rupert/proj/jules/build/VN7.3_HadGEM3-r2.0_JULES/build/ppsrc/UM/atmosphere/short_wave_radiation",included_files=['*.f90','*.f'])
print c
c.analyse()
c.call_tree()
