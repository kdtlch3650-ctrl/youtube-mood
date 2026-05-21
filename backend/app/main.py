from fastapi import FastAPI

app = FastAPI(title="YouTube Mood Recommendation API")


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
