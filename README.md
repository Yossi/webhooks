webhooks
========

Little server to listen to webhook calls from github

While this can run under apache, the actual git pull will fail unless you royaly mess up the permisions in your directory.

Better to simply execute webhooks.py from a user who will succeed with a git pull.
