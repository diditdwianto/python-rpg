from flask import Flask, jsonify, request
from flask_cors import CORS
import json
from pathlib import Path

app = Flask(__name__, static_folder="../static")
CORS(app)


@app.route("/")
def serve_index():
    return app.send_static_file("index.html")


DATA_FILE = Path(__file__).parent / "save_data.json"

DEFAULT_STATE = {
    "currencies": {"cookie": 0, "sausage": 0, "bread": 0, "gold": 0},
    "stats": {"hp": 100, "mp": 50, "damage": 10, "defense": 5},
    "equipment": {
        "helmet": None,
        "armor": None,
        "weapon": None,
        "shield": None,
        "boots": None,
        "accessory": None,
    },
    "inventory": [],
    "quests": [],
}


def load_state():
    if DATA_FILE.exists():
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return DEFAULT_STATE.copy()


def save_state(state):
    with open(DATA_FILE, "w") as f:
        json.dump(state, f, indent=2)


@app.route("/api/state", methods=["GET"])
def get_state():
    return jsonify(load_state())


@app.route("/api/state", methods=["POST"])
def update_state():
    state = request.json
    save_state(state)
    return jsonify({"status": "saved"})


@app.route("/api/shop", methods=["GET"])
def get_shop():
    shop = [
        {
            "id": "wooden_sword",
            "name": "Wooden Sword",
            "slot": "weapon",
            "stats": {"damage": 5},
            "cost": {"cookie": 50},
        },
        {
            "id": "iron_sword",
            "name": "Iron Sword",
            "slot": "weapon",
            "stats": {"damage": 15},
            "cost": {"cookie": 200},
        },
        {
            "id": "steel_sword",
            "name": "Steel Sword",
            "slot": "weapon",
            "stats": {"damage": 30},
            "cost": {"cookie": 500},
        },
        {
            "id": "leather_cap",
            "name": "Leather Cap",
            "slot": "helmet",
            "stats": {"hp": 10},
            "cost": {"cookie": 30},
        },
        {
            "id": "iron_helmet",
            "name": "Iron Helmet",
            "slot": "helmet",
            "stats": {"hp": 25, "defense": 3},
            "cost": {"cookie": 100},
        },
        {
            "id": "leather_armor",
            "name": "Leather Armor",
            "slot": "armor",
            "stats": {"hp": 20, "defense": 2},
            "cost": {"cookie": 60},
        },
        {
            "id": "chainmail",
            "name": "Chainmail",
            "slot": "armor",
            "stats": {"hp": 50, "defense": 5},
            "cost": {"cookie": 250},
        },
        {
            "id": "wooden_shield",
            "name": "Wooden Shield",
            "slot": "shield",
            "stats": {"defense": 3, "hp": 10},
            "cost": {"cookie": 40},
        },
        {
            "id": "iron_shield",
            "name": "Iron Shield",
            "slot": "shield",
            "stats": {"defense": 8, "hp": 25},
            "cost": {"cookie": 180},
        },
        {
            "id": "speed_boots",
            "name": "Speed Boots",
            "slot": "boots",
            "stats": {"hp": 15},
            "cost": {"cookie": 70},
        },
        {
            "id": "health_boots",
            "name": "Health Boots",
            "slot": "boots",
            "stats": {"hp": 40},
            "cost": {"cookie": 150},
        },
        {
            "id": "mana_ring",
            "name": "Mana Ring",
            "slot": "accessory",
            "stats": {"mp": 30, "damage": 3},
            "cost": {"cookie": 120},
        },
        {
            "id": "power_amulet",
            "name": "Power Amulet",
            "slot": "accessory",
            "stats": {"damage": 10, "mp": 20},
            "cost": {"cookie": 300},
        },
    ]
    return jsonify(shop)


