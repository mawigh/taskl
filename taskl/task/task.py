import ast
import re
from datetime import datetime
from subprocess import run
from typing import Self, List

from .tasknote import TaskNote
from ..utils import TasklUtils
from ..exceptions import TaskCommandNotFound, ErrorRunningTaskCommand, ErrorAddingNewTask


class Task:
    """Base class of a TaskWarrior task
    """

    def __init__(self, description: str, annotations: List[TaskNote] = None, **kwargs):
        """Constructor for a TaskWarrior task. Object can be build using the TaskWarrior export functionality or to create new tasks using the add() method

        Use the TaskWarrior specific keywords like `project:` or `due:`

        Adding new tasks:
        ```python3
        from taskl.task import Task

        task_description = Task(description='My new task', project='Shopping', due='tomorrow')
        new_task = task_description.add()

        task_description2 = {'description': 'Grocery shopping', 'due': 'friday', 'priority': 'M'}
        init_task2 = Task(**task_description2)
        new_task2 = init_task2.add()
        ```

        Args:
            description (str): Task description
            annotations (List[TaskNote], optional): A list of annotations (taskl.TaskNote instances). Defaults to None.
            **kwargs (Any): TaskWarrior specific keywords like `project:`
        """

        self.description: str = description
        """A "description" field may not contain newline characters, but may contain other characters, properly escaped. See https://json.org for details."""

        self.project: str = kwargs.get('project')
        """A project is a single string. For example:
        `"project":"Personal Taxes"`

        Note that projects receive special handling, so that when a "." (U+002E) is used, it implies a hierarchy, which means the following two projects:
        ```
        "Home.Kitchen"
        "Home.Garden"
        ```
        are both considered part of the "Home" project.
        """

        self.annotations: list = kwargs.get('annotations')
        """A list of Task annotations (TaskNote objects)"""

        self.priority: str = kwargs.get('priority')
        """The "priority" field, if present, MAY contain one of the following strings:
        
        ```
        "priority":"H"
        "priority":"M"
        "priority":"L"
        ```
        These represent High, Medium and Low priorities. An absent priority field indicates no priority.
        """

        self.urgency: str = kwargs.get('urgency')
        """Task urgency"""

        self.start: str = kwargs.get('start')
        """To indicate that a task is being worked on, it MAY be assigned a "start" field. Such a task is then considered Active."""
        if self.start:
            self.start = datetime.fromisoformat(self.start)

        self.end: str = kwargs.get('end')
        """When a task is deleted or completed, is MUST be assigned an "end" field. It is not valid for a task to have an "end" field unless the status is also "completed" or "deleted". If a completed task is restored to the "pending" state, the "end" field is removed."""
        if self.end:
            self.end = datetime.fromisoformat(self.end)

        self.status: str = kwargs.get('status')
        """The status field describes the state of the task, which may ONLY be one of these literal strings:
        ```
        "status":"pending"
        "status":"deleted"
        "status":"completed"
        "status":"waiting"
        "status":"recurring"
        ```

        A pending task is a task that has not yet been completed or deleted. This is the typical state for a task.

        A deleted task is one that has been removed from the pending state, and MUST have an "end" field specified. Given the required "entry" and "end" field, it can be determined how long the task was pending.

        A completed task is one that has been removed from the pending state by completion, and MUST have an "end" field specified. Given the required "entry" and "end" fields, it can be determine how long the task was pending.

        A waiting task is ostensibly a pending task that has been hidden from typical view, and MUST have a "wait" field containing the date when the task is automatically returned to the pending state. If a client sees a task that is in the waiting state, and the "wait" field is earlier than the current date and time, the client MUST remove the "wait" field and set the "status" field to "pending".

        A recurring task is essentially a parent template task from which child tasks are cloned. The parent remains hidden from view, and contains a "mask" field that represents the recurrences. Each cloned child task has an "imask" field that indexes into the parent "mask" field, as well as a "parent" field that lists the UUID of the parent.
        """

        entry: str = kwargs.get('entry')
        if entry:
            self.entry = datetime.fromisoformat(entry)
            """This is the creation date of the task."""

        modified: str = kwargs.get('modified')
        if modified:
            self.modified = datetime.fromisoformat(modified)
            """A task MUST have a "modified" field set if it is modified. This field is of type "date", and is used as a reference when merging tasks."""

        self.due: str = kwargs.get('due')
        """A task MAY have a "due" field, which indicates when the task should be completed."""
        if self.due:
            try:
                self.due = datetime.fromisoformat(self.due)
            except ValueError:
                # might be a keyword like 'tomorrow' for adding tasks
                pass

        self.uuid: str = kwargs.get('uuid')
        """When a task is created, it MUST be assigned a new UUID by the client. Once assigned, a UUID field MUST NOT be modified. UUID fields are permanent."""
        self.recur: str = kwargs.get('recur')
        """The "recur" field is for recurring tasks, and specifies the period between child tasks, in the form of a duration value. The value is kept in the raw state (such as "3wks") as a string, so that it may be evaluated each time it is needed.
        """
        self.rtype: str = kwargs.get('rtype')
        self.mask: str = kwargs.get('mask')
        """A parent recurring task has a "mask" field that is an array of child status indicators. Suppose a task is created that is due every week for a month. The "mask" field will look like:
        `"----"`
        This mask has four slots, indicating that there are four child tasks, and each slot indicates, in this case, that the child tasks are pending ("-"). The possible slot indicators are:

        * `-` - Pending
        * `+` - Completed
        * `X` - Deleted
        * `W` - Waiting

        Suppose the first three tasks has been completed, the mask would look like this:
        `"+++-"`

        If there were only three indicators in the mask:
        `"+-+"`

        This would indicate that the second task is pending, the first and third are complete, and the fourth has not yet been generated.
        """
        self.imask: str = kwargs.get('imask')
        """Child recurring tasks have an "imask" field instead of a "mask" field like their parent. The "imask" field is a zero-based integer offset into the "mask" field of the parent.
If a child task is completed, one of the changes that MUST occur is to look up the parent task, and using "imask" set the "mask" of the parent to the correct indicator. This prevents recurring tasks from being generated twice.
        """
        self.parent: str = kwargs.get('parent')
        """A recurring task instance MUST have a "parent" field, which is the UUID of the task that has "status" of "recurring". This linkage between tasks, established using "parent", "mask" and "imask" is used to track the need to generate more recurring tasks."""

        # If the current task is active, then we have an identifier
        self.id: int = kwargs.get('id')
        """The current identifier of task
        
        If the task is in state pending, the id will be the active identifier. If the task is already completed or in state deleted, the id will be the UUID
        """
        if not self.id:
            self.id = kwargs.get('uuid')

        self.active: bool = False
        """Will be set to True, if the task is currently pending 
        """
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
        ...

    def add(self) -> Self:
        """This method can be used to add new TaskWarrior tasks.

        Raises:
            TaskCommandNotFound: Could not find command `task`
            ErrorRunningTaskCommand: Unknown error when running the task command
            ErrorAddingNewTask: Error when trying to add the new task

        Returns:
            Task: Returns a new Task() instance with all attributes given by TaskWarrior
        """
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
