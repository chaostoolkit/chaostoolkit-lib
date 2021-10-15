import time

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    time.sleep(5)
    return "Hello world"
