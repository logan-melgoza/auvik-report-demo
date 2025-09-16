import pytest
from unittest.mock import patch

from auvik_report.production.helpers import (
    score_calculator,
    health_scores,
    bandwidth_average,
    max_interface_average,
    stats_per_device,
)

############################
# Tests for score_calculator
############################
def test_score_calculator_normal_values():
    stats = {"cpu": 20, "memory": 30, "storage": 40}
    result = score_calculator(stats)
    expected = 100 - (0.35 * 20 + 0.4 * 30 + 0.25 * 40)
    assert result == expected

def test_score_calculator_missing_values():
    stats = {"cpu": None, "memory": None, "storage": None}
    result = score_calculator(stats)
    assert result is None

def test_score_calculator_partial_missing_values():
    stats = {"cpu": None, "memory": 50, "storage": None}
    result = score_calculator(stats)
    expected = 100 - (0.35 * 0 + 0.4 * 50 + 0.25 * 0)
    assert result == expected

############################
# Tests for health_scores
############################
def test_health_scores_includes_low_scores():
    stats = {
        "dev1": {"name": "Router1", "cpu": 90, "memory": 90, "storage": 90}
    }
    result = health_scores(stats)
    assert isinstance(result, list)
    assert result[0]["name"] == "Router1"
    assert "health" in result[0]

def test_health_scores_excludes_high_scores():
    stats = {
        "dev1": {"name": "Router1", "cpu": 1, "memory": 1, "storage": 1}
    }
    result = health_scores(stats)
    assert result == []

############################
# Tests for bandwidth_average
############################
def test_bandwidth_average_with_data():
    device = {
        "attributes": {
            "stats": [
                {
                    "data": [
                        [1, 1000000, 2000000, 3000000],
                        [2, 2000000, 3000000, 5000000],
                    ]
                }
            ]
        }
    }
    tx_avg, rx_avg, total_avg = bandwidth_average(device)
    assert tx_avg == pytest.approx(1.5, rel=1e-3)
    assert rx_avg == pytest.approx(2.5, rel=1e-3)
    assert total_avg == pytest.approx(4.0, rel=1e-3)

def test_bandwidth_average_no_data():
    device = {"attributes": {"stats": [{"data": []}]}}
    tx_avg, rx_avg, total_avg = bandwidth_average(device)
    assert tx_avg == rx_avg == total_avg == 0

############################
# Tests for max_interface_average
############################
@patch("auvik_report.production.helpers.fetch_interface_stats")
def test_max_interface_average_returns_highest(mock_fetch):
    mock_fetch.return_value = [
        {
            "id": "int1",
            "attributes": {"stats": [{"data": [[1, 50], [2, 70]]}]},
            "relationships": {"interface": {"data": {"interfaceName": "eth0"}}},
        },
        {
            "id": "int2",
            "attributes": {"stats": [{"data": [[1, 20], [2, 30]]}]},
            "relationships": {"interface": {"data": {"interfaceName": "eth1"}}},
        },
    ]
    device = {"id": "dev1"}
    name, avg = max_interface_average(device)
    assert name == "eth0"
    assert avg == 60

@patch("auvik_report.production.helpers.fetch_interface_stats")
def test_max_interface_average_handles_empty_data(mock_fetch):
    mock_fetch.return_value = [
        {
            "id": "int1",
            "attributes": {"stats": [{"data": []}]},
            "relationships": {"interface": {"data": {"interfaceName": "eth0"}}},
        }
    ]
    device = {"id": "dev1"}
    name, avg = max_interface_average(device)
    assert name == "NA"
    assert avg == 0

############################
# Tests for stats_per_device
############################
def test_stats_per_device_aggregates_correctly():
    cpu = [
        {
            "relationships": {
                "device": {"data": {"id": "dev1", "deviceName": "Router1"}}
            },
            "attributes": {"stats": [{"data": [[1, 10], [2, 20]]}]},
        }
    ]
    memory = [
        {
            "relationships": {
                "device": {"data": {"id": "dev1", "deviceName": "Router1"}}
            },
            "attributes": {"stats": [{"data": [[1, 30], [2, 50]]}]},
        }
    ]
    storage = [
        {
            "relationships": {
                "device": {"data": {"id": "dev1", "deviceName": "Router1"}}
            },
            "attributes": {"stats": [{"data": [[1, 40], [2, 60]]}]},
        }
    ]
    result = stats_per_device(cpu, memory, storage)
    dev = result["dev1"]
    assert dev["id"] == "dev1"
    assert dev["name"] == "Router1"
    assert dev["cpu"] == 15.0
    assert dev["memory"] == 40.0
    assert dev["storage"] == 50.0

def test_stats_per_device_handles_empty_stats():
    cpu = [
        {
            "relationships": {
                "device": {"data": {"id": "dev1", "deviceName": "Router1"}}
            },
            "attributes": {"stats": [{"data": []}]},
        }
    ]
    memory, storage = [], []
    result = stats_per_device(cpu, memory, storage)
    dev = result["dev1"]
    assert dev["cpu"] is None
    assert dev["memory"] is None
    assert dev["storage"] is None
