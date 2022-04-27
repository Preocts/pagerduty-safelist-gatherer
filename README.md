# pagerduty-safelist-gatherer

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Python package](https://github.com/Preocts/pagerduty-safelist-gatherer/actions/workflows/python-tests.yml/badge.svg?branch=main)](https://github.com/Preocts/pagerduty-safelist-gatherer/actions/workflows/python-tests.yml)

Gather PagerDuty webhook IP safelist from their help documents repo

This is to replace an extremely useful endpoint they are removing for some
reason that would provide a simple, programmatically consumable IP list. Smile.

https://github.com/PagerDuty/developer-docs

https://raw.githubusercontent.com/PagerDuty/developer-docs/main/docs/webhooks/11-Webhook-IPs.md

The url for the safelist is hardcoded, however you can override it.

- Set `PDIPGATHER_URL` environ variable to the desired url (no HTTPS://)
- Set `PDIPGATHER_ROUTE` environ variable to the desired route

Example (shows defaults):
```bash
export PDIPGATHER_URL="raw.githubusercontent.com"
export PDIPGATHER_ROUTE="/PagerDuty/developer-docs/main/docs/webhooks/11-Webhook-IPs.md
```

## Requirements

- [Python](https://python.org) >= 3.8

## Internal Links

- [Development Installation Guide](docs/development.md)
- [Repo documentation](docs/)

---

## Example Usage

Output to console:

```bash
$ python pd_ip_gatherer.py
```

Importing as module:

```py
import pd_ip_gatherer

ip_list = pd_ip_gatherer.get_safelist()
```
