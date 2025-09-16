import json
import pytest
import importlib
from unittest.mock import patch, MagicMock

# Import the module, not the function
gr = importlib.import_module("auvik_report.generate_report")


############################
# Tests for gather_data
############################
@patch.object(gr, "get_cache")
@patch.object(gr, "set_cache")
@patch.object(gr, "device_health")
@patch.object(gr, "bandwidth_report")
@patch.object(gr, "open_alerts")
@patch.object(gr, "uptime_report")
def test_gather_data_fetches_when_no_cache(
    mock_uptime, mock_alerts, mock_bandwidth, mock_health, mock_set, mock_get
):
    mock_get.return_value = None
    mock_uptime.return_value = {"Router": 99.9}
    mock_alerts.return_value = {"Critical": 1}
    mock_bandwidth.return_value = [{"Device": "SW1"}]
    mock_health.return_value = [{"name": "Router1"}]

    result = gr.gather_data("tid1", "Tenant1")
    assert "uptime" in result
    assert "alerts" in result
    assert "bandwidth" in result
    assert "health" in result
    mock_set.assert_called_once()


@patch.object(gr, "get_cache")
def test_gather_data_returns_cached(mock_get):
    mock_get.return_value = {"uptime": {"Router": 99.9}}
    result = gr.gather_data("tid1", "Tenant1")
    assert result == {"uptime": {"Router": 99.9}}


############################
# Tests for gather_tenants
############################
@patch.object(gr, "populate_tenants")
def test_gather_tenants_reads_files(mock_populate, tmp_path, monkeypatch):
    data_dir = tmp_path / "data" / "tenants"
    data_dir.mkdir(parents=True)
    (data_dir / "domain_id.json").write_text(json.dumps({"data": {"dom1": "tid1"}}))
    (data_dir / "domain_name.json").write_text(
        json.dumps({"data": {"dom1": "Tenant1"}})
    )

    monkeypatch.chdir(tmp_path)
    domain_id, domain_name = gr.gather_tenants()
    assert domain_id == {"dom1": "tid1"}
    assert domain_name == {"dom1": "Tenant1"}
    mock_populate.assert_not_called()


@patch.object(gr, "populate_tenants")
def test_gather_tenants_populates_if_files_missing(mock_populate, tmp_path, monkeypatch):
    tenants_dir = tmp_path / "data" / "tenants"
    tenants_dir.mkdir(parents=True)
    (tenants_dir / "domain_id.json").write_text(json.dumps({"data": {}}))
    (tenants_dir / "domain_name.json").write_text(json.dumps({"data": {}}))

    monkeypatch.chdir(tmp_path)
    domain_id, domain_name = gr.gather_tenants()
    assert isinstance(domain_id, dict)
    assert isinstance(domain_name, dict)


############################
# Tests for generate_report
############################
@patch.object(gr, "pdfkit")
@patch.object(gr, "gather_data")
@patch.object(gr, "gather_tenants")
@patch.object(gr, "input")
def test_generate_report_happy_path(
    mock_input, mock_gather_tenants, mock_gather_data, mock_pdfkit, tmp_path, monkeypatch
):
    mock_gather_tenants.return_value = ({"dom1": "tid1"}, {"dom1": "Tenant1"})
    mock_input.side_effect = ["dom1"]
    mock_gather_data.return_value = {
        "uptime": {"Router": 99.9},
        "alerts": {"Critical": 1},
        "bandwidth": [],
        "health": [],
    }

    template_mock = MagicMock()
    template_mock.render.return_value = "<html>Report</html>"
    env_mock = MagicMock()
    env_mock.get_template.return_value = template_mock
    monkeypatch.setattr(gr, "Environment", lambda *a, **k: env_mock)

    monkeypatch.setattr(gr, "OUTPUT_DIR", tmp_path / "output")
    monkeypatch.setattr(gr, "HTML_OUT", tmp_path / "output" / "report.html")
    monkeypatch.setattr(gr, "PDF_OUT", tmp_path / "output" / "report.pdf")
    monkeypatch.setattr(gr.Path, "exists", lambda self: True)

    gr.generate_report()

    assert (tmp_path / "output" / "report.html").exists()
    template_mock.render.assert_called_once()
    mock_pdfkit.from_file.assert_called_once()


@patch.object(gr, "gather_tenants")
@patch.object(gr, "input")
def test_generate_report_invalid_domain_triggers_repopulate(
    mock_input, mock_gather_tenants, tmp_path, monkeypatch
):
    mock_gather_tenants.return_value = ({"dom1": "tid1"}, {"dom1": "Tenant1"})
    mock_input.side_effect = ["wrongdom", "dom1"]

    template_mock = MagicMock()
    template_mock.render.return_value = "<html>Report</html>"
    env_mock = MagicMock()
    env_mock.get_template.return_value = template_mock
    monkeypatch.setattr(gr, "Environment", lambda *a, **k: env_mock)

    monkeypatch.setattr(gr, "gather_data", lambda *a, **k: {
        "uptime": {},
        "alerts": {},
        "bandwidth": [],
        "health": [],
    })
    monkeypatch.setattr(gr, "populate_tenants", lambda: None)
    monkeypatch.setattr(gr, "OUTPUT_DIR", tmp_path / "output")
    monkeypatch.setattr(gr, "HTML_OUT", tmp_path / "output" / "report.html")
    monkeypatch.setattr(gr, "PDF_OUT", tmp_path / "output" / "report.pdf")
    monkeypatch.setattr(gr.Path, "exists", lambda self: True)
    monkeypatch.setattr(gr, "pdfkit", MagicMock())

    gr.generate_report()

    assert (tmp_path / "output" / "report.html").exists()
