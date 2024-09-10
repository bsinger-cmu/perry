import ast
import inspect

class FunctionData():
    def __init__(self, name, )


class FunctionCallVisitor(ast.NodeVisitor):
    def __init__(self, source):
        self.called_functions = []
        self.source = source

    def visit_Call(self, node):
        call_source = ast.get_source_segment(self.source, node)

        if isinstance(node.func, ast.Name):
            self.called_functions.append(node.func.id)
            # Get function source code
            print(inspect.getsource(node.func))
        elif isinstance(node.func, ast.Attribute):
            self.called_functions.append(node.func.attr)
        self.generic_visit(node)
