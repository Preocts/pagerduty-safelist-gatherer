"""
Gather PagerDuty webhook IP safelist from their help documents repo.

This replaces an extremely useful endpoint being removed on 05/05/2022. The
IPs pulled include both US and EU ranges with no distinction between them. Until
05/05/2022 both sources of truth are pulled and compiled into a single return.

Support Documentation:

https://support.pagerduty.com/docs/safelist-ips#webhooks

Developer Documentation:

https://developer.pagerduty.com/docs/ZG9jOjQ4OTcxMDMx-webhook-i-ps

Documentation Repo:

https://github.com/PagerDuty/developer-docs
https://raw.githubusercontent.com/PagerDuty/developer-docs/main/docs/webhooks/11-Webhook-IPs.md

The url for the safelist is hardcoded, however you can override it.
    Set `PDIPGATHER_URL` environ variable to the desired url (no HTTPS://)
    Set `PDIPGATHER_ROUTE` environ variable to the desired route

    Example (shows defaults):
        PDIPGATHER_URL="raw.githubusercontent.com"
        PDIPGATHER_ROUTE="/PagerDuty/developer-docs/main/docs/webhooks/11-Webhook-IPs.md

Example Usage:

    Output to console:
        $ pd-ip-gatherer

    Importing as module:
        import pd_ip_gatherer

        ip_list = pd_ip_gatherer.get_safelist()
"""
from __future__ import annotations

import json
import logging
import os
import re
from datetime import datetime
from http.client import HTTPSConnection


# NOTE: Does not validate IP address ranges
IP_PATTERN = re.compile(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})")
PDIPGATHER_URL = "raw.githubusercontent.com"
PDIPGATHER_ROUTE = "/PagerDuty/developer-docs/main/docs/webhooks/11-Webhook-IPs.md"
TIMEOUT_SECONDS = 3

# Documented end of life date for programmatic endpoint
WEBHOOKSITE_EOL = datetime(2022, 5, 5, 14, 0, 0, 0)

log = logging.getLogger(__name__)


def _extract_ip_addresses(text: str) -> list[str]:
    """Extract all IP addresses from given string, can return empty list."""
    return IP_PATTERN.findall(text)


def _get_appsite_webhooks() -> list[str]:
    """Pull IPs from app.pagerduty.com/webhook_ips site. Ends function on 05/05/2022"""
    if datetime.utcnow() > WEBHOOKSITE_EOL:
        return []

    urls = ["app.pagerduty.com", "app.eu.pagerduty.com"]
    full_list: list[str] = []

    for url in urls:

        conn = HTTPSConnection(host=url, timeout=TIMEOUT_SECONDS)

        conn.request("GET", "/webhook_ips")
        resp = conn.getresponse()

        if resp.status not in range(200, 300):
            log.error("Failed to get a response from /webhook_ip. %d", resp.status)
            continue

        full_list.extend(json.loads(resp.read().decode()))

    return full_list


def _get_developer_doc() -> str | None:
    """Pull developer doc from PagerDuty's GitHub page."""
    override_url = os.getenv("PDIPGATHER_URL")
    override_route = os.getenv("PDIPGATHER_ROUTE")

    url = override_url if override_url else PDIPGATHER_URL
    route = override_route if override_route else PDIPGATHER_ROUTE

    conn = HTTPSConnection(host=url, timeout=TIMEOUT_SECONDS)

    conn.request("GET", route)
    resp = conn.getresponse()

    if resp.status not in range(200, 300):
        log.error("Failed to get a proper response from GitHub. %d", resp.status)
        return None

    return resp.read().decode()


def get_safelist() -> set[str]:
    """Return all safelist IPs (US and Euro region) in the form of a list."""
    doc_set = set(_extract_ip_addresses(_get_developer_doc() or ""))
    app_set = set(_get_appsite_webhooks())
    return doc_set.union(app_set)


def _console_output() -> int:
    """Print all safelist IPs, new-line separated, to the stdout."""
    print("\n".join(get_safelist()))
    return 0


if __name__ == "__main__":
    raise SystemExit(_console_output())
