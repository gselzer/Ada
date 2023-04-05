import ast, re
import numpy as np
from collections import defaultdict

_full_script = []
_assignments = defaultdict(list) # Maps names to AST assignment nodes

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
    # Get name
    field = getattr(node, 'func')
    if hasattr(field, 'attr'):
      # Get module
      if hasattr(field, 'value'):
        info.module = getattr(getattr(field, 'value'), 'id')
      info.name = getattr(field, 'attr')
    elif hasattr(field, 'id'):
      info.name = getattr(field, 'id')
    # Get args
    for argnode in getattr(node, 'args'):
      info.args.append(argnode)

    self.calls.insert(0, info)

    # Visit children
    for child in ast.iter_child_nodes(node):
      self.visit(child)

class AssignmentCollector(ast.NodeTransformer):
  def visit_Assign(self, assign):
    # Set the proper line number
    assign.lineno = len(_full_script) - 1

    # Get variable name
    ast.dump(assign.targets)
    for target in assign.targets:
      if target is ast.Name:
        _assignments[target.id].append(assign)

    # Visit children
    for child in ast.iter_child_nodes(assign):
      self.visit(child)


def inspect_statement(statement : str):
  # Add statement to script
  _full_script.append(statement)

  # Parse tree
  tree = ast.parse(statement)
  print(ast.dump(tree))

  # Parse function calls from statement
  function_aggregator = FunctionCallAggregator()
  function_aggregator.visit(tree)
  function_calls = function_aggregator.calls
  if len(function_calls) == 0: return None # We only analyze function calls

  # Look for imshow() calls
  for call in function_calls:
      if call.name == 'imshow':
        print('Found imshow call!')

  return None