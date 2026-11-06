# Evidence of API operation

## Screenshots

I manually tested the API through the Swagger UI at `http://localhost:8000/docs` and took the screenshots included in this folder.

- `docs.png`: the API overview showing the available endpoints.
- `successful_prediction.png`: a successful POST `/predict` request showing HTTP 200 and the prediction response.
- `docs_prediction_full.png`: the expanded prediction operation and response.

## Docker screenshots

- `docker_build_and_run.png`: terminal output of `docker build -t dropout-api:1.0 .`, `docker run -d --name dropout-api -p 8000:8000 dropout-api:1.0` and `docker ps`, showing the container starting with port 8000 published.
- `docker_successful_prediction.png`: terminal output after rebuilding and running the container with the current API code. `curl` posts `examples/valid_student.json` to `http://localhost:8000/predict` inside Docker and receives the same result as the local run: Dropout probability 0.4128, `risk_label` `high_risk`, `predicted_outcome` `Dropout`, threshold 0.38 (the line is cut off at the right edge of the terminal).
- `docker_container_logs_1.png` and `docker_container_logs_2.png`: Docker Desktop log view of the running `dropout-api` container. They show the health check calling `GET /health` (200 OK) and `POST /predict` requests returning 422 Unprocessable Content for invalid input. The first is from an earlier container (running 4 minutes); the second is from the container started in the terminal screenshot (running 3 hours).

## Request logs and test results

- `health_response.json`, `successful_prediction.json` and `openapi.json`: responses saved from the running API by `scripts/record_requests.py`.
- `invalid_input_log.json` and `invalid_input_log.md`: four deliberately invalid requests with their actual HTTP 422 responses and validation messages.
- `test_results.txt`: automated test output showing 76 passing tests and one upstream TestClient deprecation warning.

Internal prediction failures are checked separately in automated tests using a controlled failing model substitute. These tests verify that the API returns a safe HTTP 500 message without exposing private details.
