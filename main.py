import telebot
import random
import json
import os

TOKEN = "8995996571:AAGCcspaubu_TcQRBItkjFjBllzTP4ozSF4"
bot = telebot.TeleBot(TOKEN)

DATA_FILE = "players.json"


# ================= LOAD =================
def load():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"players": {}, "guilds": {}, "boss": None}


def save():
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


data = load()


# ================= START =================
@bot.message_handler(commands=['start'])
def start(msg):
    uid = str(msg.from_user.id)

    if uid not in data["players"]:
        data["players"][uid] = {
            "character": None,
            "xp": 0,
            "level": 1,
            "hp": 100,
            "gold": 0,
            "inventory": [],
            "skill": 0,
            "guild": None
        }
        save()

    kb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("🎴 کرکتر", "⚔ فایت")
    kb.row("🆚 PvP", "👑 باس")
    kb.row("👤 پروفایل", "🎒 آیتم")
    kb.row("🗺 مپ", "🏰 کلن")

    bot.send_message(msg.chat.id, "🔥 MMO RPG Ready!", reply_markup=kb)


# ================= CHARACTER =================
@bot.message_handler(func=lambda m: m.text == "🎴 کرکتر")
def char(msg):
    uid = str(msg.from_user.id)
    p = data["players"].get(uid)

    if not p:
        return bot.send_message(msg.chat.id, "اول /start")

    if p["character"]:
        return bot.send_message(msg.chat.id, "❌ قبلاً گرفتی")

    chars = ["Vaelthryx","Nyxarion","Zephyrelis","Aetheryx","Solmyrion"]
    p["character"] = random.choice(chars)
    save()

    bot.send_message(msg.chat.id, f"🎴 {p['character']}")


# ================= FIGHT =================
@bot.message_handler(func=lambda m: m.text == "⚔ فایت")
def fight(msg):
    uid = str(msg.from_user.id)
    p = data["players"].get(uid)

    if not p:
        return bot.send_message(msg.chat.id, "اول /start")

    enemy = random.randint(40, 150)
    dmg = random.randint(20, 60)

    enemy -= dmg

    if enemy <= 0:
        xp = random.randint(10, 60)
        gold = random.randint(5, 40)

        p["xp"] += xp
        p["gold"] += gold

        if p["xp"] >= p["level"] * 100:
            p["level"] += 1
            p["hp"] += 25
            p["skill"] += 1

        save()

        bot.send_message(msg.chat.id,
            f"⚔ بردی!\n+{xp} XP\n+{gold} 💰"
        )
    else:
        bot.send_message(msg.chat.id, "💀 باختی!")


# ================= PVP =================
@bot.message_handler(func=lambda m: m.text == "🆚 PvP")
def pvp(msg):
    uid = str(msg.from_user.id)

    if uid not in data["players"]:
        return bot.send_message(msg.chat.id, "اول /start")

    players = list(data["players"].keys())

    if len(players) < 2:
        return bot.send_message(msg.chat.id, "هنوز پلیر کافی نیست")

    enemy_id = random.choice(players)

    while enemy_id == uid:
        enemy_id = random.choice(players)

    p1 = data["players"][uid]
    p2 = data["players"][enemy_id]

    power1 = p1["level"] * random.randint(5, 15)
    power2 = p2["level"] * random.randint(5, 15)

    if power1 > power2:
        p1["gold"] += 20
        result = "🏆 بردی PvP!"
    else:
        p1["hp"] -= 10
        result = "💀 باختی PvP!"

    save()
    bot.send_message(msg.chat.id, result)


# ================= BOSS =================
@bot.message_handler(func=lambda m: m.text == "👑 باس")
def boss(msg):
    uid = str(msg.from_user.id)
    p = data["players"].get(uid)

    if not p:
        return bot.send_message(msg.chat.id, "اول /start")

    boss_hp = random.randint(150, 300)
    dmg = p["level"] * random.randint(10, 25)

    boss_hp -= dmg

    if boss_hp <= 0:
        reward = random.randint(50, 120)
        p["gold"] += reward
        p["xp"] += 30
        save()

        bot.send_message(msg.chat.id, f"👑 باس مرد!\n+{reward} 💰")
    else:
        bot.send_message(msg.chat.id, "👹 باس هنوز زنده‌ست!")


# ================= PROFILE =================
@bot.message_handler(func=lambda m: m.text == "👤 پروفایل")
def prof(msg):
    uid = str(msg.from_user.id)
    p = data["players"].get(uid)

    if not p:
        return bot.send_message(msg.chat.id, "اول /start")

    bot.send_message(msg.chat.id,
        f"👤 Profile\n"
        f"🎴 {p['character']}\n"
        f"⭐ Level {p['level']}\n"
        f"XP {p['xp']}\n"
        f"❤️ HP {p['hp']}\n"
        f"💰 {p['gold']}"
    )


# ================= INVENTORY =================
@bot.message_handler(func=lambda m: m.text == "🎒 آیتم")
def inv(msg):
    uid = str(msg.from_user.id)
    p = data["players"].get(uid)

    if not p:
        return bot.send_message(msg.chat.id, "اول /start")

    bot.send_message(
        msg.chat.id,
        "\n".join(p["inventory"]) if p["inventory"] else "خالی"
    )


# ================= MAP =================
@bot.message_handler(func=lambda m: m.text == "🗺 مپ")
def map(msg):
    names = [
        p["character"]
        for p in data["players"].values()
        if p["character"]
    ]

    bot.send_message(msg.chat.id, "🗺 Players:\n" + "\n".join(names))


# ================= GUILD =================
@bot.message_handler(func=lambda m: m.text == "🏰 کلن")
def guild(msg):
    bot.send_message(msg.chat.id, "🏰 سیستم کلن فعلاً خامه 😈")


print("🔥 BOT RUNNING...")
bot.infinity_polling()