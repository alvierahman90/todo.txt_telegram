# commands

Anything sent without a command is assumed to be a new task to be added

## actions on tasks 
- `/add <task-text>` - Add a new task
- `/do` - Mark a task as done
- `/priority` - Set the priority of a task
- `/rm` - Remove a task 
- `/undo` - Mark a task as not done

## general 
- `/export` - Send all tasks as plaintext
- `/help` - Show help information
- `/ls [filters]` - List tasks
- `/last` - Run the last command sent
- `/marco` - Test if bot is up


## /ls filters 
- `f[ilter]:<text>` - Tasks must have this text in it
- `!f[ilter]:<text>` - Tasks must **not** have this text in  it
- `:show-done` - Show and include done tasks
- `:only-done` - Show only done tasks
