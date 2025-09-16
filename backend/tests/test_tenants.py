import json
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from auvik_report.tenants import populate_tenants, DATA_DIR, TENANTS_DIR

############################
# Tests for populate_tenants
############################
@patch("auvik_report.tenants.fetch_tenants")
def test_populate_tenants_creates_files_with_expected_content(mock_fetch, tmp_path, monkeypatch):
    # Arrange
    mock_fetch.return_value = [
        {
            "id": "t1",
            "attributes": {"domainPrefix": "dom1", "displayName": "Tenant One"},
        },
        {
            "id": "t2",
            "attributes": {"domainPrefix": "dom2", "displayName": "Tenant Two"},
        },
    ]
    monkeypatch.setattr("auvik_report.tenants.DATA_DIR", tmp_path / "data")
    monkeypatch.setattr("auvik_report.tenants.TENANTS_DIR", tmp_path / "data" / "tenants")

    # Act
    populate_tenants()

    # Assert
    domain_id_file = tmp_path / "data" / "tenants" / "domain_id.json"
    domain_name_file = tmp_path / "data" / "tenants" / "domain_name.json"
    assert domain_id_file.exists()
    assert domain_name_file.exists()

    with open(domain_id_file) as f:
        content = json.load(f)
    assert content == {"data": {"dom1": "t1", "dom2": "t2"}}

    with open(domain_name_file) as f:
        content = json.load(f)
    assert content == {"data": {"dom1": "Tenant One", "dom2": "Tenant Two"}}


@patch("auvik_report.tenants.fetch_tenants", return_value=[])
def test_populate_tenants_handles_empty_list(mock_fetch, tmp_path, monkeypatch):
    # Arrange
    monkeypatch.setattr("auvik_report.tenants.DATA_DIR", tmp_path / "data")
    monkeypatch.setattr("auvik_report.tenants.TENANTS_DIR", tmp_path / "data" / "tenants")

    # Act
    populate_tenants()

    # Assert
    domain_id_file = tmp_path / "data" / "tenants" / "domain_id.json"
    domain_name_file = tmp_path / "data" / "tenants" / "domain_name.json"
    assert domain_id_file.exists()
    assert domain_name_file.exists()

    with open(domain_id_file) as f:
        content = json.load(f)
    assert content == {"data": {}}

    with open(domain_name_file) as f:
        content = json.load(f)
    assert content == {"data": {}}
