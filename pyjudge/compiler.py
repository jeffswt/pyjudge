
import os
from . import config
from . import process
from . import tmpmgmt

class CompilerError(Exception):
    def __init__(self, *args):
        self.args = args
        return
    pass

def wrap_compiler(input_class):
    class CompilerWrapper(input_class):
        def __init__(self, *args, **kwargs):
            ret = input_class.__init__(self, *args, **kwargs)
            self.__sequence = 0
            return ret
        def compile(self, *args, **kwargs):
            if self.__sequence != 0:
                raise AttributeError('Source code already compiled')
            ret = input_class.compile(self, *args, **kwargs)
            self.__sequence = 1
            return ret
        def execute(self, *args, **kwargs):
            if self.__sequence != 1:
                raise AttributeError('Source code hadn\'t been compiled')
            ret = input_class.execute(self, *args, **kwargs)
            return ret
        pass
    return CompilerWrapper

@wrap_compiler
class Compiler:
    """ Basic compiler, all functions defined here when invoked without further
    definition would raise a NotImplementedError. Use inheritance for this
    compiler, and should not be used as an instance. """

    def __init__(self, source_path):
        self.source_path = source_path
        return

    def compile(self, override_command=None):
        """ compile() -- Compile the source code into executable. """
        raise NotImplementedError()

    def execute(self, stdin=''):
        """ execute() -- Execute compiled executable. """
        raise NotImplementedError()
    pass

@wrap_compiler
class FileHandleCompiler(Compiler):
    """ Handles a file in Unicode encoding. Does not actually compile files,
    only provides a compiler-like interface for files' handling. """

    def compile(self, override_command=None):
        try:
            self.__file_handle = open(self.source_path, 'r')
        except Exception:
            raise CompilerError('Unable to open file')
        ret_result = {
            'return_code': 0,
            'output': ''
        }
        return ret_result

    def execute(self, **kwargs):
        ret_result = {
            'time': 0,
            'memory': 0,
            'return_code': 0,
            'stdout': self.__file_handle.read(),
            'stderr': '',
        }
        return ret_result
    pass

@wrap_compiler
class PythonCompiler(Compiler):
    """ Python compiler, a wrapper for Python 2 code execution. """

    def __init__(self, source_path, version_number):
        Compiler.__init__(self, source_path)
        if version_number == 2:
            self.__python_args = config.get_config('python2_args')
        elif version_number == 3:
            self.__python_args = config.get_config('python3_args')
        else:
            raise AttributeError('Unknown Python version')
        return

    def compile(self, override_command=None):
        try:
            f_handle = open(self.source_path, 'r')
            f_handle.close()
        except:
            raise CompilerError('Unable to open file')
        if override_command:
            self.__python_args = override_command
        ret_result = {
            'return_code': 0,
            'output': ''
        }
        return ret_result

    def execute(self, **kwargs):
        args = self.__python_args
        for i in range(0, len(args)):
            args[i] = args[i].format(source_file=self.source_path)
        # Formatted arguments, executing
        p = process.Process(
            process_args=args,
            **kwargs
        )
        return p.execute()
    pass

@wrap_compiler
class Python2Compiler(PythonCompiler):
    """ Python 2 compiler, wraps PythonCompiler. """
    def __init__(self, source_path):
        return PythonCompiler.__init__(self, source_path, 2)
    pass

@wrap_compiler
class Python3Compiler(PythonCompiler):
    """ Python 3 compiler, wraps PythonCompiler. """
    def __init__(self, source_path):
        return PythonCompiler.__init__(self, source_path, 3)
    pass

@wrap_compiler
class CLikeCompiler(Compiler):
    """ C / C++ / C-Style compiler, invokes GCC or G++, used this as an
    abbreviation for fewer code lines. """

    def __init__(self, source_path, language_type):
        Compiler.__init__(self, source_path)
        if language_type == 'C':
            self.__c_args = config.get_config('gcc_args')
        elif language_type == 'C++':
            self.__c_args = config.get_config('g++_args')
        else:
            raise AttributeError('Unknown C/Style language type')
        return

    def compile(self, override_command=None):
        args = self.__c_args
        out_file = tmpmgmt.create_tmpfile()
        self.__c_executable = out_file
        for i in range(0, len(args)):
            args[i] = args[i].format(
                source_file=self.source_path,
                output_file=out_file)
            pass
        # Some hotfixes on Windows...
        try: os.rename(out_file + '.exe', out_file)
        except: pass
        # Formatted arguments, executing
        proc = process.Process(
            time_limit=0,
            memory_limit=0,
            process_args=args
        )
        ret_result = proc.execute()
        return ret_result

    def execute(self, **kwargs):
        proc = process.Process(
            process_args=[self.__c_executable],
            **kwargs
        )
        ret_result = proc.execute()
        return ret_result
    pass

@wrap_compiler
class CCompiler(CLikeCompiler):
    """ C Compiler, wraps CLikeCompiler. """
    def __init__(self, source_path):
        return CLikeCompiler.__init__(self, source_path, 'C')
    pass

@wrap_compiler
class CppCompiler(CLikeCompiler):
    """ C++ Compiler, wraps CLikeCompiler. """
    def __init__(self, source_path):
        return CLikeCompiler.__init__(self, source_path, 'C++')
    pass
