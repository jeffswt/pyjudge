
import os

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
            self.__sequence = 0
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

    def compile(self):
        """ compile() -- Compile the source code into executable. """
        raise NotImplementedError()

    def execute(self):
        """ execute() -- Execute compiled executable. """
        raise NotImplementedError()
    pass

@wrap_compiler
class FileHandleCompiler(Compiler):
    """ Handles a file in Unicode encoding. Does not actually compile files,
    only provides a compiler-like interface for files' handling. """

    def compile(self):
        try:
            self.__file_handle = open(self.source_path, 'r')
        except Exception:
            raise CompilerError('Failed to open file')
        return

    def execute(self):
        return

    def get_output(self):
        try:
            self.__file_data = self.__file_handle.read()
        except Exception:
            raise CompilerError('Failed to read from file')
        return self.__file_data

    def close(self):
        self.__file_handle.close()
        del self.__file_handle
        del self.__file_data
        return
    pass

@wrap_compiler
class PythonCompiler(Compiler):
    """
