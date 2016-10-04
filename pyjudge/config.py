
__configs = {
    'gcc_path': 'C:/Program Files (x86)/Dev-Cpp/MinGW64/bin/gcc.exe',
    'g++_path': 'C:/Program Files (x86)/Dev-Cpp/MinGW64/bin/g++.exe',
    'fpc_path': None,
    'python2_path': 'C:/Programs/Python2/python2.exe',
    'python3_path': 'C:/Programs/Python3/python3.exe',
    'javac_path': None,
}

def get_config(idx):
    if idx not in __configs:
        return None
    return __configs[idx]

def set_config(idx, dat):
    __configs[idx] = dat
    return
