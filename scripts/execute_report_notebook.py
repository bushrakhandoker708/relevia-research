"""Execute our report-only Python cells without a Jupyter kernel subprocess.

This is not a model runner. It records genuine stdout, expression values and
matplotlib figures; failures remain in the notebook and produce a failing exit.
"""
import argparse
import ast
import base64
import contextlib
import io
import os
import traceback
from pathlib import Path
import nbformat


def main():
    ap=argparse.ArgumentParser();ap.add_argument('notebook',type=Path);args=ap.parse_args()
    path=args.notebook.resolve();root=Path(__file__).resolve().parents[1]
    if path.parent != root/'notebooks':raise ValueError('Only project notebooks are supported')
    nb=nbformat.read(path,as_version=4);scope={'__name__':'__main__'};count=0;failed=False
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    os.chdir(root)
    for cell in nb.cells:
        if cell.cell_type!='code':continue
        count+=1;cell.execution_count=count;cell.outputs=[];out=io.StringIO()
        def show():
            for num in plt.get_fignums():
                fig=plt.figure(num);buf=io.BytesIO();fig.savefig(buf,format='png',dpi=120)
                cell.outputs.append(nbformat.v4.new_output('display_data',data={'image/png':base64.b64encode(buf.getvalue()).decode(),'text/plain':'Measured-data figure'}))
            plt.close('all')
        plt.show=show
        try:
            tree=ast.parse(cell.source);last=tree.body.pop() if tree.body and isinstance(tree.body[-1],ast.Expr) else None
            with contextlib.redirect_stdout(out),contextlib.redirect_stderr(out):
                exec(compile(tree,str(path),'exec'),scope)
                result=eval(compile(ast.Expression(last.value),str(path),'eval'),scope) if last else None
            if out.getvalue():cell.outputs.insert(0,nbformat.v4.new_output('stream',name='stdout',text=out.getvalue()))
            if result is not None:cell.outputs.append(nbformat.v4.new_output('execute_result',execution_count=count,data={'text/plain':repr(result)}))
        except Exception as exc:
            cell.outputs.append(nbformat.v4.new_output('error',ename=type(exc).__name__,evalue=str(exc),traceback=traceback.format_exc().splitlines()));failed=True;break
    nb.metadata['execution_method']='Actual sequential Python execution via scripts/execute_report_notebook.py; no IPython magics or Jupyter kernel'
    nbformat.write(nb,path)
    print(path.name, 'failed' if failed else f'executed {count} code cells')
    if failed:raise SystemExit(1)


if __name__=='__main__':main()
