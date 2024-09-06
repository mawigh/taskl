from taskl import TaskWarrior
from taskl import Task

taskw = TaskWarrior()

# adding a new task
task_description = Task(description='My new task', project='Shopping', due='tomorrow')
new_task = task_description.add()
print(new_task)
