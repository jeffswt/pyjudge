
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
    # 'tmp_dir': 'C:/Users/Administrator/AppData/Local/Temp/PyJudgeTemp/',
    'tmp_dir': './PyJudgeTemp/',
    'max_output': 64*1024*1024, # 64 MB Maximum allowed output
    'table_max_lines': 20,
    'table_max_linewidth': 256,
    'gcc_args': ['gcc', '-O0', '-g0', '-Wall', '-o', '{output_file}', '{source_file}'],
    'g++_args': ['g++', '-O0', '-g0', '-Wall', '-o', '{output_file}', '{source_file}'],
    'fpc_args': ['fpc', '{source_file}', '-o{output_file}'],
    'python2_args': ['python2', '{source_file}'],
    'python3_args': ['python3', '{source_file}'],
    'javac_args': ['javac'],
}

def get_config(idx):
    if idx not in __configs:
        return None
    return __configs[idx]

def set_config(idx, dat):
    __configs[idx] = dat
    return
