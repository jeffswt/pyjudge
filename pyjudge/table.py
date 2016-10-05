
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
    @classmethod
    def insert_in_lines(self, lines, pos, inject):
        ret_l = []
        for line in lines:
            ret_l.append(line[:pos] + inject + line[pos:])
        return ret_l
    def __init__(self, title, data):
        self.title = title
        self.data = data
        return
    def __repr__(self):
        console_width = 80
        row_widths = [int(console_width * 0.25) - 3, console_width - int(console_width * 0.25) + 3]
        out_l = []
        out_l += self.join_wrap_lines(' ', self.title, lwidth=1, rwidth=console_width-1, ralign='left')
        out_l.append('=' * row_widths[0] + '=+=' + '=' * row_widths[1])
        for row in self.data:
            tmp_l = self.join_wrap_lines(row[0], row[1], lwidth=row_widths[0], rwidth=row_widths[1], lalign='right', ralign='left')
            out_l += self.insert_in_lines(tmp_l[:1], row_widths[0], ' T ') + self.insert_in_lines(tmp_l[1:], row_widths[0], ' | ')
        fmt_s = ''
        for line in out_l:
            fmt_s += line + '\n'
        return fmt_s
    pass
