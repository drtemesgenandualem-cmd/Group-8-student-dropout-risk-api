# Invalid-input log

Recorded: 2026-11-04T15:26:05.616185+03:00 (Africa/Addis_Ababa). Actual requests to `http://127.0.0.1:8000/predict`.

| Test | Change to valid request | HTTP status | Actual message |
|---|---|---|---|
| missing_field | Remove `Age at enrollment` | 422 | Field required |
| wrong_type | `Age at enrollment`: `"young"` | 422 | Input should be a valid integer |
| out_of_range | `Age at enrollment`: `900` | 422 | Input should be less than or equal to 70 |
| invalid_category | `Course`: `999` | 422 | Input should be 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16 or 17 |

Full request bodies and responses: [invalid_input_log.json](invalid_input_log.json).
Each request starts with [valid_student.json](../examples/valid_student.json) and applies the change shown above.
