import ast
import contextlib
import collections

_Scope = collections.namedtuple('_Scope', 'class_scope ids')


class _Base(object):

    def __init__(self):
        self.scopes = [_Scope(False, set())]
        self.unbound = set()

    @property
    def scope(self):
        return self.scopes[-1]

    @contextlib.contextmanager
    def scoped(self, class_scope=False):
        self.scopes.append(_Scope(class_scope, set()))
        yield
        self.scopes.pop()

    def bind(self, name):
        self.scope.ids.add(name)

    def is_bound(self, name):
        return (name in self.scope.ids or
                any(name in scope.ids
                    for scope in self.scopes[:-1]
                    if not scope.class_scope))


class _Visitor(ast.NodeVisitor, _Base):

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load) and not self.is_bound(node.id):
            self.unbound.add(node.id)

        if isinstance(node.ctx, ast.Store):
            self.bind(node.id)

    def visit_FunctionDef(self, node):
        for d in node.decorator_list:
            self.visit(d)

        for d in node.args.defaults:
            self.visit(d)

        self.bind(node.name)
        with self.scoped():
            # import pdb; pdb.set_trace()
            for p in node.args.args:
                # TODO: handle py2
                self.bind(p.arg)
            if node.args.vararg:
                self.bind(node.args.vararg)
            if node.args.kwarg:
                self.bind(node.args.kwarg)

            # TODO: py3 has kwonlyargs

            for d in node.body:
                self.visit(d)

    def visit_ClassDef(self, node):
        for d in node.decorator_list:
            self.visit(d)

        for b in node.bases:
            self.visit(b)

        # TODO: py3 also has starargs, kwargs
        self.bind(node.name)
        with self.scoped(class_scope=True):
            for d in node.body:
                self.visit(d)

    def visit_ListComp(self, node):
        self.visit_GeneratorExp(node)

    def visit_GeneratorExp(self, node):
        for g in node.generators:
            self.visit(g)

        self.visit(node.elt)


def parse(source):
    node = ast.parse(source)
    visitor = _Visitor()
    visitor.visit(node)
    return visitor.unbound
