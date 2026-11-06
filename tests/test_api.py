"""API contract, validation, original-pipeline parity, and failure behavior."""
import json
from unittest.mock import Mock

import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.main import app, MODEL_PATH
from app.schemas import API_DIR, METADATA, MODEL_VERSION

GOOD = json.loads((API_DIR / "examples/valid_student.json").read_text())


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "model_version": MODEL_VERSION}


def test_valid_prediction_matches_saved_pipeline(client):
    response = client.post("/predict", json=GOOD)
    assert response.status_code == 200
    body = response.json()
    frame = pd.DataFrame([GOOD], columns=METADATA["feature_order"])
    raw = app.state.model.predict_proba(frame)[0]
    expected = dict(zip(app.state.model.classes_, raw))
    assert body["probability"] == round(expected["Dropout"], 4)
    assert body["probabilities"] == {key: round(value, 4) for key, value in expected.items()}
    assert all(0 <= value <= 1 for value in body["probabilities"].values())
    assert sum(body["probabilities"].values()) == pytest.approx(1, abs=0.0002)
    flagged = expected["Dropout"] >= 0.38
    outcome = "Dropout" if flagged else max(["Enrolled", "Graduate"], key=expected.__getitem__)
    assert body["predicted_outcome"] == outcome
    assert body["risk_label"] == ("high_risk" if flagged else "low_risk")
    assert body["threshold"] == 0.38
    assert body["model_version"] == MODEL_VERSION


@pytest.mark.parametrize("case", ["missing", "wrong_type", "out_of_range", "invalid_category", "extra", "null", "boolean", "string_code"])
def test_invalid_input_is_rejected_before_inference(client, monkeypatch, case):
    payload = dict(GOOD)
    if case == "missing":
        del payload["Age at enrollment"]
    elif case == "wrong_type":
        payload["Age at enrollment"] = "young"
    elif case == "out_of_range":
        payload["Age at enrollment"] = 900
    elif case == "invalid_category":
        payload["Course"] = 999
    elif case == "extra":
        payload["Target"] = "Dropout"
    elif case == "null":
        payload["GDP"] = None
    elif case == "boolean":
        payload["Debtor"] = True
    else:
        payload["Course"] = "1"
    model = Mock()
    monkeypatch.setitem(app.state._state, "model", model)
    response = client.post("/predict", json=payload)
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"][0] == "body"
    model.predict_proba.assert_not_called()


@pytest.mark.parametrize("feature", METADATA["feature_order"])
def test_every_field_is_required(client, feature):
    payload = dict(GOOD)
    del payload[feature]
    response = client.post("/predict", json=payload)
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", feature]


@pytest.mark.parametrize("feature,limits", METADATA["numeric_ranges"].items())
def test_numeric_limits(client, feature, limits):
    for bound in limits:
        value = bound if isinstance(GOOD[feature], float) else int(bound)
        assert client.post("/predict", json={**GOOD, feature: value}).status_code == 200
    for value in [limits[0] - 1, limits[1] + 1]:
        if isinstance(GOOD[feature], int):
            value = int(value)
        assert client.post("/predict", json={**GOOD, feature: value}).status_code == 422


@pytest.mark.parametrize("feature", METADATA["allowed_values"])
def test_each_category_rejects_unknown_code(client, feature):
    assert client.post("/predict", json={**GOOD, feature: 9999}).status_code == 422


@pytest.mark.parametrize("dropout,enrolled,graduate,outcome", [
    (0.37999, 0.2, 0.42001, "Graduate"),
    (0.38, 0.4, 0.22, "Dropout"),
    (0.2, 0.5, 0.3, "Enrolled"),
])
def test_threshold_and_non_dropout_decision(client, monkeypatch, dropout, enrolled, graduate, outcome):
    model = Mock(classes_=np.array(METADATA["classes"]))
    model.predict_proba.return_value = np.array([[dropout, enrolled, graduate]])
    monkeypatch.setitem(app.state._state, "model", model)
    body = client.post("/predict", json=GOOD).json()
    assert body["predicted_outcome"] == outcome
    assert body["risk_label"] == ("high_risk" if outcome == "Dropout" else "low_risk")
    frame = model.predict_proba.call_args.args[0]
    assert list(frame.columns) == METADATA["feature_order"]


def test_internal_error_returns_safe_message(client, monkeypatch):
    model = Mock(classes_=np.array(METADATA["classes"]))
    model.predict_proba.side_effect = RuntimeError("private model path /secret/model.joblib")
    monkeypatch.setitem(app.state._state, "model", model)
    response = client.post("/predict", json=GOOD)
    assert response.status_code == 500
    assert response.json() == {"detail": "Prediction failed"}
    assert "secret" not in response.text


@pytest.mark.parametrize("proba", [[[float("nan"), 0.4, 0.6]], [[0.4, 0.4, 0.4]], [[-0.1, 0.5, 0.6]], [[0.5, 0.5]]])
def test_invalid_model_output_returns_safe_error(client, monkeypatch, proba):
    model = Mock(classes_=np.array(METADATA["classes"]))
    model.predict_proba.return_value = proba
    monkeypatch.setitem(app.state._state, "model", model)
    response = client.post("/predict", json=GOOD)
    assert response.status_code == 500
    assert response.json() == {"detail": "Prediction failed"}


def test_model_is_loaded_once_per_startup(monkeypatch):
    import app.main as main
    real_load = main.joblib.load
    loader = Mock(wraps=real_load)
    monkeypatch.setattr(main.joblib, "load", loader)
    with TestClient(app) as client:
        for _ in range(3):
            assert client.post("/predict", json=GOOD).status_code == 200
    loader.assert_called_once_with(MODEL_PATH)


def test_openapi_documents_all_inputs(client):
    schema = client.get("/openapi.json").json()["components"]["schemas"]["PredictionInput"]
    assert set(schema["required"]) == set(METADATA["feature_order"])
    assert schema["additionalProperties"] is False
    assert all(field["description"] for field in schema["properties"].values())
    assert client.get("/docs").status_code == 200
