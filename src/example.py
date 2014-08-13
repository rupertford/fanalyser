from CodeAnalysis import CodeAnalysis, Stats, Link
try:
    c = CodeAnalysis()
    c.add_directory("/home/rupert/proj/isenes2/N512_endgame_ppsrc",included_files=['*.f90','*.f'])
    #c.add_directory("/home/rupert/proj/isenes2/nemo_3.4_ppsrc",included_files=['*.f90','*.f'])
    #c.add_directory("/home/rupert/proj/um/NewDynamicsN48Bench/UM/umatmos/ppsrc",included_files=['*.f90','*.f'])
    #c.add_directory("/home/rupert/proj/jules/build/VN7.3_HadGEM3-r2.0_JULES/build/ppsrc",included_files=['*.f90','*.f'])
    #c.add_directory("/home/rupert/proj/jules/build/VN7.3_HadGEM3-r2.0_JULES/build/ppsrc/UM/atmosphere/short_wave_radiation",included_files=['*.f90','*.f'])
    print c
    parsed = c.parse()
    stats = Stats()
    stats.apply(parsed)
    stats.info
    call_tree = Link()
    parsed = call_tree.transform(parsed)
    #call_tree.dot()
    call_tree.dot("glue_rad")
    #call_tree.dot("sbc")

except RuntimeError as e:
    print "RuntimeError: {0}".format(e.message)
