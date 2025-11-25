
```sh
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

```sh
curl -X POST http://localhost:8080/v1/ingest \
     -H "Authorization: Bearer mock-token"

```