
from taskl import TaskWarrior

my_tasks = TaskWarrior()

print('All:')
tasks = my_tasks.get_all_tasks()
print(tasks)

print('Pending:')
tasks = my_tasks.get_pending_tasks()
print(tasks[1].__dict__)

print('Completed:')
tasks = my_tasks.get_completed_tasks()
print(tasks)

print('Working set:')
print(my_tasks.working_set)
