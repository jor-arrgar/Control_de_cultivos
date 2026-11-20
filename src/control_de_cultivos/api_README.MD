# Backend FastAPI service API

Dedicated to act as an intermediary between Streamlit GUI and Azure Proxi services (function apps that manage Azure resources connections and requests). Can be deployed in the same machine as threaded parallel process or in any separated cloud machine.

## Usage

### Check health

```bash
curl "http://127.0.0.1:8001/health" ; echo # End with newline
```

### Get user explotations

```bash
curl "http://127.0.0.1:8001/proxy/user_data/explotations?user=test&userKey=secret123&check=0" ; printf '\n'
```

```bash
curl -X POST "http://127.0.0.1:8001/proxy/user_data/explotations" \
  -H "Content-Type: application/json" \
  -d '{"user":"test","userKey":"secret123","check":0}' ; echo
```

### Get explotation data

```bash
curl "http://127.0.0.1:8001/proxy/user_data/explotation?user=test&userKey=secret123&check=0&explotation=test_exploitation.json" ; echo
```

```bash
curl -X POST "http://127.0.0.1:8001/proxy/user_data/explotation" \
  -H "Content-Type: application/json" \
  -d '{"user":"test","userKey":"secret123","check":0,"explotation":"test_exploitation.json"}' ; echo
```

### Get user info (db)

```bash
curl "http://127.0.0.1:8001/proxy/user_data/user_info?user=juan@example.com" ; echo
```

### New user

```bash
curl -X POST "http://127.0.0.1:8001/proxy/user_data/insert_new_user" \
  -H "Content-Type: application/json" \
  -d '{"check":0, "user_data":{"code":"juan4@example.com","email":"juan4@example.com","name":"pipo4","province":"Valladolid","nExplotations":7}}' ; echo
```


### Get database table info

```bash
curl "http://127.0.0.1:8001/proxy/generaldb/get_table_struct?table_name=01_users" ; echo
```

### Get unique values for a given table and column

```bash
curl "http://127.0.0.1:8001/proxy/generaldb/get_column_uniques?table_name=01_users&column_name=code" ; echo
```
