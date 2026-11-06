# Sub-module 6.2 submission checklist

Project: Group 8 — Early Prediction of Student Academic Outcomes.

| # | Expected submission | Included evidence |
|---|---|---|
| 1 | API source, requirements and saved model reference | [main.py](app/main.py), [schemas.py](app/schemas.py), [requirements.txt](requirements.txt), [model provenance](model_artifacts/README.md), and the actual saved model |
| 2 | Screenshots of `/docs` and a successful prediction | [docs.png](evidence/docs.png), [successful_prediction.png](evidence/successful_prediction.png), [full expanded operation](evidence/docs_prediction_full.png), [actual response JSON](evidence/successful_prediction.json) |
| 3 | Invalid-input log with requests, status codes and messages | [Readable log](evidence/invalid_input_log.md) and [full JSON requests/responses](evidence/invalid_input_log.json); four actual requests, all HTTP 422 |
| 4 | Passing automated test results | [76 passing tests](evidence/test_results.txt), [test source](tests/test_api.py) |
| 5 | Input table, response table and limits statement | [API reference](API_REFERENCE.md) |
| 6 | Error behavior note | [API reference — Error behavior](API_REFERENCE.md#error-behavior), plus automated rejection and safe-500 tests |
| 7 | Container build and run (Dockerfile), with a short explanation of why the container helps | [Short explanation](README.md#why-use-a-container), [Dockerfile](Dockerfile), [requirements-docker.txt](requirements-docker.txt), [build and run](evidence/docker_build_and_run.png), [successful prediction in the container](evidence/docker_successful_prediction.png), container logs [1](evidence/docker_container_logs_1.png) and [2](evidence/docker_container_logs_2.png) |

The [README](README.md) follows Steps 1–5 in order and includes installation, service startup, Swagger usage, curl commands, evidence capture, tests and troubleshooting.

Verification distinguishes actual live HTTP evidence from injected model-error tests: the invalid-input log and successful prediction come from the running Uvicorn server; internal-error scenarios use controlled model substitutes in automated tests. No real training artifact was damaged to demonstrate failures.
