class Task:

    def __init__(self, raw_task_data: dict):
        self.raw_task_data = raw_task_data

        self.description = self.raw_task_data.get('description')
        self.priority = self.raw_task_data.get('priority')
        self.project = self.raw_task_data.get('project')
        self.status = self.raw_task_data.get('status')
        self.due_date = self.raw_task_data.get('due')
        self.uuid = self.raw_task_data.get('uuid')

        # If the current task is active, then we have an identifier
        self.id = self.raw_task_data.get('id', None)
        self.active = False
        if self.id:
            self.active = True

    def get_priority(self):
        return self.priority

    def set_priority(self):
        ...

    def get_due_date(self):
        return self.due_date

    def complete(self):
        ...

    def delete(self):
        ...

    def __repr__(self):
        if self.id:
            return f'Taskl.Task(id={self.id})'
        return f'Taskl.Task(uuid={self.uuid})'
