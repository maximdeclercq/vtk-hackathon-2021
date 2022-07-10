import os
from pathlib import Path
import json
import re
from math import sqrt

def distsq(a, b, p, q):
    return (a - p) ** 2 + (b - q) ** 2


for f in sorted(os.listdir(".")):
    if destination := next(iter(re.findall(r"hotels-(.*)\.json$", f)), None):
        print("===", destination, "===")
        hotels = json.loads(Path(f).read_text())
        print("number of hotels:", len(hotels))
        print("total number of rooms:", sum(hotel.get("rooms", 0) for hotel in hotels))
        mx_dist, mx_a, mx_b = -1e9, None, None
        for i in range(len(hotels)):
            a = hotels[i]
            for j in range(i + 1, len(hotels)):
                b = hotels[j]
                dist = distsq(a["latitude"], a["longitude"], b["latitude"], b["longitude"])
                if dist > mx_dist:
                    mx_dist, mx_a, mx_b = dist, a, b
        print(f"furthest:\n- {mx_a['name']}\n- {mx_b['name']}\n= {sqrt(mx_dist)}")
