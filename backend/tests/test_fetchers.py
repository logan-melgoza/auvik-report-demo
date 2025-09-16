import pytest
import requests
from unittest.mock import patch, MagicMock
from datetime import datetime
import os

# Fake environment variables for testing
os.environ["BASE_URL"] = "http://fake-base"
os.environ["AUVIK_USERNAME"] = "user"
os.environ["AUVIK_API_KEY"] = "key"
os.environ["MAIN_DOMAIN_PREFIX"] = "prefix"

from auvik_report.production.fetchers import (
    format_date_range,
    fetch_paginated_data,
    fetch_tenants,
    fetch_open_alerts,
    fetch_device_stats,
    fetch_device_availability_stats,
    fetch_interface_stats,
)

############################
# Tests for format_date_range
############################
def test_format_date_range_returns_correct_format():
    start, end = format_date_range(30)
    assert start.endswith("Z")
    assert end.endswith("Z")
    assert "T" in start
    assert "T" in end

def test_format_date_range_time_difference():
    start, end = format_date_range(10)
    dt_start = datetime.strptime(start, "%Y-%m-%dT%H:%M:%S.000Z")
    dt_end = datetime.strptime(end, "%Y-%m-%dT%H:%M:%S.000Z")
    assert (dt_end - dt_start).days == 10

################################
# Tests for fetch_paginated_data
################################
@patch("auvik_report.production.fetchers.requests.get")
def test_fetch_paginated_data_single_page(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = {"data": [{"id": 1}], "links": {}}
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    result = fetch_paginated_data("http://fake-url.com")
    assert result == [{"id": 1}]

@patch("auvik_report.production.fetchers.requests.get")
def test_fetch_paginated_data_multiple_pages(mock_get):
    first_page = MagicMock()
    first_page.json.return_value = {
        "data": [{"id": 1}],
        "links": {"next": "http://fake-url.com/page2"},
    }
    first_page.raise_for_status.return_value = None

    second_page = MagicMock()
    second_page.json.return_value = {"data": [{"id": 2}], "links": {}}
    second_page.raise_for_status.return_value = None

    mock_get.side_effect = [first_page, second_page]

    result = fetch_paginated_data("http://fake-url.com/page1")
    assert result == [{"id": 1}, {"id": 2}]

@patch("auvik_report.production.fetchers.requests.get")
def test_fetch_paginated_data_network_error(mock_get):
    mock_get.side_effect = requests.exceptions.RequestException("Network failure")
    with pytest.raises(RuntimeError, match="Network/HTTP error"):
        fetch_paginated_data("http://fake-url.com")

@patch("auvik_report.production.fetchers.requests.get")
def test_fetch_paginated_data_invalid_json(mock_get):
    mock_response = MagicMock()
    mock_response.json.side_effect = ValueError("Bad JSON")
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    with pytest.raises(RuntimeError, match="Invalid JSON"):
        fetch_paginated_data("http://fake-url.com")

@patch("auvik_report.production.fetchers.requests.get")
def test_fetch_paginated_data_circular_pagination(mock_get):
    first_page = MagicMock()
    first_page.json.return_value = {
        "data": [{"id": 1}],
        "links": {"next": "http://fake-url.com/page1"},
    }
    first_page.raise_for_status.return_value = None
    mock_get.return_value = first_page

    with pytest.raises(RuntimeError, match="circular pagination"):
        fetch_paginated_data("http://fake-url.com/page1")

################################
# Tests for fetcher functions
################################
@patch("auvik_report.production.fetchers.fetch_paginated_data", return_value=[{"tenant": "A"}])
def test_fetch_tenants(mock_fetch):
    result = fetch_tenants()
    assert result == [{"tenant": "A"}]
    assert mock_fetch.called

@patch("auvik_report.production.fetchers.fetch_paginated_data", return_value=[{"alert": "open"}])
def test_fetch_open_alerts(mock_fetch):
    result = fetch_open_alerts("tenant123")
    assert result == [{"alert": "open"}]
    url = mock_fetch.call_args[0][0]
    assert "tenant123" in url

@patch("auvik_report.production.fetchers.fetch_paginated_data", return_value=[{"stat": "cpu"}])
def test_fetch_device_stats_no_type(mock_fetch):
    result = fetch_device_stats("tenant123", "cpuUtilization")
    assert result == [{"stat": "cpu"}]
    url = mock_fetch.call_args[0][0]
    assert "device/cpuUtilization" in url
    assert "filter[deviceType]" not in url

@patch("auvik_report.production.fetchers.fetch_paginated_data", return_value=[{"stat": "cpu"}])
def test_fetch_device_stats_with_type(mock_fetch):
    result = fetch_device_stats("tenant123", "cpuUtilization", type="router")
    assert result == [{"stat": "cpu"}]
    url = mock_fetch.call_args[0][0]
    assert "filter[deviceType]=router" in url

@patch("auvik_report.production.fetchers.fetch_paginated_data", return_value=[{"uptime": "99%"}])
def test_fetch_device_availability_stats(mock_fetch):
    result = fetch_device_availability_stats("tenant123")
    assert result == [{"uptime": "99%"}]
    url = mock_fetch.call_args[0][0]
    assert "deviceAvailability/uptime" in url

@patch("auvik_report.production.fetchers.fetch_paginated_data", return_value=[{"iface": "eth0"}])
def test_fetch_interface_stats_default(mock_fetch):
    result = fetch_interface_stats("device123", "bandwidth")
    assert result == [{"iface": "eth0"}]
    url = mock_fetch.call_args[0][0]
    assert "interface/bandwidth" in url
    assert "interfaceType" not in url

@patch("auvik_report.production.fetchers.fetch_paginated_data", return_value=[{"iface": "eth1"}])
def test_fetch_interface_stats_with_type(mock_fetch):
    result = fetch_interface_stats("device123", "bandwidth", type="wifi")
    assert result == [{"iface": "eth1"}]
    url = mock_fetch.call_args[0][0]
    assert "filter[interfaceType]=wifi" in url
