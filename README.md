# taskl
Simple python library for communicating with TaskWarrior > 3

## Quick start

```python
from taskl import TaskWarrior

taskw = TaskWarrior() # defaults to $HOME/.task/
pending_tasks = taskw.get_pending_tasks()
project_tasks = taskw.get_project_tasks('shopping')

# [Taskl.Task(id=1), Taskl.Task(id=2), Taskl.Task(id=3), Taskl.Task(id=4)]
# [Taskl.Task(uuid=b59ba870-cd29-4707-873e-4d3ba41bfb97), Taskl.Task(uuid=0a047015-1087-4e16-8778-8267cb8f4a6f)]
```
