#!/usr/bin/env python3
"""
Web API interface for mySql API tool
"""
import asyncio
import os
import sys
sys.path.append(os.getcwd())

from datetime import datetime, timedelta

from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette_exporter import PrometheusMiddleware, handle_metrics
import json
import logging
import uvicorn
from typing import Union
from scripts.acc import *

from typing import Optional
from fastapi_utils.tasks import repeat_every

import acc

user = 'adi'
logging.debug('Using username %s', user)

app = FastAPI(debug=True)
app.add_middleware(PrometheusMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_route("/metrics", handle_metrics)

logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup():
    logging.debug('startup_event')


@app.on_event("shutdown")
def shutdown_event():
    logging.debug('shutdown_event')


@app.get("/")
def read_root():
    return {"acc_api": "v0.1"}

@app.get("/healthz")
def read_root():
    return "OK"


@app.get("/ver")
def get_versions():
    ver = "v0.1"
    return {"acc version": str(ver)}

########################          ACC API         ##################################

@app.get("/acc/getaccounts")
def get_accounts():
    response =  acc_get_accounts()
    return JSONResponse(status_code=200, content=response)

@app.get("/acc/getuser/{user_id}")
def get_user_details(user_id):
    response = acc_get_user_details(user_id)
    return JSONResponse(status_code=200, content=response)

@app.get("/acc/gethepek/{hepek_id}")
def get_hepek_details(hepek_id):
    response = acc_get_hepek_details(hepek_id)
    return JSONResponse(status_code=200, content=response)

@app.get("/acc/getinfo/{info_id}")
def get_hepek_details(info_id):
    response = acc_get_info_details(info_id)
    return JSONResponse(status_code=200, content=response)

@app.post("/acc/api")
async def request_post(info : Request):
    req_info = await info.json()
    response = acc_update_meter_details(req_info)
    return JSONResponse(status_code=200, content=response)


@app.post("/acc/setcontracts")
async def request_post(info : Request):
    req_info = await info.json()
    response = acc_update_contract_addresses(req_info)
    return JSONResponse(status_code=200, content=response)

serverport = int(os.getenv('ACC_API_PORT', 9002))

if __name__ == "__main__":
    logging.info('Starting ACC API Client')
    uvicorn.run(app, host="0.0.0.0", port=serverport, log_level=10)
