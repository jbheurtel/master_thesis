import math

alpha = 0.05  # whatever sort of rate
min_damage = 0.23  # minimum damage whatever the flood duration is
x_0 = 24  # at time x_0, tje ff = 0.5


def floodFactorLogit(h_flood):
    s = 1 / (1 + math.exp(-alpha * (h_flood - x_0)))
    return max(min_damage, s)


def estimate_damage(flooded_surface, destruction_factor, area_value):
    return round(flooded_surface * destruction_factor * area_value, 2)


if __name__ == '__main__':

    picture_infos = {
        "1":
            {"surface": 203,
             "flooded_levels": 1,
             "confidence": 0.56,
             "position": {},
            },
        "2":
            {"surface": 490,
             "flooded_levels": 1,
             "confidence": 0.83,
             "position": {},
             },
        "3":
            {"surface": 100,
             "flooded_levels": 0,
             "confidence": 0.9,
             "position": {},
             },
        "4":
            {"surface": 150,
             "flooded_levels": 1,
             "confidence": 0.4,
             "position": {},
             }
    }

    hours_flooded = 6
    area_value = 1250

    dest_factor = floodFactorLogit(hours_flooded)

    for k, v in picture_infos.items():
        picture_infos[k]["flooded_surface"] = v["surface"] * v["flooded_levels"]

    for k, v in picture_infos.items():
        picture_infos[k]["damage"] = estimate_damage(v["flooded_surface"], dest_factor, area_value)

    print({k: v["damage"] for k, v in picture_infos.items()})


