"""
Mutator sûr et pédagogique.
Implémente transformations non dangereuses sur des scripts Python bénins :
- renommer variables locales via AST
- obfusquer littéraux de chaînes (encodage base64 + décodeur local)
- ajouter fonctions noop (code mort) pour changer signature
"""
import ast
import base64
try:
    import astor  # utilisé si ast.unparse est absent
except Exception:
    astor = None
from typing import List

class StringObfuscator(ast.NodeTransformer):
    def __init__(self):
        self.inserted_import_base64 = False

    def visit_Module(self, node):
        # s'assurer que l'import base64 est présent si on remplace des chaînes
        self.generic_visit(node)
        if self.inserted_import_base64:
            has_import = any(isinstance(n, ast.Import) and any(alias.name == 'base64' for alias in n.names)
                             for n in node.body)
            if not has_import:
                node.body.insert(0, ast.Import(names=[ast.alias(name='base64', asname=None)]))
        return node

    def visit_Constant(self, node):
        # obfusquer uniquement les chaînes (str)
        if isinstance(node.value, str) and node.value.strip():
            b = node.value.encode('utf-8')
            encoded = base64.b64encode(b).decode('ascii')
            # remplacer par: base64.b64decode(b'...').decode('utf-8')
            self.inserted_import_base64 = True
            new_node = ast.Call(
                func=ast.Attribute(value=ast.Name(id='base64', ctx=ast.Load()), attr='b64decode', ctx=ast.Load()),
                args=[ast.Constant(value=encoded.encode('ascii'))],
                keywords=[]
            )
            # .decode('utf-8')
            new_node = ast.Call(
                func=ast.Attribute(value=new_node, attr='decode', ctx=ast.Load()),
                args=[ast.Constant(value='utf-8')],
                keywords=[]
            )
            return ast.copy_location(new_node, node)
        return node

class VariableRenamer(ast.NodeTransformer):
    def __init__(self):
        self.map = {}
        self.counter = 0
        self.protected = set(dir(__builtins__)) | {"self", "__name__", "__file__"}

    def _new_name(self, old):
        if old in self.map:
            return self.map[old]
        self.counter += 1
        new = f"v_{self.counter}"
        self.map[old] = new
        return new

    def visit_FunctionDef(self, node):
        # renommer arguments
        for arg in node.args.args:
            if arg.arg not in self.protected:
                arg.arg = self._new_name(arg.arg)
        self.generic_visit(node)
        return node

    def visit_Name(self, node):
        if isinstance(node.ctx, (ast.Store, ast.Load, ast.Del)):
            if node.id not in self.protected and not node.id.startswith("v_") and not node.id.isupper():
                new = self._new_name(node.id)
                return ast.copy_location(ast.Name(id=new, ctx=node.ctx), node)
        return node

def add_noop_functions(source_ast, count=2):
    """Ajoute quelques fonctions inutiles pour augmenter la complexité visuelle."""
    for i in range(count):
        name = f"_noop_extra_{i}"
        func = ast.parse(f"def {name}():\n    x = {i}\n    return x\n").body[0]
        source_ast.body.append(func)
    return source_ast

class Mutator:
    def __init__(self, operations: List[str]):
        self.operations = operations

    def mutate_source(self, source_code: str) -> str:
        tree = ast.parse(source_code)
        if "obfuscate_strings" in self.operations:
            tree = StringObfuscator().visit(tree)
            ast.fix_missing_locations(tree)
        if "rename_vars" in self.operations:
            tree = VariableRenamer().visit(tree)
            ast.fix_missing_locations(tree)
        if "add_noop" in self.operations:
            tree = add_noop_functions(tree, count=2)
            ast.fix_missing_locations(tree)
        # essayer ast.unparse si disponible, sinon astor
        try:
            new_code = ast.unparse(tree)
        except AttributeError:
            if astor is None:
                raise RuntimeError("ast.unparse non disponible et astor n'est pas installé")
            new_code = astor.to_source(tree)
        return new_code
