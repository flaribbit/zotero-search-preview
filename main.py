from fastapi import FastAPI
import uvicorn
import httpx

app = FastAPI()
client = httpx.Client(base_url="http://127.0.0.1:23119/api/users/0")


@app.get("/")
async def root():
    return {"message": "Welcome to Zotero Search Preview API"}


@app.get("/search")
async def search():
    pass


if __name__ == "__main__":
    res = client.get("collections/PE3MSZKI/items")
    print(res.json())
    # uvicorn.run(app, host="0.0.0.0", port=8000)
