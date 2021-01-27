## 0.0.1

Initial commit, list of features:

* /register - Sign up for receiving new issue
* /start - Sign up for receiving new issue
* /unregister - Stop receiving new issue
* /watch ID... - Watch one or multiple issue modification
* /list_watchers - List issue subscription
* /delete_watcher ID... - Delete issue subscription
* /help - Print help message

## 0.0.2

Instead of user queue we use changestream of mongodb, to notify change of issues.
Watch also comments on issue.
Add /version command
Map /start -> /register
