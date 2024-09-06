from taskl import TaskWarrior

taskw = TaskWarrior()

# adding a new task
new_task = taskw.add_task(description='My new task', project='Shopping', due='tomorrow')
print(new_task)
