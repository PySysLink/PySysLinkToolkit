import ast
import operator


class SafeEvaluator(ast.NodeVisitor):
    def __init__(self, variables):
        self.variables = variables

        # Supported operators
        self.bin_ops = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.floordiv,  # ports should be int
            ast.Mod: operator.mod,
        }

        self.unary_ops = {
            ast.UAdd: operator.pos,
            ast.USub: operator.neg,
        }

        # Supported functions
        self.functions = {
            "length": lambda x: len(x),
            "len": lambda x: len(x),
            "max": max,
            "min": min,
            "abs": abs,
            "int": int,
            "range": range,
            "str": str,
        }

    def visit(self, node):
        return super().visit(node)

    def visit_Expression(self, node):
        return self.visit(node.body)

    def visit_Constant(self, node):
        return node.value

    def visit_Name(self, node):
        if node.id not in self.variables:
            raise ValueError(f"Unknown variable: {node.id}")
        return self.variables[node.id]

    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        op_type = type(node.op)

        if op_type not in self.bin_ops:
            raise ValueError(f"Unsupported operator: {op_type}")

        return self.bin_ops[op_type](left, right)

    def visit_UnaryOp(self, node):
        operand = self.visit(node.operand)
        op_type = type(node.op)

        if op_type not in self.unary_ops:
            raise ValueError(f"Unsupported unary operator: {op_type}")

        return self.unary_ops[op_type](operand)

    def visit_Call(self, node):
        if not isinstance(node.func, ast.Name):
            raise ValueError("Only simple function calls allowed")

        func_name = node.func.id
        if func_name not in self.functions:
            raise ValueError(f"Unsupported function: {func_name}")

        args = [self.visit(arg) for arg in node.args]
        return self.functions[func_name](*args)

    def generic_visit(self, node):
        raise ValueError(f"Unsupported expression: {type(node).__name__}")

    def visit_ListComp(self, node):
        result = []

        def recurse(level):
            if level == len(node.generators):
                result.append(self.visit(node.elt))
                return

            gen = node.generators[level]

            iterable = self.visit(gen.iter)

            for value in iterable:
                old = self.variables.get(gen.target.id, None)
                had_old = gen.target.id in self.variables

                self.variables[gen.target.id] = value

                if not gen.ifs or all(self.visit(cond) for cond in gen.ifs):
                    recurse(level + 1)

                if had_old:
                    self.variables[gen.target.id] = old
                else:
                    del self.variables[gen.target.id]

        recurse(0)

        return result

    def visit_JoinedStr(self, node):
        return "".join(str(self.visit(v)) for v in node.values)

    def visit_FormattedValue(self, node):
        return self.visit(node.value)   