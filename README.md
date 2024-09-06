# taskl
Simple python library for communicating with [TaskWarrior](https://taskwarrior.org/) > v3

## Installation

### Install via pip

work in progress

## Quick start

```python
from taskl import TaskWarrior
from taskl import Task

taskw = TaskWarrior()
pending_tasks = taskw.get_pending_tasks()
project_tasks = taskw.get_project_tasks('shopping')

# Add a new task
task_description = Task(description='My new task', project='Shopping', due='tomorrow')
new_task = task_description.add()
print(new_task)

# [Taskl.Task(id=1), Taskl.Task(id=2), Taskl.Task(id=3), Taskl.Task(id=4)]
# [Taskl.Task(uuid=b59ba870-cd29-4707-873e-4d3ba41bfb97), Taskl.Task(uuid=0a047015-1087-4e16-8778-8267cb8f4a6f)]
# Taskl.Task(id=30)
```

## Documentation

taskl documentation: https://mawigh.github.io/taskl/taskl.html