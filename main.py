import fastapi
from fastapi import status, Body
from fastapi.responses import JSONResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
from sqs import SQS_Client
import time

app = fastapi.FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

sqs_client = SQS_Client()

LAST_USED = [0]

@app.get('/')
async def redirect_to_app():
    return RedirectResponse("/app")

@app.get('/app')
async def get_app():
    return FileResponse("static/index.html")


@app.post("/api/create")
async def create_campaign(
    subject: str = Body(...),
    body: str = Body(...),
    recv_addrs: list[str] = Body(...),
):
    
    if len(recv_addrs) > 10:
        return JSONResponse(content = {"error": "cannot send more than 10 emails."}, status_code = status.HTTP_400_BAD_REQUEST)

    # Check if more than 10 seconds have passed since last request
    if time.time().__ceil__() - LAST_USED[0] < 10:
        return JSONResponse(content = {"error": "too many requests"}, status_code = status.HTTP_429_TOO_MANY_REQUESTS)
    LAST_USED[0] = time.time().__ceil__()
    
    for addr in recv_addrs:
        messageAttributes = {
            "recv_addr": {'StringValue': addr, 'DataType': 'String'},
            "mail_subject": {'StringValue': subject, 'DataType': 'String'},
            "mail_body": {'StringValue': body, 'DataType': 'String'}
        }
        sqs_client.publish(messageAttributes)
    

    return JSONResponse(
        content = {"deployed": len(recv_addrs), "time": LAST_USED},
        status_code = status.HTTP_200_OK
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)