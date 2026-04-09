# COSC310 Term Project Group 21

Deployed Site: [https://platter.quietrecords.store](https://platter.quietrecords.store)

## Run with Docker Compose

### Start (keeps existing data)
```bash
docker compose up --build -d
```


### Clean Start (wipes existing data)
```bash
docker compose down -v && docker compose up --build -d
```


### Stop
```bash
docker compose down
```

Backend API available at [http://localhost:8000](http://localhost:8000) — Swagger docs at [http://localhost:8000/docs](http://localhost:8000/docs)

Frontend available at [http://localhost:3000](http://localhost:3000)

Note: New User registration will not complete if the .env email settings have not been setup, the rest of the system functionality and existing users are unaffected.
