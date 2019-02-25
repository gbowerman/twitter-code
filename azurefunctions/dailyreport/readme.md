# Social media reporter for Teams

This Python-based Twitter search tool is designed to be triggered as an Azure Function using a daily Timer Trigger, and post to a Microsoft Teams webhook.

This code makes use of the Azure Functions `TimerTrigger`, which makes it easy to execute functions on a schedule.

## Advantages of running as a schedule-based Azure Function

- __Before__: Windows scheduled task that would run on a laptop at a fixed time or the next time it was opened. I.e. single point of failure.
- __After__: serverless i.e. no infrastructure dependency.

- __Before__: Twitter credentials, Teams webhook, search strings stored locally in config file.
- __After__: Config details stored as app settings configurable/updateable in Azure Portal.

## App settings configured in Azure Portal

Application Settings are encrypted at rest and transmitted over an encrypted channel. Set these in the Azure Portal, and they appear as environment variables to the Python code.

### Access settings for Tweepy
- accessToken - Twitter accessToken
- accessTokenSecret - Twitter token secret
- consumerKey - Twitter consumer key
- consumerSecret - Twitter consumer secret

### Twitter search settings
- searchStrings - Search strings for Twitter query e.g. ["azure+linux", "azure+OSS", "azure+%22red+hat%22"]

### Microsoft Teams webhook settings
- teamsMsgTitle - Message title for Teams message
- teamsWebhook - webhook for specific Teams channel