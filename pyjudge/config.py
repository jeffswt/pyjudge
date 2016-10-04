
"""
# About configuring compiler arguments

The following arguments may be passed into the compilers or intepreters, if such
events are supported by the compilers and intepreters. Otherwise they would be
implemented by the external methods of the module.

    source_file : The filename of the code.
    output_file : The output executable of the code.
    min_memory : Minimum required memory of the heap space.
    max_memory : Maximum allowed memory of the heap space.

Others would be implemented by this module.
"""

__configs = {
    'gcc_args': ['C:/Program Files (x86)/Dev-Cpp/MinGW64/bin/gcc.exe', '-O0', '-g0', '-o', '${output_file}', '${source_file}"'],
    'g++_args': ['C:/Program Files (x86)/Dev-Cpp/MinGW64/bin/g++.exe', '-O0', '-g0', '-o', '${output_file}', '${source_file}"'],
    'fpc_args': None,
    'python2_args': ['C:/Programs/Python2/python2.exe', '${source_file}'],
    'python3_args': ['C:/Programs/Python3/python3.exe', '${source_file}'],
    'javac_args': None,
}

def get_config(idx):
    if idx not in __configs:
        return None
    return __configs[idx]

def set_config(idx, dat):
    __configs[idx] = dat
    return
