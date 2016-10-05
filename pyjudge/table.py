
class Table:
    @classmethod
    def wrap_lines(self, lin, width, align='left'):
        res = []
        while lin:
            tmp = lin[:width]
            lin = lin[width:]
            if len(tmp) < width:
                if align == 'left':
                    tmp = tmp.ljust(width, ' ')
                elif align == 'right':
                    tmp = tmp.rjust(width, ' ')
                elif align == 'centre':
                    dist = width - len(tmp)
                    tmp = ' ' * (dist - int(dist / 2)) + tmp + ' ' * int(dist / 2)
                else:
                    raise AttributeError('Unknown align method')
                pass
            res.append(tmp)
            continue
        if len(res) <= 0:
            res.append(' ' * width)
        return res
    @classmethod
    def join_wrap_lines(self, left, right, lwidth=10, rwidth=10, lalign='left', ralign='right'):
        if type(left) == str:
            left = self.wrap_lines(left, lwidth, align=lalign)
        if type(right) == str:
            right = self.wrap_lines(right, rwidth, align=ralign)
        # Done wrapping to lists, syncing height
        lwidth = len(left[0]) # Guranteed correctness
        rwidth = len(right[0])
        while len(right) < len(left):
            right.append(' ' * rwidth)
        while len(left) < len(right):
            left.append(' ' * lwidth)
        # Combining
        res = []
        for i in range(0, len(left)):
            res.append(left[i] + right[i])
        return res
    def __init__(self, title, data):
        self.title = title
        self.data = data
        return
