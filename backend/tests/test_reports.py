import pytest
from unittest.mock import patch

from auvik_report.production.reports import (
    uptime_report,
    open_alerts,
    bandwidth_report,
    device_health,
)

############################
# Tests for uptime_report
############################
@patch("auvik_report.production.reports.fetch_device_availability_stats")
def test_uptime_report_computes_averages(mock_fetch):
    mock_fetch.return_value = [
        {
            "relationships": {"device": {"data": {"deviceType": "router"}}},
            "attributes": {"stats": [{"data": [[1, 90], [2, 100]]}]},
        },
        {
            "relationships": {"device": {"data": {"deviceType": "switch"}}},
            "attributes": {"stats": [{"data": [[1, 80]]}]},
        },
    ]
    result = uptime_report("tenant1")
    assert result["Router"] == pytest.approx(95.0, rel=1e-3)
    assert result["Switch"] == pytest.approx(80.0, rel=1e-3)


@patch("auvik_report.production.reports.fetch_device_availability_stats")
def test_uptime_report_handles_access_point_name(mock_fetch):
    mock_fetch.return_value = [
        {
            "relationships": {"device": {"data": {"deviceType": "accessPoint"}}},
            "attributes": {"stats": [{"data": [[1, 50], [2, 100]]}]},
        }
    ]
    result = uptime_report("tenant1")
    assert "Access Point" in result
    assert result["Access Point"] == 75.0


############################
# Tests for open_alerts
############################
@patch("auvik_report.production.reports.fetch_open_alerts")
def test_open_alerts_counts_by_severity_and_status(mock_fetch):
    mock_fetch.return_value = [
        {"attributes": {"severity": "critical", "status": "active"}},
        {"attributes": {"severity": "critical", "status": "paused"}},
        {"attributes": {"severity": "warning", "status": "paused"}},
    ]
    result = open_alerts("tenant1")
    assert result["Critical"] == 2
    assert result["Warning"] == 1
    assert result["Paused"] == 2  # extra count when status == Paused


@patch("auvik_report.production.reports.fetch_open_alerts")
def test_open_alerts_no_devices(mock_fetch):
    mock_fetch.return_value = []
    result = open_alerts("tenant1")
    assert result == {"No Devices": 0}


############################
# Tests for bandwidth_report
############################
@patch("auvik_report.production.reports.max_interface_average")
@patch("auvik_report.production.reports.bandwidth_average")
@patch("auvik_report.production.reports.fetch_device_stats")
def test_bandwidth_report_builds_entries(mock_fetch, mock_bandwidth, mock_max_iface):
    mock_fetch.side_effect = [
        [  # firewalls
            {
                "relationships": {
                    "device": {"data": {"deviceName": "FW1", "deviceType": "firewall"}}
                },
                "attributes": {"stats": [{"data": [[1, 100, 200, 300]]}]},
                "id": "fw1",
            }
        ],
        [],  # routers
        [],  # switches
        [],  # stack
        [],  # aps
    ]
    mock_bandwidth.return_value = (1.0, 2.0, 3.0)
    mock_max_iface.return_value = ("eth0", 50)

    result = bandwidth_report("tenant1")
    assert len(result) == 1
    entry = result[0]
    assert entry["Device"] == "FW1"
    assert entry["Type"] == "Firewall"
    assert entry["TX"] == 1.0
    assert entry["RX"] == 2.0
    assert entry["Total"] == 3.0
    assert entry["Top Interface"] == "eth0"
    assert entry["Average Utilization"] == 50


@patch("auvik_report.production.reports.max_interface_average")
@patch("auvik_report.production.reports.bandwidth_average")
@patch("auvik_report.production.reports.fetch_device_stats")
def test_bandwidth_report_skips_devices_with_no_stats(
    mock_fetch, mock_bandwidth, mock_max_iface
):
    mock_fetch.side_effect = [
        [
            {
                "relationships": {
                    "device": {"data": {"deviceName": "SW1", "deviceType": "switch"}}
                },
                "attributes": {"stats": [{"data": []}]},  # empty data
                "id": "sw1",
            }
        ],
        [],
        [],
        [],
        [],
    ]
    mock_bandwidth.return_value = (10, 20, 30)
    mock_max_iface.return_value = ("eth1", 70)

    result = bandwidth_report("tenant1")
    assert result == []


############################
# Tests for device_health
############################
@patch("auvik_report.production.reports.health_scores")
@patch("auvik_report.production.reports.stats_per_device")
@patch("auvik_report.production.reports.fetch_device_stats")
def test_device_health_calls_dependencies(mock_fetch, mock_stats, mock_health):
    mock_fetch.side_effect = [
        [
            {
                "relationships": {
                    "device": {"data": {"id": "dev1", "deviceName": "Router1"}}
                },
                "attributes": {"stats": [{"data": [[1, 10], [2, 20]]}]},
            }
        ],  # cpu
        [],  # memory
        [],  # storage
    ]

    mock_stats.return_value = {"dev1": {"cpu": 10, "memory": 20, "storage": 30}}
    mock_health.return_value = [{"name": "Router1", "health": 50}]

    result = device_health("tenant1")
    assert result == [{"name": "Router1", "health": 50}]
    mock_stats.assert_called_once()
    mock_health.assert_called_once()
