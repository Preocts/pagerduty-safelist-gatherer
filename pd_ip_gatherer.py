"""
Gather PagerDuty webhook IP safelist from their help documents repo

This replaces an extremely useful endpoint being removed on 05/05/2022.

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
        $ python pd_ip_gatherer.py

    Importing as module:
        import pd_ip_gatherer

        ip_list = pd_ip_gatherer.get_safelist()
"""
from __future__ import annotations

import logging
import os
import re
from http.client import HTTPSConnection


# NOTE: Does not validate IP address ranges
IP_PATTERN = re.compile(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})")
PDIPGATHER_URL = "raw.githubusercontent.com"
PDIPGATHER_ROUTE = "/PagerDuty/developer-docs/main/docs/webhooks/11-Webhook-IPs.md"
TIMEOUT_SECONDS = 3

log = logging.getLogger(__name__)


def extract_ip_addresses(text: str) -> list[str]:
    """Extract all IP addresses from given string, can return empty list"""
    return IP_PATTERN.findall(text)


def get_developer_doc() -> str | None:
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


def get_safelist() -> list[str]:
    """Rerturn all safelist IPs (US and Euro region) in the form of a list"""
    return extract_ip_addresses(get_developer_doc() or "")


if __name__ == "__main__":
    print("\n".join(get_safelist()))
    raise SystemExit(0)
