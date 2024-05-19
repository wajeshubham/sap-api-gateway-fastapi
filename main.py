from fastapi import FastAPI, Request, Response
import httpx

import aiosmtplib
import ssl

import asyncio

SMTP_SERVER = "smtp.gmail.com"
PORT = 587
EMAIL = "<email>"
PASSWORD = "<password>"

context = ssl.create_default_context()

app = FastAPI()
redis = None

# SAP system endpoint and request threshold
SAP_API_URL = "https://api.freeapi.app/api/v1/public"
REQUEST_THRESHOLD = {
    "warning": 5,
    "critical": 10
}

total_requests = {} # ! store this data in db
requests_count = 0 # ! store this data in db

@app.middleware("http")
async def api_gateway_middleware(request: Request, call_next):
    global requests_count
    
    path = request.url.path
    client_ip = request.client.host
    
    print(f"Client IP: {client_ip}")
    print(f"Request URL: {path}")

    # Increment request counters
    total_requests[client_ip] = total_requests.get(client_ip, 0) + 1
    requests_count += 1
    print(f"Total requests: {requests_count}")
    print(f"Total requests for {client_ip}: {total_requests[client_ip]}")

    # Check if the threshold is reached
    if requests_count == REQUEST_THRESHOLD["warning"]:
        # Send threshold email asynchronously without blocking the request
        asyncio.create_task(send_threshold_email(requests_count, "warning"))
    
    # Check if the threshold is reached
    if requests_count == REQUEST_THRESHOLD["critical"]:
        # Send threshold email asynchronously without blocking the request
        asyncio.create_task(send_threshold_email(requests_count, "critical"))

    # Forward the request to the SAP system
    async with httpx.AsyncClient() as client:
        sap_response = await client.request(
            method=request.method,
            url=f"{SAP_API_URL}{path}",
            headers=request.headers,
            params=request.query_params,
            data=await request.body()
        )
    
    # Create response for the original client
    response = Response(
        content=sap_response.content,
        status_code=sap_response.status_code,
        headers=dict(sap_response.headers)
    )

    return response

async def send_threshold_email(request_count, severity):
    print(f"Sending threshold email for {request_count} requests")
        
    message = f"""\
Subject: Request Threshold Reached

Hello admin,

We have reached the request threshold of {request_count} requests which is {severity.upper()} severity. Please review the system and make necessary changes.
    """
    try:
        await aiosmtplib.send(
            message,
            hostname=SMTP_SERVER,
            port=PORT,
            start_tls=True,
            username=EMAIL,
            password=PASSWORD,
            recipients=["<recipient>"],
            sender=EMAIL,
        )
        print("Threshold email sent successfully.")
    except Exception as e:
        print(f"Failed to send threshold email: {e}")

