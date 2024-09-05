from datetime import datetime
from .tasknote import TaskNote

class Task:
    """Base class of a TaskWarrior task
    """

    def __init__(self, raw_task_data: dict):
        """Constructor to build the Task object

        Also manipulates data such as date formats

        Args:
            raw_task_data (dict): The raw task data (`task export`) of the task
        """
        # self.raw_task_data = raw_task_data

        self.description = raw_task_data.get('description')
        """Task description"""
        self.annotations = raw_task_data.get('annotations', [])
        """A list of Task annotations (TaskNote objects)"""
        self.priority = raw_task_data.get('priority')
        """Task priority"""
        self.urgency = raw_task_data.get('urgency')
        """Task urgency"""
        self.urgency = raw_task_data.get('urgency')
        """Task urgency"""
        self.project = raw_task_data.get('project')
        """Task project"""
        self.start = raw_task_data.get('start')
        """datetime object if task is started"""
        if self.start:
            self.start = datetime.fromisoformat(raw_task_data.get('start'))
        self.status = raw_task_data.get('status')
        """current task status"""
        self.entry = datetime.fromisoformat(raw_task_data.get('entry'))
        """datetime of the task creation date"""
        self.modified = datetime.fromisoformat(raw_task_data.get('modified'))
        """datetime of the task last modification"""
        self.due = raw_task_data.get('due')
        """datetime of the task due date"""
        if self.due:
            self.due = datetime.fromisoformat(self.due)
        self.uuid = raw_task_data.get('uuid')
        self.recur = raw_task_data.get('recur')
        self.rtype = raw_task_data.get('rtype')
        self.mask = raw_task_data.get('mask')
        self.parent = raw_task_data.get('parent')

        # If the current task is active, then we have an identifier
        self.id = raw_task_data.get('id', self.uuid)
        self.active = False
        try:
            int(self.id)
            self.active = True
        except ValueError:
            # self.id == self.uuid
            pass

        if len(self.annotations) >= 1:
            # task note object for each annotation
            self.annotations = [TaskNote(self.id, note) for note in self.annotations]

    def get_priority(self) -> str:
        """Returns the task priority

        Returns:
            str: The task priority
        """
        return self.priority

    def set_priority(self):
        ...

    def get_due_date(self) -> datetime:
        """Get the task due date 

        Returns:
            datetime: datetime object of the task due date
        """
        return self.due

    def complete(self):
        ...

    def delete(self):
        ...

    def __repr__(self):
        return f'Taskl.Task(id={self.id})'
