from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
     return {"message": "CRM API funcionando", "versión": "1.0.0"}

@app.get("/healt")
def healt_check():
     return {"status": "healthy"}

