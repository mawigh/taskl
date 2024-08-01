
from taskl import TaskWarrior

my_tasks = TaskWarrior()

print("Projects:")
print(my_tasks.get_projects())

print("Project tasks for Jupyter:")
print(my_tasks.get_project_tasks('Jupyter'))