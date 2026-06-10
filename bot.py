import discord
from discord.ext import commands
from discord import app_commands
import json, os, time
from datetime import datetime

TOKEN = os.getenv("DISCORD_TOKEN", "YOUR_BOT_TOKEN_HERE")
DATA_FILE = "market_data.json"

RESOURCES = {
    "Wheat":          {"base": 14,  "tier": "Common",    "emoji": "🌾"},
    "Corn":           {"base": 18,  "tier": "Common",    "emoji": "🌽"},
    "Coal":           {"base": 26,  "tier": "Common",    "emoji": "⬛"},
    "Wood":           {"base": 38,  "tier": "Common",    "emoji": "🪵"},
    "Flour":          {"base": 45,  "tier": "Common",    "emoji": "🍚"},
    "Carrot":         {"base": 60,  "tier": "Uncommon",  "emoji": "🥕"},
    "Books":          {"base": 80,  "tier": "Uncommon",  "emoji": "📚"},
    "Oil":            {"base": 120, "tier": "Uncommon",  "emoji": "🛢️"},
    "Iron":           {"base": 200, "tier": "Rare",      "emoji": "🔩"},
    "Cement":         {"base": 350, "tier": "Rare",      "emoji": "🏗️"},
    "Gold":           {"base": 600, "tier": "Epic",      "emoji": "🥇"},
    "Coin Bag":       {"base": 900, "tier": "Epic",      "emoji": "💰"},
    "Research":       {"base": 1200,"tier": "Legendary", "emoji": "🔬"},
    "Diamond":        {"base": 1800,"tier": "Legendary", "emoji": "💎"},
    "Uranium Ore":    {"base": 2500,"tier": "Mythic",    "emoji": "☢️"},
    "Stable Uranium": {"base": 4000,"tier": "Mythic",    "emoji": "⚗️"},
    "Data Cube":      {"base": 6000,"tier": "Secret",    "emoji": "🔷"},
    "Dark Matter":    {"base": 10000,"tier":"Secret",    "emoji": "🌑"},
    "Alien Essence":  {"base": 25000,"tier":"Secret",    "emoji": "👽"},
}

FACTORIES = {
    "Wheat Farm":         {"cost": 150,           "output": "Wheat",          "tier": "Common"},
    "Corn Farm":          {"cost": 150,           "output": "Corn",           "tier": "Common"},
    "Coal Cave":          {"cost": 500,           "output": "Coal",           "tier": "Common"},
    "Tree Farm":          {"cost": 1000,          "output": "Wood",           "tier": "Common"},
    "Windmill":           {"cost": 1800,          "output": "Flour",          "tier": "Common"},
    "Carrot Farm":        {"cost": 6500,          "output": "Carrot",         "tier": "Uncommon"},
    "Library":            {"cost": 9000,          "output": "Books",          "tier": "Uncommon"},
    "Oil Rig":            {"cost": 13000,         "output": "Oil",            "tier": "Uncommon"},
    "Wood Plant":         {"cost": 1000,          "output": "Wood (x20)",     "tier": "Common"},
    "Iron Cave":          {"cost": 80000,         "output": "Iron",           "tier": "Rare"},
    "Cement Plant":       {"cost": 180000,        "output": "Cement",         "tier": "Rare"},
    "Gold Cave":          {"cost": 450000,        "output": "Gold",           "tier": "Epic"},
    "Bank":               {"cost": 1000000,       "output": "Coin Bag",       "tier": "Epic"},
    "Research Lab":       {"cost": 5000000,       "output": "Research",       "tier": "Legendary"},
    "Diamond Cave":       {"cost": 7500000,       "output": "Diamond",        "tier": "Legendary"},
    "Uranium Cave":       {"cost": 10000000,      "output": "Uranium Ore",    "tier": "Mythic"},
    "Nuclear Reactor":    {"cost": 20000000,      "output": "Stable Uranium", "tier": "Mythic"},
    "Data Center":        {"cost": 50000000,      "output": "Data Cube",      "tier": "Secret"},
    "Blackhole Generator":{"cost": 1000000000,    "output": "Dark Matter",    "tier": "Secret"},
    "Area 51 Lab":        {"cost": 7500000000,    "output": "Alien Essence",  "tier": "Secret"},
    "Mega Drill":         {"cost": 0,             "output": "Oil (x256)",     "tier": "Special"},
}

