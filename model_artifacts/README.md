# Saved model reference

`dropout_risk_model.joblib` is an unchanged copy of the existing Module 5 artifact `../../Models/dropout_risk_model.joblib`. `model_metadata.json` is copied from the same original Models directory. It keeps the original filename, which is the file `app/main.py` loads. No training was performed for this API.

SHA-256 of both the API copy and original model:

```text
62fc0555b1b5d01861725cec644577d5ae095392894a609eac431fb2f0efcf64
```

The saved object is the complete fitted preprocessing and Logistic Regression pipeline. The API uses its original feature order, class order and 0.38 threshold, recorded in the accompanying metadata. Model/API release version: `1.0.0`.

To update artifacts after deliberate retraining, export the entire fitted pipeline with `joblib.dump(pipeline, "model_artifacts/dropout_risk_model.joblib")`, update metadata and the typed schema together, assign a new release version, then repeat the tests and evidence capture. The current artifact needs no re-export.
