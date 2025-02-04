import uvicorn

if __name__ == "__main__":
    uvicorn.run("SampleProject.asgi:application", host="0.0.0.0", port=8000)