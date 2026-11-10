## Backend FastAPI service API

Dedicated to act as an intermediary between Streamlit GUI and Azure Proxi services (function apps that manage Azure resources connections and requests). Can be deployed in the same machine as threaded parallel process or in any separated cloud machine.

### Usage

**Get user explotations**

```bash
curl "http://127.0.0.1:8001/proxy/user_data/explotations?user=test&userKey=secret123&check=0"
```

```bash
curl -X POST "http://127.0.0.1:8001/proxy/user_data/explotations" \
  -H "Content-Type: application/json" \
  -d '{"user":"test","userKey":"secret123","check":0}'
```

**Get explotation data**

```bash
curl "http://127.0.0.1:8001/proxy/user_data/explotation?user=test&userKey=secret123&check=0&explotation=test_exploitation.json"
```

```bash
curl -X POST "http://127.0.0.1:8001/proxy/user_data/explotation" \
  -H "Content-Type: application/json" \
  -d '{"user":"test","userKey":"secret123","check":0,"explotation":"test_exploitation.json"}'
```