@app.route("/api/buy", methods=["POST"])
def buy_item():
    data = request.json
    item_id = data.get("itemId")
    state = load_state()

    shop = [
        {"id": "wooden_sword", "cost": {"cookie": 50}},
        {"id": "iron_sword", "cost": {"cookie": 200}},
        {"id": "steel_sword", "cost": {"cookie": 500}},
        {"id": "leather_cap", "cost": {"cookie": 30}},
        {"id": "iron_helmet", "cost": {"cookie": 100}},
        {"id": "leather_armor", "cost": {"cookie": 60}},
        {"id": "chainmail", "cost": {"cookie": 250}},
        {"id": "wooden_shield", "cost": {"cookie": 40}},
        {"id": "iron_shield", "cost": {"cookie": 180}},
        {"id": "speed_boots", "cost": {"cookie": 70}},
        {"id": "health_boots", "cost": {"cookie": 150}},
        {"id": "mana_ring", "cost": {"cookie": 120}},
        {"id": "power_amulet", "cost": {"cookie": 300}},
    ]

    item = next((i for i in shop if i["id"] == item_id), None)
    if not item:
        return jsonify({"status": "error", "message": "Item not found"}), 400

    for currency, amount in item["cost"].items():
        if state["currencies"].get(currency, 0) < amount:
            return jsonify(
                {"status": "error", "message": f"Not enough {currency}"}
            ), 400

    for currency, amount in item["cost"].items():
        state["currencies"][currency] -= amount

    state["inventory"].append(item_id)
    save_state(state)
    return jsonify({"status": "success", "state": state})


@app.route("/api/equip", methods=["POST"])
def equip_item():
    data = request.json
    slot = data.get("slot")
    item_id = data.get("itemId")

    state = load_state()

    if slot not in state["equipment"]:
        return jsonify({"status": "error", "message": "Invalid slot"}), 400

    shop = {
        "wooden_sword": {"slot": "weapon", "stats": {"damage": 5}},
        "iron_sword": {"slot": "weapon", "stats": {"damage": 15}},
        "steel_sword": {"slot": "weapon", "stats": {"damage": 30}},
        "leather_cap": {"slot": "helmet", "stats": {"hp": 10}},
        "iron_helmet": {"slot": "helmet", "stats": {"hp": 25, "defense": 3}},
        "leather_armor": {"slot": "armor", "stats": {"hp": 20, "defense": 2}},
        "chainmail": {"slot": "armor", "stats": {"hp": 50, "defense": 5}},
        "wooden_shield": {"slot": "shield", "stats": {"defense": 3, "hp": 10}},
        "iron_shield": {"slot": "shield", "stats": {"defense": 8, "hp": 25}},
        "speed_boots": {"slot": "boots", "stats": {"hp": 15}},
        "health_boots": {"slot": "boots", "stats": {"hp": 40}},
        "mana_ring": {"slot": "accessory", "stats": {"mp": 30, "damage": 3}},
        "power_amulet": {"slot": "accessory", "stats": {"damage": 10, "mp": 20}},
    }

    for item in shop.values():
        if item["slot"] == slot:
            for stat, val in item["stats"].items():
                if stat in state["stats"]:
                    state["stats"][stat] = DEFAULT_STATE["stats"][stat]
                    for equipped_id in state["equipment"].values():
                        if equipped_id and equipped_id in shop:
                            for s, v in shop[equipped_id]["stats"].items():
                                state["stats"][s] += v

    if item_id is None:
        state["equipment"][slot] = None
    else:
        state["equipment"][slot] = item_id
        if item_id in shop:
            for stat, val in shop[item_id]["stats"].items():
                if stat in state["stats"]:
                    state["stats"][stat] += val

    save_state(state)
    return jsonify({"status": "success", "state": state})


@app.route("/api/quests", methods=["GET"])
def get_quests():
    quests = [
        {
            "id": "first_steps",
            "name": "First Steps",
            "description": "Accumulate 100 cookies",
            "reward": {"cookie": 50},
            "target": 100,
            "progress": 0,
        },
        {
            "id": "sausage_hunter",
            "name": "Sausage Hunter",
            "description": "Collect 10 sausages",
            "reward": {"cookie": 100},
            "target": 10,
            "progress": 0,
        },
        {
            "id": "equipment_ready",
            "name": "Equipment Ready",
            "description": "Equip your first item",
            "reward": {"cookie": 25},
            "target": 1,
            "progress": 0,
        },
    ]
    return jsonify(quests)


@app.route("/api/add_currency", methods=["POST"])
def add_currency():
    data = request.json
    currency = data.get("currency")
    amount = data.get("amount", 1)

    state = load_state()
    if currency in state["currencies"]:
        state["currencies"][currency] += amount
        save_state(state)

    return jsonify({"status": "success", "state": state})


if __name__ == "__main__":
    app.run(debug=True, port=8085)
