# Name.com Auto DNS Updater

DynDNS forced a transition for my domain to Name.com. Name.com apparently doesn't support dynamic DNS updates, however, provide an API to do it.

Python script to query the external IP address and update the A-Records with Name.com to reflect the change (if any).

API Documentation can be found here:
https://www.name.com/api-docs

API Credentials and tokens can be generated, modified, and revoked here:
https://www.name.com/account/settings/api

Personal usage is set as a cron job on a FreeNAS machine with the command:

```cd /script/location/here/ && git pull && python updater.py```

Script must be run at least once manually before automating it as it prompts for credentials and input.

To reset the script, delete the generated .namedns_data file.

