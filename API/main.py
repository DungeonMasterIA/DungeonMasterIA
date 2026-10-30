from fastapi import FastAPI

from app.routers import auth, users

app = FastAPI()

app.include_router(auth.router)
app.include_router(users.router)

@app.get("/")
def leer_raiz():
    return {"mensaje": "¡Hola, mundo!"}