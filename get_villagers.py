import json

import httpx
from bs4 import BeautifulSoup

from html_parser import HTMLTableParser


# Base URL for Villagers in New Horizons
villagers_list_url = (
    "https://animalcrossing.fandom.com/wiki/Villager_list_(New_Horizons)"
)

request = httpx.get(villagers_list_url)
raw_html = request.text

soup = BeautifulSoup(raw_html, "html.parser")
# Best guess to find Villagers table
table = soup.find("table", attrs={"class": "roundy sortable"})


def _find_img_src(name, query_type=None):
    image_url = None
    base_villager_url = "https://animalcrossing.fandom.com/wiki/{name}"
    image_class_name = "pi-image-thumbnail"
    if query_type:
        name = f"{name}_({query_type})"
    villager_page = base_villager_url.format(name=name)
    villager = httpx.get(villager_page)
    raw_villager = villager.text
    villager_soup = BeautifulSoup(raw_villager, "html.parser")
    villager_image_src = villager_soup.find("img", attrs={"class": image_class_name})
    if villager_image_src:
        image_url = villager_image_src.get("src")

    return image_url


# Parse through the AC Villagers table
ht = HTMLTableParser()
table = ht.parse_html_table(table)
df = table.replace(r"\n", " ", regex=True)

df_json = df.to_json()
ac_villagers = json.loads(df_json)

# Other columns include Images which are not available, and catch phrases
names = list(ac_villagers.get(" Name\n").values())
personalities = list(ac_villagers.get(" Personality\n").values())
species = list(ac_villagers.get(" Species\n").values())
birthdays = list(ac_villagers.get(" Birthday\n").values())

names = [n.strip() for n in names]
personalities = [p.strip() for p in personalities]
species = [s.strip() for s in species]
birthdays = [b.strip() for b in birthdays]

# Make sure we don't have an inequality somewhere, otherwise idk what to do, panic mode.
print(
    "Checking if we have the same amount of names, personalities, species, and birthdays: "
)
print(len(names) == len(personalities) == len(species) == len(birthdays))

ac_villagers_dict = {"Villagers": []}

ac_villager_obj = {
    "name": "",
    "personality": "",
    "species": "",
    "birthday": "",
    "image": "N/A",
}

for index, name in enumerate(names):

    # Just go with NA version
    if name == "JacobNAJakeyPAL":
        name = "Jacob"
    if name == "SporkNACracklePAL":
        name = "Spork"
    if name == "Ren\u00e9e":
        name = "Renée"

    print(f"Looking for {name}...")

    species_name = species[index].lower()

    # Try just the villager name, then various weird filter types
    village_img_src = _find_img_src(name)
    if village_img_src is None:
        village_img_src = _find_img_src(name, query_type="villager")
    if village_img_src is None:
        village_img_src = _find_img_src(name, query_type=species_name)
    if village_img_src is None:
        village_img_src = _find_img_src(name, query_type="New_Leaf")
    if village_img_src is None:
        village_img_src = _find_img_src(name, query_type="Wild_World")

    image_src_url = "N/A"
    if village_img_src:
        image_src_url = village_img_src

    ac_villager_obj = {
        "name": name,
        "personality": personalities[index],
        "species": species[index],
        "birthday": birthdays[index],
        "image": image_src_url,
    }
    ac_villagers_dict["Villagers"].append(ac_villager_obj)

# Save results to json file.
with open("villagers.json", "w") as json_file:
    json.dump(ac_villagers_dict, json_file)
