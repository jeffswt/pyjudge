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
