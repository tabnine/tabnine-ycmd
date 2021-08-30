from ycmd import responses
from ycmd.completers.general_completer import GeneralCompleter
from ycmd.completers import completer_utils
from ycmd.utils import LOGGER, re, SplitLines
from .tabnine import Tabnine


FILETYPE_TRIGGERS = {
  'c,\
  objc,objcpp,\
  ocaml,\
  cpp,cuda,objcpp,cs,\
  perl,\
  php,\
  d\
  elixir,\
  go,\
  gdscript,\
  groovy,\
  java,\
  javascript,\
  javascriptreact,\
  julia,\
  perl6,\
  python,\
  scala,\
  ypescript,\
  typescriptreact,\
  vb,\
  ruby,rust,\
  lua,\
  erlang': list("abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz(=[%/{+#.,\\<+-|&*=$#@!")
}

class TabnineCompleter( GeneralCompleter ):

  def __init__( self, user_options ):
    super().__init__( user_options )
    self._settings_for_file = {}
    self._environment_for_file = {}
    self._environment_for_interpreter_path = {}
    self.completion_triggers = completer_utils.PreparedTriggers(default_triggers =  FILETYPE_TRIGGERS)
    self._tabnine = Tabnine()


  def ComputeCandidatesInner( self, request_data ):
      completions = []
      for file_name, file_data in request_data.get('file_data').items():
          before = self._GetBefore(request_data,file_name)
          request = {"before": before, "after": "", "filename": file_name, "max_num_results": 5, "region_includes_beginning": True, "region_includes_end": False}
          response = self._tabnine.auto_complete(request)
          completions += [result.get('new_prefix') for result in response.get('results')]
      
      return [ responses.BuildCompletionData(
        insertion_text = completion,
        extra_menu_info = "[⌬ tabnine]",
      ) for completion in completions ]


  def SupportedFiletypes( self ):
      return [ 'python' ]

  def ShouldUseNowInner( self, request_data ):
      return True 

  def _GetBefore(self, request_data, file_name):
      before = ""
      line_num = request_data['line_num'] 
      column_num = request_data['column_num'] - 1 
      lines = completer_utils.GetFileLines(request_data, file_name)
      lines = lines[:line_num]
      for line in lines[:-1]:
          before += line

      before += lines[-1][:column_num] 
      return before

  def _OpenHub(self):
      self._tabnine.configuration({})

  # This is to disable caching Tabnine suggestions
  def _GetCandidatesFromSubclass( self, request_data ):
    raw_completions = self.ComputeCandidatesInner( request_data )
    self._completions_cache.Update( request_data, raw_completions )
    return raw_completions



