import ast
import sys
if sys.version_info > (3,8):
    from ast import Module
else :
    from ast import Module as OriginalModule
    Module = lambda nodelist, type_ignores: OriginalModule(nodelist)


def execute_cell_get_output(shell,line,cell,local_ns):
        if cell:
            expr = shell.transform_cell(cell)
        else:
            expr = shell.transform_cell(line)

        expr_ast = shell.compile.ast_parse(expr)
        expr_ast = shell.transform_ast(expr_ast)
        expr_val=None
        if len(expr_ast.body)==1 and isinstance(expr_ast.body[0], ast.Expr):
            mode = 'eval'
            source = '<timed eval>'
            expr_ast = ast.Expression(expr_ast.body[0].value)
        else:
            mode = 'exec'
            source = '<timed exec>'
            if len(expr_ast.body) > 1 and isinstance(expr_ast.body[-1], ast.Expr):
                expr_val= expr_ast.body[-1]
                expr_ast = expr_ast.body[:-1]
                expr_ast = Module(expr_ast, [])
                expr_val = ast.Expression(expr_val.value)

        code = shell.compile(expr_ast, source, mode)
        glob = shell.user_ns
        if mode=='eval':
            try:
                out = eval(code, glob, local_ns)
            except:
                shell.showtraceback()
                return
        else:
            try:
                exec(code, glob, local_ns)
                out=None
                if expr_val is not None:
                    code_2 = shell.compile(expr_val, source, 'eval')
                    out = eval(code_2, glob, local_ns)
            except:
                shell.showtraceback()
                return

        return out