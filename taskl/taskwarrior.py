import ast
from os import environ, path
from subprocess import run
from configparser import ConfigParser
from .exceptions import TaskCommandNotFound, ErrorRunningTaskCommand, NoTaskGiven
from .task.task import Task
from .utils import TasklUtils


class TaskWarrior:

    def __init__(self, task_dir: str = None, task_rc_file: str = None):
        """Initializing taskl

        Args:
            task_dir (str, optional): Custom TaskWarrior task directory. Defaults to None.
            task_rc_file (str, optional): Custom TaskWarrior configuration file (.taskrc). Defaults to None.
        """

        self.task_dir = task_dir
        """The TaskWarrior task directory"""

        self.task_rc_file = task_rc_file
        """The TaskWarrior configuration file (.taskrc)"""

        # a list of the current active (pending) tasks - All tasks in the current working set have an id
        self.working_set = []
        """A list of the current active (pending) TaskWarrior tasks - All tasks in the current working set have an identifier (integer)"""

        if not self.task_rc_file:
            # first check if the user set the corresponding env var
            env_taskrc = environ.get('TASKRC', None)
            if env_taskrc:
                self.task_rc_file = env_taskrc
            else:
                # if nothing is given, using the default location
                self.task_rc_file = environ.get('HOME', '~') + '/.taskrc'

        # reading taskrc configuration file
        with open(self.task_rc_file, 'r') as f:
            # we manually need to add a section so that the ConfigParser() can read the configuration file
            config = '[config]\n' + f.read()
            config = config.replace('include', 'include=')
        self.taskrc = ConfigParser()
        """[ConfigParser](https://docs.python.org/3/library/configparser.html#configparser.ConfigParser) object of the TaskWarrior .taskrc file"""
        self.taskrc.read_string(config)

        if not self.task_dir:
            self.task_dir = self.taskrc.get('config', 'data.location')
            if not self.task_dir:
                self.task_dir = environ.get('HOME', '~') + '/.task'

    def get_taskrc(self) -> ConfigParser:
        """Returns a [ConfigParser](https://docs.python.org/3/library/configparser.html#configparser.ConfigParser) object of the TaskWarrior .taskrc configuration file

        Returns:
            ConfigParser: [ConfigParser](https://docs.python.org/3/library/configparser.html#configparser.ConfigParser) object of the TaskWarrior configuration file
        """
        return self.taskrc

    def task_export(self, id: int | str = None) -> list | None:
        """Get the raw task export of all tasks or a given task if the task id is set

        Args:
            id (int | str, optional): The task identifier or the task uuid. Defaults to None.

        Raises:
            TaskCommandNotFound: Could not find the task command - Is TaskWarrior installed?
            ErrorRunningTaskCommand: Unknown error running the task command

        Returns:
            list | None: _description_
        """
        cmd = [TasklUtils.get_task_command(), 'export']
        if id:
            cmd.insert(1, str(id))

        task_call = run(cmd, capture_output=True, text=True)
        if not task_call.returncode == 0:
            if task_call.returncode == 127:
                raise TaskCommandNotFound(task_call.stderr)
            raise ErrorRunningTaskCommand(task_call.stderr)

        data = ast.literal_eval(task_call.stdout)
        if len(data) >= 1:
            return data
        return None

    def get_all_tasks(self, include_deleted: bool = False) -> list[Task]:
        """Get all TaskWarrior tasks

        Args:
            include_deleted (bool, optional): Include also all deleted tasks. Defaults to False.

        Returns:
            list[Task]: Returns a list of all tasks (Task objects)
        """
        all_tasks = []
        self.working_set = []

        data = self.task_export()

        if len(data) >= 1:
            for task_data in data:
                task_status = task_data.get('status')
                if include_deleted is False and task_status == 'deleted':
                    continue

                task_id = task_data.get('id')
                if not task_id == 0:
                    self.working_set.append(Task(**task_data))

                all_tasks.append(Task(**task_data))

        return all_tasks

    def add_task(self, description: str, **kwargs) -> Task:
        """Method for creating a new TaskWarrior task.

        Use the TaskWarrior specific keywords like `project:` or `due:`

        Example:
        ```python3
        from taskl import TaskWarrior

        taskw = TaskWarrior()
        new_task = taskw.add_task(description='Grocery shopping', project='Shopping', due='tomorrow')
        ```

        Args:
            description (str): The task description
            **kwargs (Any): TaskWarrior specific keywords like `project:`

        Returns:
            Task: The new Task instance
        """
        task_description = Task(description=description, **kwargs)
        return task_description.add()

    def complete_task(self, id: int) -> bool | NoTaskGiven:
        """Mark a task as complete (done) using the active task id

        Args:
            id (int): the task id

        Raises:
            TaskCommandNotFound: Could not find the task command - Is TaskWarrior installed?
            NoTaskGiven: Task cannot be found

        Returns:
            bool | NoTaskGiven: Returns True if successful
        """
        cmd = [TasklUtils.get_task_command(), id, 'done']
        task_call = run(cmd, capture_output=True, text=True)
        if not task_call.returncode == 0:
            if task_call.returncode == 127:
                raise TaskCommandNotFound(task_call.stderr)
            elif task_call.returncode == 1:
                raise NoTaskGiven(task_call.stderr)

        return True

    def delete_task(self, id: int) -> bool | NoTaskGiven:
        """Delete a specific task using the task id

        Args:
            id (int): the active task identifier

        Raises:
            TaskCommandNotFound: Could not find the task command - Is TaskWarrior installed?
            NoTaskGiven: Task cannot be found

        Returns:
            bool | NoTaskGiven: Returns True if successful
        """
        cmd = [TasklUtils.get_task_command(), id, 'delete']
        task_call = run(cmd, capture_output=True, text=True)
        if not task_call.returncode == 0:
            if task_call.returncode == 127:
                raise TaskCommandNotFound(task_call.stderr)
            elif task_call.returncode == 1:
                raise NoTaskGiven(task_call.stderr)

        return True

    def get_task(self, id: str | int) -> Task | None:
        """Get a specific task using the id or uuid

        Args:
            id (str | int): The task id. Can be the active id or the task uuid

        Returns:
            Task | None: Returns the Task object, or None if Task cannot be found 
        """
        # ToDo: Documentation -> If str: uuid, if int: id

        data = self.task_export(id=id)
        if data:
            return Task(**data[0])
        return None

    def get_pending_tasks(self) -> list[Task]:
        """Get all pending tasks

        Returns:
            list[Task]: Returns a list of pending tasks (Task objects)
        """
        tasks = self.get_all_tasks()
        pending_tasks = [task for task in tasks if task.status == 'pending']
        return pending_tasks

    def get_recurring_tasks(self) -> list[Task]:
        """Get all recurring tasks

        Returns:
            list[Task]: Returns a list of recurring tasks (Task objects)
        """
        tasks = self.get_all_tasks()
        recurring_tasks = [task for task in tasks if task.status == 'recurring']
        return recurring_tasks

    def get_completed_tasks(self) -> list[Task]:
        """Get all completed tasks

        Returns:
            list[Task]: Returns a list of completed tasks (Task objects)
        """
        tasks = self.get_all_tasks()
        completed = [task for task in tasks if task.status == 'completed']
        return completed

    def get_deleted_tasks(self) -> list[Task]:
        """Get all deleted tasks

        Returns:
            list[Task]: Returns a list of deleted tasks (Task objects)
        """
        tasks = self.get_all_tasks(include_deleted=True)
        deleted = [task for task in tasks if task.status == 'deleted']
        return deleted

    def get_projects(self) -> list[str]:
        """Get all known projects

        Returns:
            list[str]: Returns a list of all known projects
        """
        tasks = self.get_all_tasks()
        projects = list(set([task.project for task in tasks if task.project is not None]))
        return projects

    def get_project_tasks(self, project: str, only_pending: bool = True) -> list[Task]:
        """Get tasks for a specific project

        Args:
            project (str): The name of the project
            only_pending (bool, optional): Returning only pending tasks. Defaults to True.

        Returns:
            list[Task]: returns a list of tasks (Task objects)
        """
        if only_pending:
            tasks = self.get_pending_tasks()
        else:
            tasks = self.get_all_tasks()
        project_tasks = [task for task in tasks if task.project == project]
        return project_tasks

    def get_child_tasks(self, uuid: str) -> list[Task]:
        """

        Args:
            uuid (str): The task uuid

        Returns:
            list[Task]: returns a list of tasks (Task objects)
        """
        tasks = self.get_all_tasks()
        child_tasks = [task for task in tasks if task.parent == uuid]
        return child_tasks

    def get_tasks_without_project(self, only_pending: bool = True) -> list[Task]:
        """Get TaskWarrior tasks without a named project

        Args:
            only_pending (bool, optional): Returning only pending tasks. Defaults to True.

        Returns:
            list[Task]: returns a list of tasks (Task objects)
        """
        if only_pending:
            tasks = self.get_pending_tasks()
        else:
            tasks = self.get_all_tasks()
        tasks = [task for task in tasks if task.project == '' or task.project is None]
        return tasks
