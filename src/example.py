# BSD 3-Clause License
#
# Copyright (c) 2017, Science and Technology Failities Council
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# Author R. Ford STFC Daresbury Lab.
#
from CodeAnalysis import CodeAnalysis, Stats, Link
try:
    c = CodeAnalysis()
    #c.add_directory("/home/rupert/proj/isenes2/N512_endgame_ppsrc",included_files=['*.f90','*.f'])
    c.add_directory("/home/rupert/proj/isenes2/code_analysis/ppsrc-nemo",included_files=['*.f90','*.f'])
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
    #call_tree.dot("glue_rad")
    call_tree.dot("sbc")

except RuntimeError as e:
    print "RuntimeError: {0}".format(e.message)
