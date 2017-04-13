
import copy
import os
import re

from . import config
from . import process
from . import table
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
    def __repr__(self):
        return repr(table.Table('Process Execution Results', [
            ('Return Code', self.return_code),
            ('Compiler Output', self.output),
        ]))
    pass

def wrap_compiler(input_class):
    class CompilerWrapper(input_class):
        def __init__(self, *args, **kwargs):
            ret = input_class.__init__(self, *args, **kwargs)
            self.__sequence = 0
            self.__compile_result = None
            return ret
        def compile(self, *args, **kwargs):
            if self.__compile_result != None:
                if self.__compile_result.return_code != 0:
                    raise CompilerError(self.__compile_result.output)
                return self.__compile_result
            try:
                ret = input_class.compile(self, *args, **kwargs)
                self.__compile_result = ret
                ret.output = ret.output.replace('\r', '')
                if ret.return_code != 0:
                    raise CompilerError(ret.output)
                self.__sequence = 1
            except CompilerError as err:
                out = err.args[0].replace('\r', '')
                self.__compile_result = CompilerResult(return_code=1, output=err.args[0])
                raise err
            return ret
        def compiled(self):
            return self.__sequence == 1
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
            ret.stdout = __create_clean_str(ret.stdout)
            ret.stderr = __create_clean_str(ret.stderr)
            return ret
        def close(self):
            if self.__sequence != 1:
                raise AttributeError('Nothing to remove')
            ret = input_class.close(self)
            self.__sequence = 0
            return ret
        def closed(self):
            return self.__sequence == 0
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
class DirectoryFilesCompiler(Compiler):
    """ Wraps files in directory for matching files. """

    def compile(self, override_command=None):
        pattern_1 = r'\.([^.]*?)\*$'
        pattern_2 = r'{number}.\1'
        f_handles = []
        for i in range(1, 101): # Maximum allowed 100 inputs
            def __test_available(src, i, *args):
                for j in args:
                    fn = re.sub(pattern_1, pattern_2.format(number=j % i), src)
                    if os.path.exists(fn):
                        return fn
                    continue
                return None
            fn = __test_available(self.source_path, i, '%d', '0%d', ' %d', ' 0%d', '(%d)', '(0%d)', ' (%d)', ' (0%d)', '.%d', '.0%d')
            if not fn:
                break
            n_comp = FileHandleCompiler(fn)
            try:
                n_comp.compile()
            except CompilerError:
                if not n_comp.closed():
                    n_comp.close()
                break
            f_handles.append((i, fn, n_comp))
        self.__file_handle = f_handles
        self.__file_pointer = 0
        if len(self.__file_handle) <= 0:
            raise CompilerError('Unable to find any corresponding file')
        return CompilerResult(return_code=0, output='')

    def execute(self, additional_args=[], **kwargs):
        try:
            f_handle = self.__file_handle[self.__file_pointer][2]
            ret = f_handle.execute(additional_args, **kwargs)
        except Exception as err:
            raise err
        finally:
            self.__file_pointer += 1
            if self.__file_pointer >= len(self.__file_handle):
                self.__file_pointer = 0
            pass
        return ret

    def close(self):
        for tup in self.__file_handle:
            f_handle = tup[2]
            if not f_handle.closed():
                f_handle.close()
            continue
        del self.__file_handle
        del self.__file_pointer
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
    abbreviation for fewer code lines.
    This can also be used for languages that are compiled to machine code which
    can be executed directly. """

    def __init__(self, source_path, language_type):
        Compiler.__init__(self, source_path)
        if language_type == 'C':
            self.__c_args = config.get_config('gcc_args')
        elif language_type == 'C++':
            self.__c_args = config.get_config('g++_args')
        elif language_type == 'Pascal':
            self.__c_args = config.get_config('fpc_args')
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
class PascalCompiler(CLikeCompiler):
    """ Pascal Compiler, wraps CLikeCompiler. """
    def __init__(self, source_path):
        return CLikeCompiler.__init__(self, source_path, 'Pascal')
    pass

@wrap_compiler
class JavaCompiler(Compiler):
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
                r'.ans$': 'Text', # De-facto standards by CCF
                r'.std$': 'Text', # Non-standard
                r'.(in|out|ans|std)\*$': 'Directory', # De-facto standards by CCF and pyJudge
                r'.cpp$': 'C++',
                r'.c\+\+$': 'C++',
                r'.c$': 'C',
                r'.py$': 'Python3',
                r'.py3$': 'Python3', # Non-standard
                r'.py2$': 'Python2', # Non-standard
                r'.pas$': 'Pascal',
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
            'Directory': DirectoryFilesCompiler,
            'C++': CppCompiler,
            'C': CCompiler,
            'Python3': Python3Compiler,
            'Python2': Python2Compiler,
            'Java': JavaCompiler,
            'Pascal': PascalCompiler,
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
