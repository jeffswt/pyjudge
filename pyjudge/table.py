
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
    def __init__(self, title, data):
        self.title = title
        self.data = data
        return