MILITARY = {
    "Border Tower":     {"cost": 150,        "rarity": "Common",    "desc": "Cheap watchtower with a pistol guy"},
    "Barracks":         {"cost": 750,        "rarity": "Common",    "desc": "Infantry straight out of basic training"},
    "Sniper Tower":     {"cost": 4000,       "rarity": "Uncommon",  "desc": "Eyes in the sky, bullets from above"},
    "Vehicle Base":     {"cost": 8000,       "rarity": "Uncommon",  "desc": "Light vehicles for fast patrols"},
    "Tank Base":        {"cost": 25000,      "rarity": "Rare",      "desc": "Spawns tanks — tanks are good"},
    "Heli Pad":         {"cost": 140000,     "rarity": "Rare",      "desc": "Chopper support from the skies"},
    "Special Force":    {"cost": 300000,     "rarity": "Epic",      "desc": "Minigun guy included — brrrt"},
    "Missile Hangar":   {"cost": 600000,     "rarity": "Epic",      "desc": "Rockets rolling out, extra firepower"},
    "Hangar":           {"cost": 1200000,    "rarity": "Epic",      "desc": "Warthog airfield, close air support"},
    "Big Tank Base":    {"cost": 2400000,    "rarity": "Legendary", "desc": "Elite tanks"},
    "Big Hanger":       {"cost": 3000000,    "rarity": "Legendary", "desc": "Elite airbase with F35 Fighter Jets"},
    "Missile Launcher": {"cost": 4500000,    "rarity": "Legendary", "desc": "Launches missiles — 250 damage"},
    "Military Hospital":{"cost": 7500000,    "rarity": "Legendary", "desc": "Heals your units"},
    "General's Base":   {"cost": 10000000,   "rarity": "Mythic",    "desc": "B2 bombers on standby"},
    "Air Base":         {"cost": 50000000,   "rarity": "Mythic",    "desc": "Spawns a Black Hawk helicopter"},
    "Artillery Depot":  {"cost": 250000000,  "rarity": "Mythic",    "desc": "Spawns a tank with rockets"},
    "Rocket Bunker":    {"cost": 5000000000, "rarity": "Secret",    "desc": "Spawns THE BEST artillery"},
    "Mech Station":     {"cost": 25000000000,"rarity": "Secret",    "desc": "Futuristic Mechs!"},
}

BLACK_MARKET = {
    "Gem Mine":         {"price": 500,  "desc": "Passive gem income. +15% per owned (max 5000 gems)"},
    "Clone Facility":   {"price": 2000, "desc": "Clone your units. +10% per owned (max 10000 gems)"},
    "Elite Base":       {"price": 3000, "desc": "Advanced base upgrade"},
    "Research Booster": {"price": 1500, "desc": "Speeds up research"},
    "Rocket Pad":       {"price": 2500, "desc": "Advanced military structure"},
    "Worker Statue+":   {"price": 1800, "desc": "20% production speed (2x normal statue)"},
}

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            return json.load(f)
    return {"market": {}, "alerts": {}, "stock": {}}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def pct_bar(pct):
    filled = int((pct + 40) / 80 * 10)
    return "█" * filled + "░" * (10 - filled)

def eff_price(base, pct):
    return int(base * (1 + pct / 100))

def fmt(n):
    if n >= 1_000_000_000: return f"${n/1_000_000_000:.1f}B"
    if n >= 1_000_000: return f"${n/1_000_000:.1f}M"
    if n >= 1_000: return f"${n/1_000:.0f}K"
    return f"${n:,}"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

@tree.command(name="market", description="Show current Mini War market prices")
async def market(interaction: discord.Interaction):
    data = load_data()
    md = data.get("market", {})
    embed = discord.Embed(title="📊 Mini War Market Board", color=0x2f3136, timestamp=datetime.utcnow())
    embed.set_footer(text="Market refreshes every 3 min • /update to report prices")
    if not md:
        embed.description = "No data yet!\nUse `/update <resource> <percent>` to report.\nExample: `/update Wheat 30`"
    else:
        age = int(time.time() - md.get("_updated", time.time()))
        embed.description = f"Last updated: **{age}s ago** by {md.get('_by','someone')}"
        for tier in ["Common","Uncommon","Rare","Epic","Legendary","Mythic","Secret"]:
            lines = []
            for name, info in RESOURCES.items():
                if info["tier"] != tier: continue
                pct = md.get(name, {}).get("pct", None)
                if pct is not None:
                    sign = "+" if pct >= 0 else ""
                    dot = "🟢" if pct > 0 else ("🔴" if pct < 0 else "⚪")
                    lines.append(f"{info['emoji']} **{name}** {dot}`{sign}{pct}%` `{pct_bar(pct)}` **${eff_price(info['base'],pct):,}**")
                else:
                    lines.append(f"{info['emoji']} **{name}** — *not reported*")
            if lines:
                embed.add_field(name=tier, value="\n".join(lines), inline=False)
    await interaction.response.send_message(embed=embed)

