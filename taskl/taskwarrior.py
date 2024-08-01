import sqlite3
import ast
from os import environ, path
from configparser import ConfigParser
from .exceptions import TaskWarriorDatabaseNotFound
from .task import Task


class TaskWarrior:

    def __init__(self, task_dir=None, task_rc_file=None, task_database=None):

        self.task_dir = task_dir
        self.task_rc_file = task_rc_file
        self.task_database = task_database

        # a list of the current active (pending) tasks - All tasks in the current working set have an id
        self.working_set = []

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
        self.taskrc = ConfigParser()
        self.taskrc.read_string(config)

        if not self.task_dir:
            self.task_dir = self.taskrc.get('config', 'data.location')
            if not self.task_dir:
                self.task_dir = environ.get('HOME', '~') + '/.task'

        if not self.task_database:
            self.task_database = self.task_dir + '/taskchampion.sqlite3'

        if not path.isfile(self.task_database):
            raise TaskWarriorDatabaseNotFound()

        self.connection = sqlite3.connect(self.task_database)

    def get_all_tasks(self) -> list[Task]:
        all_tasks = []
        self.working_set = []
        if self.connection:
            cur = self.connection.cursor()
            stmt = cur.execute('SELECT uuid, data FROM tasks')
            data = stmt.fetchall()

            if len(data) >= 1:
                for raw_task in data:
                    task_data = ast.literal_eval(raw_task[1])
                    task_data['uuid'] = raw_task[0]
                    stmt = cur.execute('SELECT id FROM working_set WHERE uuid=?', (raw_task[0],))
                    task_id = stmt.fetchone()

                    # manipulate task data using configuration values from .taskrc
                    # TODO

                    if task_id:
                        task_data['id'] = task_id[0]
                        self.working_set.append(Task(task_data))

                    all_tasks.append(Task(task_data))

        return all_tasks

    def get_pending_tasks(self) -> list[Task]:
        tasks = self.get_all_tasks()
        pending_tasks = [task for task in tasks if task.status == 'pending']
        return pending_tasks

    def get_completed_tasks(self) -> list[Task]:
        tasks = self.get_all_tasks()
        completed = [task for task in tasks if task.status == 'completed']
        return completed

    def get_projects(self) -> list[str]:
        tasks = self.get_all_tasks()
        projects = list(set([task.project for task in tasks if task.project is not None]))
        return projects

    def get_project_tasks(self, project: str, only_pending: bool = True) -> list[Task]:
        if only_pending:
            tasks = self.get_pending_tasks()
        else:
            tasks = self.get_all_tasks()
        project_tasks = [task for task in tasks if task.project == project]
        return project_tasks

    def get_tasks_without_project(self) -> list[Task]:
        tasks = self.get_all_tasks()
        tasks = [task for task in tasks if task.project == '' or task.project is None]
        return tasks
