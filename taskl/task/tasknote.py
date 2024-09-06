from datetime import datetime

class TaskNote:

    """Class for TaskWarrior task annotations
    """

    def __init__(self, task_id: str | int, annotation: dict):
        """Constructor for a task annotation

        Args:
            task_id (str | int): the task identfier. Can be an active id or the uuid of the task
            annotation (dict): the annotation itself
        """

        self.task_id: str = task_id
        """The TaskWarrior task identifier"""
        self.description: str = annotation.get('description')
        """The description of the annotation"""
        self.entry: str = datetime.fromisoformat(annotation.get('entry'))
        """The annotation creation date"""

    def __repr__(self):
        return f'Taskl.Task.Note(task_id={self.task_id})'