@tree.command(name="update", description="Report current market % for a resource")
@app_commands.describe(resource="Resource name", percent="Market percent (-40 to +40)")
async def update_market(interaction: discord.Interaction, resource: str, percent: int):
    matched = next((r for r in RESOURCES if r.lower()==resource.lower()), None)
    if not matched:
        matched = next((r for r in RESOURCES if resource.lower() in r.lower()), None)
    if not matched:
        await interaction.response.send_message(f"❌ Unknown resource. Valid: {', '.join(RESOURCES)}", ephemeral=True); return
    if not -40 <= percent <= 40:
        await interaction.response.send_message("❌ Percent must be -40 to +40.", ephemeral=True); return
    data = load_data()
    data.setdefault("market", {})[matched] = {"pct": percent, "ts": time.time()}
    data["market"]["_updated"] = time.time()
    data["market"]["_by"] = str(interaction.user.display_name)
    save_data(data)
    info = RESOURCES[matched]
    sign = "+" if percent >= 0 else ""
    color = 0x2ecc71 if percent > 0 else (0xe74c3c if percent < 0 else 0x95a5a6)
    embed = discord.Embed(title="📈 Market Updated", color=color)
    embed.add_field(name=f"{info['emoji']} {matched}", value=f"**{sign}{percent}%** `{pct_bar(percent)}`\nPrice: **${eff_price(info['base'],percent):,}** *(base ${info['base']:,})*")
    alerts = data.get("alerts", {})
    pings = [f"<@{uid}>" for uid, uals in alerts.items() for a in uals if a["resource"]==matched and percent>=a["threshold"]]
    if pings:
        embed.add_field(name="🔔 Alert!", value=f"{' '.join(pings)} — {matched} hit {sign}{percent}%!", inline=False)
    await interaction.response.send_message(embed=embed)

@tree.command(name="factories", description="Show all factories and what they produce")
async def factories(interaction: discord.Interaction):
    embed = discord.Embed(title="🏭 Mini War — All Factories", color=0xe67e22,
        description="Buy from Shopkeeper → Factories section")
    tiers = {}
    for name, info in FACTORIES.items():
        tiers.setdefault(info["tier"], []).append(f"**{name}** — `{fmt(info['cost'])}` → {info['output']}")
    for tier in ["Common","Uncommon","Rare","Epic","Legendary","Mythic","Secret","Special"]:
        if tier in tiers:
            embed.add_field(name=tier, value="\n".join(tiers[tier]), inline=False)
    embed.set_footer(text="Mega Drill obtained from Veteran Crate (Daily/Robux)")
    await interaction.response.send_message(embed=embed)

@tree.command(name="military", description="Show all military buildings and costs")
async def military(interaction: discord.Interaction):
    embed = discord.Embed(title="⚔️ Mini War — Military Buildings", color=0xe74c3c)
    rarities = {}
    for name, info in MILITARY.items():
        rarities.setdefault(info["rarity"], []).append(f"**{name}** — `{fmt(info['cost'])}`\n  _{info['desc']}_")
    for r in ["Common","Uncommon","Rare","Epic","Legendary","Mythic","Secret"]:
        if r in rarities:
            embed.add_field(name=r, value="\n".join(rarities[r]), inline=False)
    embed.set_footer(text="Build economy first before rushing military!")
    await interaction.response.send_message(embed=embed)

@tree.command(name="prices", description="Show base sell prices for all resources")
async def prices(interaction: discord.Interaction):
    embed = discord.Embed(title="💰 Mini War — Resource Sell Prices", color=0xf39c12,
        description="Actual sell price = base × (1 + market%). Max market bonus +40%.")
    tiers = {}
    for name, info in RESOURCES.items():
        tiers.setdefault(info["tier"], []).append(f"{info['emoji']} **{name}** `${info['base']:,}`")
    for tier in ["Common","Uncommon","Rare","Epic","Legendary","Mythic","Secret"]:
        if tier in tiers:
            embed.add_field(name=tier, value="\n".join(tiers[tier]), inline=True)
    embed.set_footer(text="Trader upgrade +5% | Financier upgrade +2%")
    await interaction.response.send_message(embed=embed)

