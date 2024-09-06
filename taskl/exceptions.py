class TaskCommandNotFound(Exception):
    """Will be raised if the task command could not be found
    """
    pass
class ErrorRunningTaskCommand(Exception):
    """Will be raised if the task command returns an unknown error
    """
    pass
class NoTaskGiven(Exception):
    """Will be rasied if a given task could not be found using the task command
    """
    pass
class ErrorAddingNewTask(Exception):
    """Will be raised on adding new tasks"""
    pass
