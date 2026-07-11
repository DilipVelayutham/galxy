import ast
import builtins
import sys

def check_file(path):
    print(f"Analyzing {path}...")
    try:
        with open(path, "r", encoding="utf-8") as f:
            code = f.read()
        
        # 1. Compile to check syntax
        tree = ast.parse(code)
        print("Syntax: Valid Python syntax!")
        
        # 2. Check for undefined variables
        defined = set(dir(builtins)) | {"seed_db", "__name__", "__file__", "__doc__", "__package__", "ASCENDING", "TEXT"}
        
        # Simple walker to trace variable scopes
        class ScopeVisitor(ast.NodeVisitor):
            def __init__(self):
                self.scopes = [defined.copy()]
                self.errors = []

            def visit_Import(self, node):
                for alias in node.names:
                    self.scopes[-1].add(alias.asname or alias.name)
                self.generic_visit(node)

            def visit_ImportFrom(self, node):
                for alias in node.names:
                    self.scopes[-1].add(alias.asname or alias.name)
                self.generic_visit(node)

            def visit_FunctionDef(self, node):
                # Create inner scope
                inner_scope = self.scopes[-1].copy()
                for arg in node.args.args:
                    inner_scope.add(arg.arg)
                self.scopes.append(inner_scope)
                self.generic_visit(node)
                self.scopes.pop()

            def visit_Assign(self, node):
                # Before visiting value, targets get defined
                for target in node.targets:
                    self.define_target(target)
                self.generic_visit(node)

            def define_target(self, target):
                if isinstance(target, ast.Name):
                    self.scopes[-1].add(target.id)
                elif isinstance(target, (ast.Tuple, ast.List)):
                    for el in target.elts:
                        self.define_target(el)

            def visit_Name(self, node):
                if isinstance(node.ctx, ast.Load):
                    # Check if defined in any active scope
                    found = False
                    for scope in reversed(self.scopes):
                        if node.id in scope:
                            found = True
                            break
                    if not found:
                        self.errors.append((node.id, node.lineno))
                self.generic_visit(node)

        visitor = ScopeVisitor()
        visitor.visit(tree)
        
        if visitor.errors:
            print("Found undefined variables:")
            for name, line in sorted(visitor.errors, key=lambda x: x[1]):
                print(f"Line {line}: Name '{name}' is used but not defined.")
        else:
            print("Variables: All names are correctly defined!")
            
    except Exception as e:
        print(f"Error parsing file: {e}")

if __name__ == "__main__":
    check_file("seed.py")
