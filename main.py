import telebot
import random
import json
import os
import time

# ================= CONFIG =================
TOKEN = "8995996571:AAFvB6LWjy0cLAxMSvr8rkY3vi0pIC6utK0"
ADMIN_USERNAME = "hoseinst"

bot = telebot.TeleBot(TOKEN)
DATA_FILE = "data.json"

# ================= LOAD =================
def load():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {
        "players": {},
        "world_boss": {"hp": 10000, "active": False},
        "economy": {"inflation": 1.0}
    }

def save():
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

data = load()

# ================= MAPS =================
MAPS = [
    "Holy Luminarchy", "Frostheim", "Voidbreak Wastes",
    "Storm Archipelago", "Sunken City", "EmberHollow",
    "Abyssal Black Market", "Dragonnest Peaks", "Celestial Spire"
]

# ================= CHARACTERS =================
CHARACTERS = {
    "Vaelthryx": {"element": "Void", "katana": "Voidreaver"},
    "Nyxarion": {"element": "Shadow", "katana": "Nightfall"},
    "Zephyrelis": {"element": "Wind/Fire", "katana": "Stormwhisper"},
    "Kaelvorith": {"element": "Fire", "katana": "Infernal Fang"},
    "Aetheryx": {"element": "Energy", "katana": "Celestial Edge"},
}

# ================= LEGENDARY ITEMS =================
LEGENDARY = [
    "🔥 Blade of Infinity",
    "⚡ Thunderheart Core",
    "🌌 Void Emperor Katana",
    "🩸 Blood of Gods",
    "❄ Frost Eternal Edge"
]

# ================= INIT =================
def init(uid, username):
    if uid not in data["players"]:
        data["players"][uid] = {
            "name": username,
            "character": None,
            "hp": 100,
            "xp": 0,
            "level": 1,
            "zen": 0,
            "energy": 5,
            "inventory": [],
            "map": "Holy Luminarchy",
            "combo": 0
        }
        save()

# ================= ECONOMY INFLATION =================
def apply_inflation(amount):
    return int(amount * data["economy"]["inflation"])

def update_inflation():
    # هر بار جنگ جهانی یا باس → inflation بالا میره
    data["economy"]["inflation"] += 0.01

# ================= ENERGY =================
def use_energy(p):
    if p["energy"] <= 0:
        return False
    p["energy"] -= 1
    return True

# ================= START =================
@bot.message_handler(commands=["start"])
def start(msg):
    uid = str(msg.from_user.id)
    init(uid, msg.from_user.username or str(uid))

    kb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("🎴 character", "⚔ attack")
    kb.row("🆚 pvp", "👑 worldboss")
    kb.row("🗺 map", "💰 shop")
    kb.row("📊 status", "🎒 inventory")

    bot.send_message(msg.chat.id, "🔥 ASTRAL ABYSS MMO ONLINE", reply_markup=kb)

# ================= CHARACTER =================
@bot.message_handler(func=lambda m: m.text == "🎴 character")
def character(msg):
    uid = str(msg.from_user.id)
    p = data["players"][uid]

    if p["character"]:
        return bot.send_message(msg.chat.id, "❌ already have character")

    p["character"] = random.choice(list(CHARACTERS.keys()))
    save()

    c = CHARACTERS[p["character"]]

    bot.send_message(msg.chat.id,
        f"🎴 {p['character']}\n⚔ {c['element']}\n🗡 {c['katana']}"
    )

# ================= COMBO SYSTEM =================
def combo_damage(p):
    base = p["level"] * random.randint(8, 15)

    if p["combo"] >= 3:
        base *= 2
        p["combo"] = 0
    else:
        p["combo"] += 1

    return base

# ================= LEGENDARY DROP =================
def drop_legendary():
    if random.randint(1, 100) <= 5:  # 5%
        return random.choice(LEGENDARY)
    return None

# ================= ATTACK =================
@bot.message_handler(func=lambda m: m.text == "⚔ attack")
def attack(msg):
    uid = str(msg.from_user.id)
    p = data["players"][uid]

    if not use_energy(p):
        return bot.send_message(msg.chat.id, "⚡ no energy")

    dmg = combo_damage(p)
    enemy = random.randint(80, 200) - dmg

    if enemy <= 0:
        xp = random.randint(20, 60)
        zen = apply_inflation(random.randint(10, 50))

        p["xp"] += xp
        p["zen"] += zen

        item = drop_legendary()
        if item:
            p["inventory"].append(item)

        if p["xp"] >= p["level"] * 100:
            p["level"] += 1
            p["hp"] = 100

        save()

        bot.send_message(msg.chat.id,
            f"🏆 WIN!\n+{xp} XP\n+{zen} Zen\n"
            f"{'💎 LEGENDARY DROP: ' + item if item else ''}"
        )
    else:
        p["hp"] -= 10
        save()
        bot.send_message(msg.chat.id, "💀 lose")

