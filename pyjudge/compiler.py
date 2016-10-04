def wrap_compiler(input_class):
    class CompilerWrapper(input_class):
        def __init__(self, source_path):
            ret = input_class.__init__(self, source_path)
            self.__sequence = 0
            return ret
        def compile(self):
            if self.__sequence != 0:
                raise AttributeError('Source code already compiled')
            ret = input_class.compile(self)
            self.__sequence = 1
            return ret
        def execute(self):
            if self.__sequence != 1:
                raise AttributeError('Source code hadn\'t been compiled')
            ret = input_class.execute(self)
            self.__sequence = 2
            return ret
        def get_output(self):
            if self.__sequence != 2:
                raise AttributeError('No execution had been made')
            ret = input_class.get_output(self)
            return ret
        def close(self):
            if self.__sequence == 0:
                raise AttributeError('Compiler handle already closed')
            ret = input_class.close(self)
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

    def get_output(self):
        """ get_output() -- Receive execution output in string. """
        raise NotImplementedError()

    def close(self):
        """ close() -- Free executable file. """
        raise NotImplementedError()
