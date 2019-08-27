import bs4
import json

with open("data/locations.html") as f:
    html = f.read()


soup = bs4.BeautifulSoup(html)
locations_nested = {}
locations_flat = {}
locations_with_children = set()


for a in soup.find_all("a"):
    name = a.text
    href = a["href"]
    structure =[ x for x in href.split("/") if x not in {"", "alquiler-viviendas", "mapa"}]
    if structure[0] == "barcelona":
        depth = len(structure)
        i = 1
        data = locations_nested
        for key in structure:
            if key not in data:
                data[key] = {}
            if i == depth:
                data[key]["name"] = name
                data[key]["href"] = href
                locations_flat[key] = data[key]
            else:
                if "children" not in data[key]:
                    data[key]["children"] = {}
                data = data[key]["children"]
                locations_with_children.add(key)
            i+=1


leaf_locations = {k:v for (k, v) in locations_flat.items() if k not in locations_with_children}

with open("data/locations_nested.json", "w") as f:
    json.dump(locations_nested, f)

with open("data/leaf_locations.json", "w") as f:
    json.dump(leaf_locations, f)
