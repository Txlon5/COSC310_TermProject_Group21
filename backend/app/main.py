from fastapi import FastAPI

app = FastAPI()
@app.get("/")
def hello():
    return {"msg": "Hello World"}
@app.get("/items/{name}")
def get_item(name: str):
    return {"item": name, "status": "ok"}