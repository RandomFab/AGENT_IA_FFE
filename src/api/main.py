from fastapi import FastAPI

api = FastAPI()

@api.get('/')
def root():
    return  {"message":"Hello FFE"}

@api.get('/health')
def health():
    return {"message":"Api is healthy"}