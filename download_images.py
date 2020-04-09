# All the images are hot links back to AC Wiki
# Don't want to hit their URL everytime someone uses the site or something
# Download all the images locally, use the Name as the filename under images/ dir

import json

import httpx


with open("villagers.json") as json_file:
    villagers = json.load(json_file)
    for villager in villagers["Villagers"]:
        image = villager.get('image')
        villager_name = villager.get('name')

        response = httpx.get(image)
        if response.is_error:
            print(f"Could not get image for: {villager_name}")
            continue

        with open(f"images/{villager_name}.png", 'wb') as out_file:
            out_file.write(response.content)
