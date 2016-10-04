
from . import compiler
from . import process

class JudgerError(Exception):
    def __init__(self, *args):
        self.args = args
        return
    pass

status_codes = {
    'AC': 'Accepted',
    'CE': 'Compile Error',
    'WA': 'Wrong Answer',
    'RE': 'Runtime Error',
    'TLE': 'Time Limit Exceeded',
    'MLE': 'Memory Limit Exceeded',
    'PE': 'Presentation Error',
}

class Judger:
    """ Base judger, always returns NotImplementedError on all actions. Extend
    this class for further functionalities. """

    def __init__(self):
        return

    def judge(self, *args, **kwargs):
        raise NotImplementedError()
    pass

