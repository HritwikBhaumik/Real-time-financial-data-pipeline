# Finnhub Real‑Time Market Data Pipeline

A ready‑to‑run, Dockerized pipeline that ingests live trades from Finnhub WebSocket, stores ticks in Postgres, serves an HTTP API (FastAPI), and visualizes prices via Streamlit.

## Run It

```bash
cp .env.example .env
# Edit the token & symbols
vim .env

# Launch
docker compose up --build
```

- API: http://localhost:8000/docs
- Dashboard: http://localhost:8501

## Environment
See `.env.example` for all knobs. Minimal required is `FINNHUB_TOKEN`.

## Notes
- Free Finnhub plans may throttle updates; that’s fine for demo.
- The ingestor batches DB commits (~0.5s) for throughput.
- Candles are computed on query time; for high volume you can add a background job to persist minute bars.

## Dev
```bash
make up
make logs
make down
```

## Testing
```bash
docker compose run --rm api pytest -q
```

## License
MIT
