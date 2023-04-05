import ast, re
import numpy as np

_py_assignment_regex = re.compile(r'\s*(\w+)\s*=\s*(.+)$')

class FunctionCallAggregator(ast.NodeVisitor):
  class FunctionInfo:
    def __init__(self):
      self.module = None
      self.name = None
      self.args = []
    
    def __str__(self):
      return f'FunctionInfo(module={self.module}, name={self.name}, args={self.args})'

  def __init__(self):
    self.calls = []

  def visit_Call(self, node):
    info = self.FunctionInfo()

    # Collect data on function
    # Get module
    # Get name
    field = getattr(node, 'func')
    if hasattr(field, 'attr'):
      if hasattr(field, 'value'):
        info.module = getattr(getattr(field, 'value'), 'id')
      info.name = getattr(field, 'attr')
    elif hasattr(field, 'id'):
      info.name = getattr(field, 'id')
    # Get args
    for argnode in getattr(node, 'args'):
      info.args.append(argnode)

    self.calls.append(info)

    # Visit children
    for child in ast.iter_child_nodes(node):
      self.visit(child)

def inspect_statement(statement : str):
  # Parse function calls from statement
  tree = ast.parse(statement)
  print(ast.dump(tree))
  function_aggregator = FunctionCallAggregator()
  function_aggregator.visit(tree)
  function_calls = function_aggregator.calls
  if len(function_calls) == 0: return None # We only analyze function calls

  # Look for imshow() calls
  for call in function_calls:
      if call.name == 'imshow':
        print('Found imshow call!')

  return None