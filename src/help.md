# commands

Anything sent without a command is assumed to be a new task to be added

## actions on tasks 
- `/add <task-text>` - Add a new task
- `/do <id> [id [id [id]...]]` - Do task(s)
- `/priority <priority> <id> [id [id [id]...]]` - Set the priority of task(s)
- `/rm <id> [id [id [id]...]]` - Remove task(s)
- `/undo <id> [id [id [id]...]]` - undo task(s)

### fuzzy actions
- `/fdo <text to match>`
- `/fpriority <text to match>`
- `/frm <text to match>`
- `/fundo <text to match>`

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
