from .tabnine_completer import TabnineCompleter


def GetCompleter(user_options):
    return TabnineCompleter(user_options)