# ================= WORLD BOSS =================
@bot.message_handler(func=lambda m: m.text == "👑 worldboss")
def worldboss(msg):
    uid = str(msg.from_user.id)
    p = data["players"][uid]

    boss = data["world_boss"]

    if not boss["active"]:
        boss["active"] = True
        boss["hp"] = 10000

    dmg = p["level"] * random.randint(10, 25)
    boss["hp"] -= dmg

    update_inflation()

    if boss["hp"] <= 0:
        reward = apply_inflation(random.randint(200, 500))
        p["zen"] += reward
        p["xp"] += 100

        boss["active"] = False

        save()

        return bot.send_message(msg.chat.id,
            f"👑 WORLD BOSS DOWN!\n+{reward} Zen 💰"
        )

    save()
    bot.send_message(msg.chat.id, f"👑 Boss HP: {boss['hp']}")

# ================= MAP =================
@bot.message_handler(func=lambda m: m.text == "🗺 map")
def map_move(msg):
    uid = str(msg.from_user.id)
    p = data["players"][uid]

    p["map"] = random.choice(MAPS)
    save()

    bot.send_message(msg.chat.id, f"🗺 {p['map']}")

# ================= SHOP =================
@bot.message_handler(func=lambda m: m.text == "💰 shop")
def shop(msg):
    uid = str(msg.from_user.id)
    p = data["players"][uid]

    price = apply_inflation(random.randint(50, 120))
    item = random.choice(["Potion", "Energy Core", "Blade Fragment"])

    if p["zen"] < price:
        return bot.send_message(msg.chat.id, "❌ not enough zen")

    p["zen"] -= price
    p["inventory"].append(item)
    save()

    bot.send_message(msg.chat.id, f"🛒 bought {item} for {price}")

# ================= PVP =================
@bot.message_handler(func=lambda m: m.text == "🆚 pvp")
def pvp(msg):
    uid = str(msg.from_user.id)
    p1 = data["players"][uid]

    enemies = list(data["players"].keys())
    enemy = random.choice(enemies)

    if enemy == uid:
        return

    p2 = data["players"][enemy]

    power1 = p1["level"] * random.randint(10, 25)
    power2 = p2["level"] * random.randint(10, 25)

    if power1 > power2:
        p1["zen"] += 40
        result = "🏆 win"
    else:
        p1["hp"] -= 20
        result = "💀 lose"

    save()
    bot.send_message(msg.chat.id, result)

# ================= STATUS =================
@bot.message_handler(func=lambda m: m.text == "📊 status")
def status(msg):
    uid = str(msg.from_user.id)
    p = data["players"][uid]

    bot.send_message(msg.chat.id,
        f"👤 {p['name']}\n"
        f"🎴 {p['character']}\n"
        f"⭐ Lvl {p['level']}\n"
        f"❤️ HP {p['hp']}\n"
        f"⚡ Energy {p['energy']}\n"
        f"💰 Zen {p['zen']}\n"
        f"🗺 {p['map']}\n"
        f"🔥 Combo {p['combo']}"
    )

# ================= INVENTORY =================
@bot.message_handler(func=lambda m: m.text == "🎒 inventory")
def inv(msg):
    uid = str(msg.from_user.id)
    p = data["players"][uid]

    bot.send_message(msg.chat.id,
        "\n".join(p["inventory"]) if p["inventory"] else "empty"
    )

# ================= NPC SYSTEM =================
@bot.message_handler(func=lambda m: True)
def npc(msg):
    if msg.text.startswith("/"):
        return

    replies = [
        "🌌 The void whispers...",
        "⚔ Battle echoes in distance...",
        "🔥 Energy shifts around you...",
        "🗺 The world is unstable...",
        "👁 Something is watching..."
    ]

    bot.send_message(msg.chat.id, random.choice(replies))

# ================= RUN =================
print("🔥 MMO RPG RUNNING...")
bot.infinity_polling()