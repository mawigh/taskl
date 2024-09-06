import ast
import re
from datetime import datetime
from subprocess import run
from typing import Self

from .tasknote import TaskNote
from ..utils import TasklUtils
from ..exceptions import TaskCommandNotFound, ErrorRunningTaskCommand, ErrorAddingNewTask


class Task:
    """Base class of a TaskWarrior task
    """

    def __init__(self, description: str, due: str = None, project: str = None, priority: str = None, urgency: str = None, annotations: list = None, start: str = None, status: str = None, entry: str = None, modified: str = None, id: int = None, uuid: str = None, imask: str = None, end: str = None, recur: str = None, rtype: str = None, mask: str = None, parent: str = None):

        self.description = description
        """Task description"""

        self.annotations = annotations
        """A list of Task annotations (TaskNote objects)"""

        self.priority = priority
        """Task priority"""

        self.urgency = urgency
        """Task urgency"""

        self.project = project
        """Task project"""

        self.start = start
        """datetime object if task is started"""
        if self.start:
            self.start = datetime.fromisoformat(self.start)

        self.end = end
        if self.end:
            self.end = datetime.fromisoformat(self.end)

        self.status = status
        """current task status"""

        if entry:
            self.entry = datetime.fromisoformat(entry)
            """datetime of the task creation date"""

        if modified:
            self.modified = datetime.fromisoformat(modified)
            """datetime of the task last modification"""

        self.due = due
        """datetime of the task due date"""
        if self.due:
            try:
                self.due = datetime.fromisoformat(self.due)
            except ValueError:
                # might be a keyword like 'tomorrow' for adding tasks
                pass

        self.uuid = uuid
        self.recur = recur
        self.rtype = rtype
        self.mask = mask
        self.imask = imask
        self.parent = parent

        # If the current task is active, then we have an identifier
        self.id = id
        if not self.id:
            self.id = uuid

        self.active = False
        try:
            int(self.id)
            self.active = True
        except ValueError:
            # self.id == self.uuid
            pass
        except TypeError:
            # may be a new task
            pass

        if self.annotations:
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
        task_cmd = TasklUtils.get_task_command()
        print(task_cmd)

    def add(self) -> Self:
        task_cmd = TasklUtils.get_task_command()

        task_opts = []
        if self.description:
            task_opts.append(self.description)
        if self.project:
            task_opts.append(f'project:{self.project}')
        if self.due:
            task_opts.append(f'due:{self.due}')
        if self.priority:
            task_opts.append(f'priority:{self.priority}')

        cmd_add = [task_cmd, 'add'] + task_opts
        task_call = run(cmd_add, capture_output=True, text=True)
        if not task_call.returncode == 0:
            if task_call.returncode == 127:
                raise TaskCommandNotFound(task_call.stderr)
            raise ErrorRunningTaskCommand(task_call.stderr)

        task_id = re.findall(r'\d+', task_call.stdout)
        try:
            int(task_id[0])
            self.id = task_id[0]
        except ValueError:
            # Could not extract the identifier from the output
            raise ErrorAddingNewTask(task_call.stderr)

        cmd_export = [task_cmd, str(self.id), 'export']
        task_call = run(cmd_export, capture_output=True, text=True)
        if not task_call.returncode == 0:
            if task_call.returncode == 127:
                raise TaskCommandNotFound(task_call.stderr)
            raise ErrorRunningTaskCommand(task_call.stderr)

        data = ast.literal_eval(task_call.stdout)
        if len(data) == 1:
            return Task(**data[0])
        else:
            raise ErrorAddingNewTask(task_call.stderr)

    def __repr__(self):
        return f'Taskl.Task(id={self.id})'
