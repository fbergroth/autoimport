import textwrap

from autoimport import parser


def test_generator():
    source = '(x for x in pkg.xs)'
    assert parser.parse(source) == set(['pkg'])

def test_list_comprehension():
    source = '[y for y in ys]'
    assert parser.parse(source) == set(['ys'])

#TODO: *args, **kwargs
def test_function_def():
    source = textwrap.dedent('''\
    a = 1
    @decorator(a, decvar)
    def f(b):
        return a + b + pkg.c + local
    f(a)
    ''')
    assert parser.parse(source) == set(['decorator', 'decvar', 'pkg', 'local'])


def test_class():
    source = textwrap.dedent('''\
    @classdec
    class Clazz(pkg.base):
        a = 3
        b = a + 1
        # def method(self, x, y):
        #     return a + x + y
    ''')
    assert parser.parse(source) == set(['classdec', 'pkg'])
