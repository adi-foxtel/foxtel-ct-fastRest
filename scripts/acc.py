#!/usr/bin/env python
import os
import json

CarbonContractAddress   = None
ErgonContractAddress    = None
TodoListContractAddress = None

meter = None
entry = None

def acc_update_meter_details(payload) :

    entry = 0

    meters = json.load(open('scripts/.env', 'r'))

    if len(meters) > 0 :
        for item in meters:
            if item["hepek"] == payload["hepek"] :
                break
            if item["info"] == payload["info"] and payload["hepek"] != item["hepek"] :
                break
            entry += 1

        if entry < len(meters) :
            meters[entry] = payload
        else :
            meters.append(payload)

    else :
        meters.append(payload)

    with open('scripts/.env', 'w') as f:
        json.dump(meters, f, indent=4, sort_keys=True)

    
    acc_update_meter_readings(payload)

    return { "status": "ok" }        

def acc_update_contract_addresses(info) :

    meters = json.load(open('scripts/.env', 'r'))

    for item in meters:

        if item["energy_contract_address"] != info["energy_contract_address"] :
            item["energy_contract_address"] = info["energy_contract_address"]

        if item["ergon_contract_address"] != info["ergon_contract_address"] :
            item["ergon_contract_address"] = info["ergon_contract_address"]

        if item["carbon_contract_address"] != info["carbon_contract_address"] :
            item["carbon_contract_address"] = info["carbon_contract_address"]

    with open('scripts/.env', 'w') as f:
        json.dump(meters, f, indent=4, sort_keys=True)

    return { "status": "ok" }


def acc_update_meter_readings(payload) :

    if (payload.get("meter") is None) :
        return

    filename = payload["info"] + "_" + payload["hepek"] + ".json"

    path = 'scripts/' + filename
    
    print(f"path {path}")

    if os.path.exists(path) == False :
        with open(path, 'w+') as f:
            json.dump( [], f, indent=4, sort_keys=True)

    meters = json.load(open( path, 'r'))

    print(f"no reads {len(meters)}")

    if len(meters) >= 1440 :
        meters.pop(0)

    meters.append(payload["meter"])

    with open( path, 'w') as f:
        json.dump(meters, f, indent=4, sort_keys=True)



def acc_get_info_details(info_id) :

    acc = None
    meters = json.load(open('scripts/.env', 'r'))

    if len(meters) > 0 :    
        for item in meters:
            if info_id == item["info"] :
                acc = item
                break
    return acc        

def acc_get_hepek_details(hepek_id) :

    acc = None
    meters = json.load(open('scripts/.env', 'r'))

    if len(meters) > 0 :    
        for item in meters:
            if hepek_id == item["hepek"] :
                acc = item
                break
    return acc        

def acc_get_user_details(user_id) :

    acc = None
    meters = json.load(open('scripts/.env', 'r'))

    if len(meters) > 0 :    
        for item in meters:
            if user_id == item["user"] :
                acc = item
                break
    return acc        


def acc_get_accounts() :
    
    meters = json.load(open('scripts/.env', 'r'))
    return meters

