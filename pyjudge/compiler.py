
import copy
import os
import re

from . import config
from . import process
from . import tmpmgmt

class CompilerError(Exception):
    def __init__(self, *args):
        self.args = args
        return
    pass

class CompilerResult:
    """ Compiler output, wrapped. """
    def __init__(self,
            return_code=1,
            output=''):
        self.return_code = return_code
        self.output = output
        return
    pass

def wrap_compiler(input_class):
    class CompilerWrapper(input_class):
        def __init__(self, *args, **kwargs):
            ret = input_class.__init__(self, *args, **kwargs)
            self.__sequence = 0
            return ret
        def compile(self, *args, **kwargs):
            if self.__sequence not in {0, 1}:
                raise AttributeError('Source code already compiled')
            if self.__sequence == 1:
                input_class.close(self)
            ret = input_class.compile(self, *args, **kwargs)
            if ret.return_code == 0:
                self.__sequence = 1
            ret['output'] = ret['output'].replace('\r', '')
            return ret
        def execute(self, *args, **kwargs):
            if self.__sequence != 1:
                raise AttributeError('Source code hadn\'t been compiled')
            ret = input_class.execute(self, *args, **kwargs)
            # Converting bytes to str
            def __create_clean_str(dat):
                if type(dat) == bytes:
                    dat = dat.decode('utf-8', 'ignore')
                dat = dat.replace('\r', '')
                return dat
            ret['stdout'] = __create_clean_str(ret['stdout'])
            ret['stderr'] = __create_clean_str(ret['stderr'])
            return ret
        def close(self):
            if self.__sequence != 1:
                raise AttributeError('Nothing to remove')
            ret = input_class.close(self)
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

    def execute(self, additional_args=[], **kwargs):
        """ execute() -- Execute compiled executable. """
        raise NotImplementedError()

    def close(self):
        """ close() -- Remove compiled executable. """
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
        ret_result = CompilerResult(
            return_code = 0,
            output = '',
        )
        return ret_result

    def execute(self, additional_args=[], **kwargs):
        ret_result = process.ProcessResult(
            time = 0,
            memory = 0,
            return_code = 0,
            stdout = self.__file_handle.read(),
            stderr = '',
        )
        self.__file_handle.seek(0)
        return ret_result

    def close(self):
        self.__file_handle.close()
        return
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
        ret_result = CompilerResult(
            return_code = 0,
            output = '',
        )
        return ret_result

    def execute(self, additional_args=[], **kwargs):
        args = copy.deepcopy(self.__python_args)
        for i in range(0, len(args)):
            args[i] = args[i].format(source_file=self.source_path)
        # Formatted arguments, executing
        p = process.Process(
            process_args = args + additional_args,
            **kwargs
        )
        return p.execute()

    def close(self):
        return
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
        args = copy.deepcopy(self.__c_args)
        out_file = tmpmgmt.create_tmpfile()
        self.__c_executable = out_file
        for i in range(0, len(args)):
            args[i] = args[i].format(
                source_file = self.source_path,
                output_file = out_file)
            pass
        # Formatted arguments, executing
        proc = process.Process(
            time_limit = 0,
            memory_limit = 0,
            process_args = args
        )
        ret_result_old = proc.execute()
        ret_result = CompilerResult(
            return_code = ret_result_old.return_code,
            output = ret_result_old.stderr,
        )
        # Some hotfixes on Windows...
        try:
            os.rename(out_file + '.exe', out_file)
        except:
            pass
        # Done compilation
        if ret_result.return_code != 0:
            raise CompilerError(ret_result.output)
        return ret_result

    def execute(self, additional_args=[], **kwargs):
        proc = process.Process(
            process_args = [self.__c_executable] + additional_args,
            **kwargs
        )
        ret_result = proc.execute()
        return ret_result

    def close(self):
        tmpmgmt.remove_tmpfile(self.__c_executable)
        return
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

@wrap_compiler
class ExecutableCompiler(Compiler):
    """ Compiler that only runs executables. Discouraged when using. Should take
    special care when running untrusted code on servers. """

    def compile(self, override_command=None):
        try:
            f_handle = open(self.source_path, 'r')
            f_handle.close()
        except:
            raise CompilerError('Unable to open file')
        ret_result = CompilerResult(
            return_code = 0,
            output = '',
        )
        return ret_result

    def execute(self, additional_args=[], **kwargs):
        proc = process.Process(
            process_args = [self.source_path] + additional_args,
            **kwargs
        )
        ret_result = proc.execute()
        return ret_result

    def close(self):
        return
    pass

@wrap_compiler
class AdaptiveCompiler(Compiler):
    """ Adaptive compiler, adapts compilation method through input or given
    method type. """
    def __init__(self, source_path, source_type=None):
        Compiler.__init__(self, source_path)
        if not source_type:
            src_match = {
                r'.txt$': 'Text',
                r'.in$': 'Text', # De-facto standards by CCF
                r'.out$': 'Text', # De-facto standards by CCF
                r'.cpp$': 'C++',
                r'.c\+\+$': 'C++',
                r'.c$': 'C',
                r'.py$': 'Python3',
                r'.py3$': 'Python3', # Non-standard
                r'.py2$': 'Python2', # Non-standard
                r'.java$': 'Java',
                r'.exe$': 'Executable', # Windows executable
                r'^[~.]$': 'Executable', # We treat them as executable
            }
            for i in src_match:
                j = src_match[i]
                if re.findall(i, source_path):
                    source_type = j
                    break
                continue
            if not source_type:
                source_type = 'Text'
            pass
        # Determined source_path, now creating new compilers for use...
        comp_match = {
            'Text': FileHandleCompiler,
            'C++': CppCompiler,
            'C': CCompiler,
            'Python3': Python3Compiler,
            'Python2': Python2Compiler,
            'Executable': ExecutableCompiler,
        }
        comp_is = Compiler
        for i in comp_match:
            if source_type == i:
                comp_is = comp_match[i]
                break
            continue
        self.__actual_compiler = comp_is(source_path)
        return

    def compile(self, *args, **kwargs):
        return self.__actual_compiler.compile(*args, **kwargs)

    def execute(self, *args, **kwargs):
        return self.__actual_compiler.execute(*args, **kwargs)

    def close(self, *args, **kwargs):
        return self.__actual_compiler.close(*args, **kwargs)
    pass
