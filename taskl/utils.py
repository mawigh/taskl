from shutil import which

class TasklUtils:

    @staticmethod
    def get_task_command() -> str | None:
        """Get the absolute path of the TaskWarrior command task

        Returns:
            str | None: Returns the absolute path of the task command
        """
        return which('task')