@tree.command(name="blackmarket", description="Black Market items and gem tips")
async def black_market(interaction: discord.Interaction):
    embed = discord.Embed(title="🚁 Mini War Black Market", color=0x1abc9c,
        description="Green helicopter lands at helipad near Shopkeeper.\n⏱️ **Every 40 min** | ✅ **Open 20 min**")
    items = "\n".join([f"💎 **{n}** — `{i['price']} Gems`\n  _{i['desc']}_" for n,i in BLACK_MARKET.items()])
    embed.add_field(name="🛒 Items", value=items, inline=False)
    embed.add_field(name="💡 Gem Tips", value="• **Gem Mine** — best first buy, passive gems\n• **Daily Quests** — free gems every day\n• **Shop** — 50💎 for 39 R$, 2000💎 for 799 R$", inline=False)
    await interaction.response.send_message(embed=embed)

@tree.command(name="alert", description="Get pinged when a resource hits a market %")
@app_commands.describe(resource="Resource to watch", threshold="Alert when % reaches this value")
async def set_alert(interaction: discord.Interaction, resource: str, threshold: int):
    matched = next((r for r in RESOURCES if r.lower()==resource.lower()), None)
    if not matched:
        await interaction.response.send_message("❌ Unknown resource.", ephemeral=True); return
    data = load_data()
    uid = str(interaction.user.id)
    data.setdefault("alerts", {}).setdefault(uid, [])
    data["alerts"][uid] = [a for a in data["alerts"][uid] if a["resource"] != matched]
    data["alerts"][uid].append({"resource": matched, "threshold": threshold})
    save_data(data)
    sign = "+" if threshold >= 0 else ""
    await interaction.response.send_message(f"🔔 Alert set! Ping when **{matched}** hits `{sign}{threshold}%`", ephemeral=True)

@tree.command(name="stock", description="Log or view your resource stock")
@app_commands.describe(resource="Resource name (blank to view all)", amount="Amount you have")
async def stock(interaction: discord.Interaction, resource: str = None, amount: int = None):
    data = load_data()
    uid = str(interaction.user.id)
    if resource is None:
        user_stock = data.get("stock", {}).get(uid, {})
        if not user_stock:
            await interaction.response.send_message("No stock logged. Use `/stock <resource> <amount>`", ephemeral=True); return
        embed = discord.Embed(title=f"📦 {interaction.user.display_name}'s Stock", color=0x2ecc71)
        embed.description = "\n".join([f"{RESOURCES.get(r,{}).get('emoji','📦')} **{r}**: `{amt:,}`" for r, amt in user_stock.items()])
        await interaction.response.send_message(embed=embed, ephemeral=True); return
    matched = next((r for r in RESOURCES if r.lower()==resource.lower()), None)
    if not matched:
        await interaction.response.send_message("❌ Unknown resource.", ephemeral=True); return
    data.setdefault("stock", {}).setdefault(uid, {})[matched] = amount
    save_data(data)
    await interaction.response.send_message(f"📦 Logged: **{RESOURCES[matched]['emoji']} {matched}** × `{amount:,}`", ephemeral=True)

@tree.command(name="help", description="Show all bot commands")
async def help_cmd(interaction: discord.Interaction):
    embed = discord.Embed(title="🎮 Mini War Bot — Commands", color=0x5865F2)
    embed.add_field(name="📊 Market", value="`/market` — View prices\n`/update <resource> <pct>` — Report market %\n`/prices` — Base sell prices", inline=False)
    embed.add_field(name="🏭 Factories", value="`/factories` — All factories & outputs", inline=False)
    embed.add_field(name="⚔️ Military", value="`/military` — All military buildings & costs", inline=False)
    embed.add_field(name="📦 Stock", value="`/stock` — View your stock\n`/stock <resource> <amount>` — Log stock", inline=False)
    embed.add_field(name="🔔 Alerts", value="`/alert <resource> <pct>` — Price ping alert", inline=False)
    embed.add_field(name="🚁 Black Market", value="`/blackmarket` — Items & gem tips", inline=False)
    await interaction.response.send_message(embed=embed)

@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ {bot.user} online!")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Mini War 📊"))

bot.run(TOKEN)
