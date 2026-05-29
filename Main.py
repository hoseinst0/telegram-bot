import telebot
import random
import json
import os
import time

TOKEN = "8995996571:AAGCcspaubu_TcQRBItkjFjBllzTP4ozSF4"
bot = telebot.TeleBot(TOKEN)

ADMIN_USERNAME = "hoseinst"

DATA_FILE = "players.json"

# ================= LOAD =================
def load():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"players": {}, "guilds": {}, "market": {}}

def save():
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

data = load()

# ================= CONSTANTS =================
MAX_HP = 100
MAX_ENERGY = 5
ENERGY_RESET_TIME = 600

MAPS = [
    "Celestial Spire", "Holy Luminarchy", "Frostheim",
    "Voidbreak Wastes", "Stormward Archipelago",
    "Azure Tides Empire", "The Sunken City",
    "Clockwork Depths", "Sands of Eternity",
    "Verdant Vale", "Ruins of Orion-7",
    "Dragonnest Peaks", "EmberHollow",
    "Dreadgate Citadel", "Abyssal Black Market",
    "Player Dominion"
]

CHARACTERS = {
    "Vaelthryx": {"element": "Void", "katana": "Voidreaver",
                  "powers": ["گام خلأ", "کشش گرانشی", "هاله سکوت", "برش تاریکی"]},

    "Nyxarion": {"element": "Shadow", "katana": "Nightfall",
                 "powers": ["لغزش سایه", "دید در تاریکی", "ضربه بی‌صدا"]},

    "Zephyrelis": {"element": "Wind/Fire", "katana": "Stormwhisper",
                   "powers": ["کنترل باد", "کنترل آتش", "گام سبک"]},

    "Kaelvorith": {"element": "Fire", "katana": "Infernal Fang",
                   "powers": ["برش شعله", "یورش آتش", "سپر خاکستر"]},

    "Aetheryx": {"element": "Energy", "katana": "Celestial Edge",
                 "powers": ["موج انرژی", "جهش نور", "سپر درخشان"]}
}

# ================= INIT =================
def init_player(uid):
    if uid not in data["players"]:
        data["players"][uid] = {
            "character": None,
            "hp": MAX_HP,
            "energy": MAX_ENERGY,
            "last_energy": time.time(),
            "xp": 0,
            "level": 1,
            "zen": 0,
            "inventory": [],
            "map": "Holy Luminarchy"
        }
        save()

# ================= ADMIN CHECK =================
def is_admin(msg):
    return msg.from_user.username == ADMIN_USERNAME

# ================= ENERGY =================
def regen_energy(p):
    if time.time() - p["last_energy"] > ENERGY_RESET_TIME:
        p["energy"] = min(MAX_ENERGY, p["energy"] + 1)
        p["last_energy"] = time.time()

def use_energy(p):
    regen_energy(p)
    if p["energy"] <= 0:
        return False
    p["energy"] -= 1
    return True

# ================= START =================
@bot.message_handler(commands=['start'])
def start(msg):
    uid = str(msg.from_user.id)
    init_player(uid)

    kb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("🎴 کرکتر", "📜 اطلاعات")
    kb.row("⚔ فایت", "🆚 PvP")
    kb.row("🗺 مپ", "👤 پروفایل")
    kb.row("🎒 آیتم")

    bot.send_message(msg.chat.id, "🔥 ASTRAL RPG ONLINE", reply_markup=kb)

# ================= CHARACTER =================
@bot.message_handler(func=lambda m: m.text == "🎴 کرکتر")
def char(msg):
    uid = str(msg.from_user.id)
    p = data["players"][uid]

    if p["character"]:
        return bot.send_message(msg.chat.id, "❌ قبلاً داری")

    p["character"] = random.choice(list(CHARACTERS.keys()))
    save()

    c = CHARACTERS[p["character"]]

    bot.send_message(msg.chat.id,
        f"🎴 {p['character']}\n"
        f"⚔ {c['element']}\n"
        f"🗡 {c['katana']}"
    )

# ================= ADMIN GIVE CHARACTER =================
@bot.message_handler(commands=['givechar'])
def give_char(msg):
    if not is_admin(msg):
        return bot.send_message(msg.chat.id, "⛔ دسترسی نداری")

    try:
        parts = msg.text.split()
        target_id = parts[1]
        char_name = parts[2]

        if char_name == "random":
            char_name = random.choice(list(CHARACTERS.keys()))

        init_player(target_id)
        data["players"][target_id]["character"] = char_name
        save()

        bot.send_message(msg.chat.id,
            f"✅ دادم {char_name} به {target_id}"
        )
    except:
        bot.send_message(msg.chat.id, "فرمت: /givechar user_id name")

# ================= INFO POWER =================
@bot.message_handler(func=lambda m: m.text == "📜 اطلاعات")
def info(msg):
    uid = str(msg.from_user.id)
    p = data["players"][uid]

    if not p["character"]:
        return bot.send_message(msg.chat.id, "اول کرکتر بگیر")

    c = CHARACTERS[p["character"]]

    bot.send_message(msg.chat.id,
        f"🎴 {p['character']}\n"
        f"⚔ عنصر: {c['element']}\n"
        f"🗡 کاتانا: {c['katana']}\n"
        f"🔥 قدرت‌ها:\n- " + "\n- ".join(c["powers"])
    )

# ================= FIGHT =================
@bot.message_handler(func=lambda m: m.text == "⚔ فایت")
def fight(msg):
    uid = str(msg.from_user.id)
    p = data["players"][uid]

    if not use_energy(p):
        return bot.send_message(msg.chat.id, "⚡ انرژی نداری")

    enemy = random.randint(50, 150)
    dmg = p["level"] * random.randint(10, 20)

    enemy -= dmg

    if enemy <= 0:
        p["xp"] += 20
        p["zen"] += 30

        if p["xp"] >= p["level"] * 100:
            p["level"] += 1
            p["hp"] = MAX_HP

        save()
        bot.send_message(msg.chat.id, "⚔ بردی!")
    else:
        p["hp"] -= 10
        save()
        bot.send_message(msg.chat.id, "💀 باختی")

# ================= MAP =================
@bot.message_handler(func=lambda m: m.text == "🗺 مپ")
def map_move(msg):
    uid = str(msg.from_user.id)
    p = data["players"][uid]

    p["map"] = random.choice(MAPS)
    save()

    bot.send_message(msg.chat.id, f"🗺 رفتی: {p['map']}")

# ================= PROFILE =================
@bot.message_handler(func=lambda m: m.text == "👤 پروفایل")
def profile(msg):
    uid = str(msg.from_user.id)
    p = data["players"][uid]

    bot.send_message(msg.chat.id,
        f"👤 {p['character']}\n"
        f"⭐ Lv {p['level']}\n"
        f"❤️ HP {p['hp']}\n"
        f"⚡ Energy {p['energy']}\n"
        f"💰 Zen {p['zen']}\n"
        f"🗺 {p['map']}"
    )

# ================= INVENTORY =================
@bot.message_handler(func=lambda m: m.text == "🎒 آیتم")
def inv(msg):
    uid = str(msg.from_user.id)
    p = data["players"][uid]

    bot.send_message(msg.chat.id,
        "\n".join(p["inventory"]) if p["inventory"] else "خالی"
    )

print("🔥 BOT RUNNING...")
bot.infinity_polling()
