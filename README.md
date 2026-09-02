# Todoist Bot for Telegram

An unofficial Telegram interface for [Todoist](https://todoist.com/), originally
available as [@Todoist_bot](https://t.me/Todoist_bot).

![Todoist Bot logo](logo.png)

The bot lets users connect a Todoist account through OAuth, create tasks from Telegram,
receive reminder notifications, and browse their projects and labels.

> [!IMPORTANT]
> This is a legacy project built against older Telegram and Todoist APIs. It is shared
> as an example of a working integration, not as a ready-to-deploy current release.
> Review its dependencies, API compatibility, and security model before operating it.

## Features

- Todoist authorization through OAuth.
- Task creation from Telegram messages.
- Todoist reminder notifications delivered through Telegram.
- Project and label listing.

## Data handling

The application stores the Telegram profile fields, Todoist account ID, OAuth access
token, and activity timestamps required to provide the integration. A self-hosted
deployment is responsible for protecting the database, application secrets, logs, and
backups and for providing an appropriate privacy notice to its users.

## Contributing

Bug reports and pull requests are welcome, but please account for the project's legacy
dependencies before proposing deployment or feature changes.

## License

[MIT](LICENSE)
