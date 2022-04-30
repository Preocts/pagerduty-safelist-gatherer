"""Tests for sample"""
import os
from contextlib import redirect_stdout
from datetime import datetime
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pytest

import pd_ip_gatherer as pdip

SAMPLE = Path("tests/fixture_sample.md").open().read()
EXPECTED_IPS = {
    "192.168.1.1",
    "192.168.1.2",
    "127.0.0.1",
    "0.0.0.0",
    "255.255.255.255",
    "1.2.3.4",
}


@pytest.mark.parametrize(
    ("address"),
    (
        ("192.168.1.1"),
        ("127.0.0.1"),
        ("0.0.0.0"),
        ("255.255.255.255"),
        ("999.999.999.999"),
        ("1.2.3.4"),
    ),
)
def test_extract_ip_addresses(address: str) -> None:
    results = pdip._extract_ip_addresses(address)

    assert results[0] == address


def test_extract_ip_addresses_from_sample() -> None:
    results = pdip._extract_ip_addresses(SAMPLE)

    print(results)

    assert len(set(results) - EXPECTED_IPS) == 0


def test_get_developer_doc_success() -> None:
    expected_starts_with = "# pagerduty-safelist-gatherer"
    mocker = {
        "PDIPGATHER_URL": "raw.githubusercontent.com",
        "PDIPGATHER_ROUTE": "/Preocts/pagerduty-safelist-gatherer/main/README.md",
    }
    with patch.dict(os.environ, mocker):

        result = pdip._get_developer_doc()

    assert result
    assert result.startswith(expected_starts_with)


def test_get_developer_doc_failure() -> None:
    mocker = {
        "PDIPGATHER_URL": "raw.githubusercontent.com",
        "PDIPGATHER_ROUTE": "/Preocts/pagerduty-safelist-gatherer/main/EGG.md",
    }
    with patch.dict(os.environ, mocker):

        result = pdip._get_developer_doc()

    assert result is None


def test_get_safelist() -> None:
    mocker = {
        "PDIPGATHER_URL": "raw.githubusercontent.com",
        "PDIPGATHER_ROUTE": "/Preocts/pagerduty-safelist-gatherer/main/tests/fixture_sample.md",  # noqa E501
    }
    with patch.dict(os.environ, mocker):
        with patch.object(pdip, "_get_appsite_webhooks", return_value=[]):

            results = pdip.get_safelist()

    assert len(set(results) - EXPECTED_IPS) == 0


def test_console_out() -> None:
    mocker = {
        "PDIPGATHER_URL": "raw.githubusercontent.com",
        "PDIPGATHER_ROUTE": "/Preocts/pagerduty-safelist-gatherer/main/tests/fixture_sample.md",  # noqa E501
    }
    with patch.dict(os.environ, mocker):
        with patch.object(pdip, "_get_appsite_webhooks", return_value=[]):
            with redirect_stdout(StringIO()) as con_cap:

                result = pdip._console_output()

                clean_capture = {
                    line for line in con_cap.getvalue().split("\n") if line
                }

    assert result == 0
    assert len(clean_capture - EXPECTED_IPS) == 0


def test_appsite_webhooks() -> None:
    results = pdip._get_appsite_webhooks()

    assert results


def tet_appsite_post_eol_date() -> None:
    hold_value = pdip.WEBHOOKSITE_EOL
    try:
        pdip.WEBHOOKSITE_EOL = datetime(2021, 5, 5, 14, 0, 0)

        results = pdip._get_appsite_webhooks()

        assert not results

    finally:
        pdip.WEBHOOKSITE_EOL = hold_value
