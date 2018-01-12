import dnnamo

from .tool_utilities import BaselineTool, path_to_loader_pair, ToolRegistry

class PrimopDiagnosticTool(BaselineTool):
  TOOL_NAME='_primop_diag'
  TOOL_SUMMARY='[INTERNAL] Assists in diagnosing Primop translation problems.'

  def add_subparser(self, argparser):
    super(PrimopDiagnosticTool, self).add_subparser(argparser)
    self.subparser.add_argument('--prioritized', '-p', action='store_true', default=False, help='Return a prioritized translation list based on the fraction of time spent in each native operation type.')
    return self.subparser

  def _run(self, modelfiles):
    self.data = dict()

    for modelfile in modelfiles:
      frame = dnnamo.frameworks.FRAMEWORKS[self.args['framework']]()
      (modname, pypath) = path_to_loader_pair(modelfile)
      frame.load(dnnamo.loader.RunpyLoader, modname, pypath=pypath)

      for primop in frame.absgraph:
        if primop.optype!='undef':
          self.data[primop.id] = (primop.source_op.type, primop.optype)

      if self.args['prioritized']:
        raise NotImplementedError, 'Timing-prioritized diagnosis not available yet.'



  def _output(self):
    for k,v in self.data.items():
      print k,'=>',v

ToolRegistry.register(PrimopDiagnosticTool)