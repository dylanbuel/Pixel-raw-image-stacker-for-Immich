import requests
import json
import argparse

def getAPIInfo() -> dict:
    parser = argparse.ArgumentParser(
                    prog='Raw image stacker',
                    description=' This application is intended to stack RAW and JPEG images taken by Pixel phones inside Immich')
    parser.add_argument('--config', help='Path to config file', default='config.json')
    
    args = parser.parse_args()
    with open (args.config) as configFile:
        config = json.load(configFile)
        return config

def getAssets(apiConfig: dict) -> list:
    url = apiConfig["baseURL"] + "api/search/metadata/"
    assets = []
    page = 1

    while True:
        headers = {
            "x-api-key": apiConfig["apiKey"],
            "Content-Type": "application/json"
        }
        data = {
            "type": "IMAGE",
            "page": page
        }

        response = requests.post(url, headers=headers, json=data)
        responseDate = response.json()
        if response.status_code != 200:
            raise Exception(f"Failed to get assets: {response.status_code} - {response.text}")

        assets.extend(responseDate["assets"]["items"])
        page = responseDate["assets"]["nextPage"]

        if page is None:
            break

    return assets

def groupAssetsByFileType(assets: list) -> dict:
    assetsByFileType = {}
    for asset in assets:
        mimeType = asset["originalMimeType"]
        if mimeType not in assetsByFileType:
            assetsByFileType[mimeType] = []
        assetsByFileType[mimeType].append(asset)
    return assetsByFileType

def listJpgAndDngWithMatchingIDs(jpgAssets: list, dngAssets: list) -> list:
    matchingAssets = []
    for rawAsset in dngAssets:
        id = rawAsset["originalFileName"].split(".")[0]
        for jpgAsset in jpgAssets:
            jpgId = jpgAsset["originalFileName"].split(".")[0]
            if id == jpgId:
                matchingAssets.append({
                    "id": id,
                    "jpgAsset": jpgAsset,
                    "dngAsset": rawAsset
                })
    return matchingAssets

def getExistingStackedAssets(apiConfig: dict) -> list:
    url = apiConfig["baseURL"] + "api/stacks"
    headers = {
        "x-api-key": apiConfig["apiKey"]
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        stacks = response.json()
    else:
        raise Exception(f"Failed to get stacked assets: {response.status_code} - {response.text}")
    
    ids = []
    for stack in stacks:
        ids.append(stack["assets"][0]["originalFileName"].split(".")[0])
    return ids

def cleanAssetsThatAreStacked(assetsWithMatchingIDs: list, assetsWithExistingStacks: list) -> list:
    cleanedAssets = []
    for asset in assetsWithMatchingIDs:
        if asset["id"] not in assetsWithExistingStacks:
            cleanedAssets.append(asset)
    return cleanedAssets

def stackDuplicate(assetsWithMatchingIDs: list, apiConfig: dict) -> list:
    stackedAssets = []
    for asset in assetsWithMatchingIDs:
        url = apiConfig["baseURL"] + "api/stacks"
        headers = {
            "x-api-key": apiConfig["apiKey"],
            "Content-Type": "application/json"
        }
        data = {
            "assetIds": [asset["jpgAsset"]["id"], asset["dngAsset"]["id"]]
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 201:
            stackedAssets.append(asset["id"])
        else:
            raise Exception(f"Failed to stack assets for ID {asset['id']}: {response.status_code} - {response.text}")
    return stackedAssets


if __name__ == '__main__':
    print("Reading Config")
    apiConfig = getAPIInfo()
    print("Getting all Assets")
    assets = getAssets(apiConfig)
    print("Grouping Assets by MIME Type")
    assetsByMIMEType = groupAssetsByFileType(assets)
    print("Finding JPG and DNG Assets with Matching Pixel IDs")
    assetsWithMatchingIDs = listJpgAndDngWithMatchingIDs(assetsByMIMEType["image/jpeg"], assetsByMIMEType["image/dng"])
    print("Getting a list of all Assets that are already Stacked")
    assetsWithExistingStacks = getExistingStackedAssets(apiConfig)
    print("Cleaning list of Assets to Stack by removing those that are already Stacked")
    assetsToStack = cleanAssetsThatAreStacked(assetsWithMatchingIDs, assetsWithExistingStacks)
    print(f"Stacking {len(assetsToStack)} Assets")
    stackedAssets = stackDuplicate(assetsToStack, apiConfig)
    print(f"Stacked {len(stackedAssets)} Assets")
    for assetId in stackedAssets:
        print(f"Stacked Asset with ID: {assetId}")