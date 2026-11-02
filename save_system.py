"""Local JSON save file (data/save.json). Everything works offline."""
import copy
import json
import os
import catalog
from settings import DATA_DIR, SAVE_PATH

DEFAULT_SAVE = {
    "version": 1,
    "coins": 100,
    "unlocked": {
        "characters": ["kid", "student", "farmer"],
        "hats": ["none", "cap"],
        "outfits": ["pula"],
        "accessories": ["none"],
        "flags": ["araw"],
        "bamboo": ["berde"],
        "skies": ["stage"],
    },
    "unlocked_stages": [1],
    "best_time_attack": {},
    "best_time_attack_overall": None,
    "equipped": {"flags": "araw", "bamboo": "berde", "skies": "stage"},
    "loadouts": {"p1": dict(catalog.DEFAULT_LOADOUT_P1), "p2": dict(catalog.DEFAULT_LOADOUT_P2)},
    "settings": {"music": True, "sfx": True, "fullscreen": False, "music_vol": 1.0},
    "stats": {"matches": 0, "p1_wins": 0, "p2_wins": 0, "time_attack_runs": 0},
    "last_stage": 1,
}


def _merge(base, new):
    """Overlay `new` on `base`, keeping the structure of `base`."""
    for k, v in new.items():
        if k in base and isinstance(base[k], dict) and isinstance(v, dict) and k not in ("best_time_attack",):
            _merge(base[k], v)
        else:
            base[k] = v
    return base


class SaveSystem:
    def __init__(self, path=SAVE_PATH):
        self.path = path
        self.data = copy.deepcopy(DEFAULT_SAVE)
        self.load()

    # -- file io ---------------------------------------------------------
    def load(self):
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                raw = json.load(f)
            if isinstance(raw, dict):
                _merge(self.data, raw)
        except (OSError, ValueError):
            self.data = copy.deepcopy(DEFAULT_SAVE)
            self.save()
        self._sanitize()

    def save(self):
        try:
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
            tmp = self.path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2)
            os.replace(tmp, self.path)
        except OSError:
            pass  # read-only folder: the game still works, it just can't save

    def reset(self):
        self.data = copy.deepcopy(DEFAULT_SAVE)
        self.save()

    def _sanitize(self):
        d = self.data
        for name, key, items in catalog.CATEGORIES:
            ids = {i["id"] for i in items}
            d["unlocked"][key] = [i for i in d["unlocked"].get(key, []) if i in ids] or [items[0]["id"]]
        for p in ("p1", "p2"):
            lo = d["loadouts"][p]
            if lo.get("character") not in d["unlocked"]["characters"]:
                lo["character"] = "kid"
            for slot, key in (("hat", "hats"), ("outfit", "outfits"), ("accessory", "accessories")):
                if lo.get(slot, "default") != "default" and lo[slot] not in d["unlocked"][key]:
                    lo[slot] = "default"
        if 1 not in d["unlocked_stages"]:
            d["unlocked_stages"].append(1)

    # -- convenience ------------------------------------------------------
    @property
    def coins(self):
        return self.data["coins"]

    def add_coins(self, n):
        self.data["coins"] = max(0, self.data["coins"] + int(n))

    def is_unlocked(self, key, item_id):
        return item_id in self.data["unlocked"][key]

    def unlock(self, key, item_id):
        if item_id not in self.data["unlocked"][key]:
            self.data["unlocked"][key].append(item_id)

    def unlock_stage(self, stage_id):
        if stage_id not in self.data["unlocked_stages"] and 1 <= stage_id <= len(catalog.STAGES):
            self.data["unlocked_stages"].append(stage_id)

    def stage_unlocked(self, stage_id):
        return stage_id in self.data["unlocked_stages"]

    def loadout(self, player):
        return self.data["loadouts"]["p%d" % player]

    @property
    def settings(self):
        return self.data["settings"]

    def record_time_attack(self, stage_id, seconds):
        """Returns True if this is a new personal best."""
        best = self.data["best_time_attack"]
        key = str(stage_id)
        new = key not in best or seconds < best[key]
        if new:
            best[key] = round(seconds, 2)
        overall = self.data["best_time_attack_overall"]
        if overall is None or seconds < overall:
            self.data["best_time_attack_overall"] = round(seconds, 2)
        return new

    def best_time(self, stage_id):
        return self.data["best_time_attack"].get(str(stage_id))
