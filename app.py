"""
Highrise Room Management Bot - Main Core Engine (app.py)
With Anti-Duplication Locks, Debouncing, and Initialization Guards.
"""

import os
import sys
import time
import random
import asyncio
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from json import load, dump

from highrise import BaseBot, User, Position, AnchorPosition, SessionMetadata, CurrencyItem, Item
from highrise.__main__ import main, BotDefinition

sys.stdout.reconfigure(line_buffering=True)
os.environ["PYTHONUNBUFFERED"] = "1"

ROOM_ID = "6a28b5b000b6151bd4c9641e"
API_TOKEN = "fd250294097b09a7fd05aa523c63b77ef0b980cc28f7f09742b22d0db30b53a0"
DATA_FILE = "./data.json"

TIP_MAP = {
    "1g": "gold_bar_1", "5g": "gold_bar_5", "10g": "gold_bar_10", 
    "50g": "gold_bar_50", "100g": "gold_bar_100", "500g": "gold_bar_500",
    "1k": "gold_bar_1k", "5k": "gold_bar_5k", "10k": "gold_bar_10k"
}

EMOTE_MAP = {
    "rest": {"id": "sit-open", "duration": 4.5}, 
    "zombie": {"id": "idle_zombie", "duration": 5.0},
    "relaxed": {"id": "idle_layingdown2", "duration": 5.5}, 
    "attentive": {"id": "idle_layingdown", "duration": 6.0},
    "sleepy": {"id": "idle-sleep", "duration": 5.0}, 
    "poutyface": {"id": "idle-sad", "duration": 5.0},
    "posh": {"id": "idle-posh", "duration": 5.0}, 
    "tired": {"id": "idle-loop-tired", "duration": 4.5},
    "taploop": {"id": "idle-loop-tapdance", "duration": 3.5}, 
    "sit": {"id": "idle-loop-sitfloor", "duration": 5.0},
    "shy": {"id": "idle-loop-shy", "duration": 4.0}, 
    "bummed": {"id": "idle-loop-sad", "duration": 3.5},
    "chillin": {"id": "idle-loop-happy", "duration": 4.5}, 
    "annoyed": {"id": "idle-loop-annoyed", "duration": 4.0},
    "aerobics": {"id": "idle-loop-aerobics", "duration": 4.0}, 
    "ponder": {"id": "idle-lookup", "duration": 5.0},
    "heropose": {"id": "idle-hero", "duration": 4.5}, 
    "relaxing": {"id": "idle-floorsleeping2", "duration": 4.0},
    "cozynap": {"id": "idle-floorsleeping", "duration": 3.5}, 
    "enthused": {"id": "idle-enthusiastic", "duration": 4.0},
    "feelthebeat": {"id": "idle-dance-headbobbing", "duration": 5.0}, 
    "irritated": {"id": "idle-angry", "duration": 5.0},
    "fastsing": {"id": "emote-sicklycute-sing-fast", "duration": 4.0}, 
    "slowsing": {"id": "emote-sicklycute-sing-slow", "duration": 4.0},
    "yes": {"id": "emote-yes", "duration": 1.5}, 
    "ibelieveicanfly": {"id": "emote-wings", "duration": 4.5},
    "thewave": {"id": "emote-wave", "duration": 1.5}, 
    "think": {"id": "emote-think", "duration": 2.0},
    "theatrical": {"id": "emote-theatrical", "duration": 4.0}, 
    "tapdance": {"id": "emote-tapdance", "duration": 4.5},
    "superrun": {"id": "emote-superrun", "duration": 3.0}, 
    "superpunch": {"id": "emote-superpunch", "duration": 2.0},
    "sumofight": {"id": "emote-sumo", "duration": 4.0}, 
    "thumbsuck": {"id": "emote-suckthumb", "duration": 2.2},
    "splitsdrop": {"id": "emote-splitsdrop", "duration": 2.5}, 
    "snowballfight": {"id": "emote-snowball", "duration": 2.5},
    "snowangel": {"id": "emote-snowangel", "duration": 3.0}, 
    "handshake": {"id": "emote-secrethandshake", "duration": 2.0},
    "sad": {"id": "emote-sad", "duration": 2.5}, 
    "pull": {"id": "emote-ropepull", "duration": 4.0},
    "roll": {"id": "emote-roll", "duration": 2.0}, 
    "rofl": {"id": "emote-rofl", "duration": 3.0},
    "robot": {"id": "emote-robot", "duration": 4.0}, 
    "rainbow": {"id": "emote-rainbow", "duration": 1.8},
    "proposing": {"id": "emote-proposing", "duration": 2.5}, 
    "peekaboo": {"id": "emote-peekaboo", "duration": 2.0},
    "peace": {"id": "emote-peace", "duration": 2.5}, 
    "panic": {"id": "emote-panic", "duration": 1.5},
    "no": {"id": "emote-no", "duration": 1.5}, 
    "ninjarun": {"id": "emote-ninjarun", "duration": 2.5},
    "nightfever": {"id": "emote-nightfever", "duration": 2.5}, 
    "monsterfail": {"id": "emote-monster_fail", "duration": 2.5},
    "model": {"id": "emote-model", "duration": 3.0}, 
    "levelup": {"id": "emote-levelup", "duration": 3.0},
    "amused": {"id": "emote-laughing2", "duration": 2.5}, 
    "laugh": {"id": "emote-laughing", "duration": 1.5},
    "kiss": {"id": "emote-kiss", "duration": 1.2}, 
    "superkick": {"id": "emote-kicking", "duration": 2.5},
    "jump": {"id": "emote-jumpb", "duration": 2.0}, 
    "judochop": {"id": "emote-judochop", "duration": 1.2},
    "jetpack": {"id": "emote-jetpack", "duration": 5.0}, 
    "hugyourself": {"id": "emote-hugyourself", "duration": 2.5},
    "sweating": {"id": "emote-hot", "duration": 2.2}, 
    "hello": {"id": "emote-hello", "duration": 1.5},
    "harlemshake": {"id": "emote-harlemshake", "duration": 5.0}, 
    "happy": {"id": "emote-happy", "duration": 1.8},
    "handstand": {"id": "emote-handstand", "duration": 2.2}, 
    "greedyemote": {"id": "emote-greedy", "duration": 2.5},
    "moonwalk": {"id": "emote-gordonshuffle", "duration": 3.5}, 
    "ghostfloat": {"id": "emote-ghost-idle", "duration": 5.0},
    "gangnamstyle": {"id": "emote-gangnam", "duration": 3.5}, 
    "faint": {"id": "emote-fainting", "duration": 5.0},
    "clumsy": {"id": "emote-fail2", "duration": 3.0}, 
    "fall": {"id": "emote-fail1", "duration": 2.5},
    "facepalm": {"id": "emote-exasperatedb", "duration": 1.5}, 
    "exasperated": {"id": "emote-exasperated", "duration": 1.2},
    "elbowbump": {"id": "emote-elbowbump", "duration": 2.0}, 
    "disco": {"id": "emote-disco", "duration": 2.5},
    "blastoff": {"id": "emote-disappear", "duration": 3.0}, 
    "faintdrop": {"id": "emote-deathdrop", "duration": 2.0},
    "collapse": {"id": "emote-death2", "duration": 2.5}, 
    "revival": {"id": "emote-death", "duration": 3.0},
    "dab": {"id": "emote-dab", "duration": 1.5}, 
    "curtsy": {"id": "emote-curtsy", "duration": 1.2},
    "confusion": {"id": "emote-confused", "duration": 4.0}, 
    "cold": {"id": "emote-cold", "duration": 2.0},
    "charging": {"id": "emote-charging", "duration": 3.5}, 
    "bunnyhop": {"id": "emote-bunnyhop", "duration": 4.5},
    "bow": {"id": "emote-bow", "duration": 1.8}, 
    "boo": {"id": "emote-boo", "duration": 2.2},
    "homerun": {"id": "emote-baseball", "duration": 3.0}, 
    "fallingapart": {"id": "emote-apart", "duration": 2.5},
    "thumbsup": {"id": "emoji-thumbsup", "duration": 1.5}, 
    "point": {"id": "emoji-there", "duration": 1.0},
    "sneeze": {"id": "emoji-sneeze", "duration": 1.5}, 
    "smirk": {"id": "emoji-smirking", "duration": 2.5},
    "sick": {"id": "emoji-sick", "duration": 2.5}, 
    "gasp": {"id": "emoji-scared", "duration": 1.5},
    "punch": {"id": "emoji-punch", "duration": 0.8}, 
    "pray": {"id": "emoji-pray", "duration": 2.5},
    "stinky": {"id": "emoji-poop", "duration": 2.5}, 
    "naughty": {"id": "emoji-naughty", "duration": 2.2},
    "mindblown": {"id": "emoji-mind-blown", "duration": 1.2}, 
    "lying": {"id": "emoji-lying", "duration": 3.0},
    "levitate": {"id": "emoji-halo", "duration": 2.8}, 
    "fireballlunge": {"id": "emoji-hadoken", "duration": 1.5},
    "giveup": {"id": "emoji-give-up", "duration": 2.5}, 
    "tummyache": {"id": "emoji-gagging", "duration": 2.5},
    "stunned": {"id": "emoji-dizzy", "duration": 2.0}, 
    "sob": {"id": "emoji-crying", "duration": 1.8},
    "clap": {"id": "emoji-clapping", "duration": 1.0}, 
    "raisetheroof": {"id": "emoji-celebrate", "duration": 1.8},
    "arrogance": {"id": "emoji-arrogance", "duration": 3.0}, 
    "angry": {"id": "emoji-angry", "duration": 2.5},
    "voguehands": {"id": "dance-voguehands", "duration": 4.0}, 
    "savagedance": {"id": "dance-tiktok8", "duration": 4.5},
    "dontstartnow": {"id": "dance-tiktok2", "duration": 4.0}, 
    "smoothwalk": {"id": "dance-smoothwalk", "duration": 3.0},
    "ringonit": {"id": "dance-singleladies", "duration": 5.0}, 
    "letsgoshopping": {"id": "dance-shoppingcart", "duration": 2.0},
    "russian": {"id": "dance-russian", "duration": 4.0}, 
    "pennywise": {"id": "dance-pennywise", "duration": 0.8},
    "orangejuicedance": {"id": "dance-orangejustice", "duration": 3.0}, 
    "rockout": {"id": "dance-metal", "duration": 5.0},
    "macarena": {"id": "dance-macarena", "duration": 5.0}, 
    "handsintheair": {"id": "dance-handsup", "duration": 5.0},
    "duckwalk": {"id": "dance-duckwalk", "duration": 4.5}, 
    "kpopdance": {"id": "dance-blackpink", "duration": 3.5},
    "pushups": {"id": "dance-aerobics", "duration": 4.0}, 
    "hyped": {"id": "emote-hyped", "duration": 3.5},
    "jinglebell": {"id": "dance-jinglebell", "duration": 4.5}, 
    "nervous": {"id": "idle-nervous", "duration": 5.0},
    "toilet": {"id": "idle-toilet", "duration": 6.0}, 
    "attention": {"id": "emote-attention", "duration": 2.0},
    "astronaut": {"id": "emote-astronaut", "duration": 4.5}, 
    "dancezombie": {"id": "dance-zombie", "duration": 4.5}
}

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/get_vips":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            vips = Bot.instance.vip_users if Bot.instance else []
            self.wfile.write(json.dumps({"vip_users": vips}).encode())
        else:
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Bot Engine Live")
            
    def log_message(self, format, *args):
        return

class Bot(BaseBot):
    instance = None

    def __init__(self):
        super().__init__()
        Bot.instance = self
        self.bot_id = None
        self.owner_id = None
        self.owner_username = "sadi_key"
        
        # --- LOCKS TO PREVENT DUPLICATION ---
        self.is_initialized = False 
        self.last_command_time = {} 
        self.announcement_task = None 
        # ------------------------------------

        self.tip_data = {}
        self.vip_users = []
        self.welcome_payouts = []
        
        self.load_database_file()

        self.vip_spawn_points = [
            Position(26.75, 23.0, 23.35, facing="FrontRight"),
            Position(19.00070, 23.0, 33.99, facing="FrontRight"),
            Position(27.5, 23.0, 30.0, facing="FrontRight")
        ]
        self.ground_spawn_position = Position(27.0, 0.5, 34.0, facing="FrontRight")

        self.active_emote_loops = {}
        self.tip_queue = asyncio.Queue()
        self.room_stay_tracker = {}

    def load_database_file(self) -> None:
        if not os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "w") as file:
                    dump({"users": {}, "vip_users": [], "welcome_payouts": [], "bot_position": {"x": 0, "y": 0, "z": 0, "facing": "FrontRight"}}, file)
            except Exception as e:
                print(f"[MEMORY ERROR] Initialization failed: {e}")
                return

        try:
            with open(DATA_FILE, "r") as file:
                data = load(file)
                self.tip_data = data.get("users", {})
                self.vip_users = data.get("vip_users", [])
                self.welcome_payouts = data.get("welcome_payouts", [])
                print(f"[MEMORY LOG] Loaded Brain. Tippers={len(self.tip_data)}, VIPs={len(self.vip_users)}")
        except Exception as e:
            print(f"[MEMORY ERROR] Read failed: {e}")

    def save_database_file(self) -> None:
        try:
            data = {}
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, "r") as file:
                    try:
                        data = load(file)
                    except Exception:
                        data = {}

            data["users"] = self.tip_data
            data["vip_users"] = self.vip_users
            data["welcome_payouts"] = self.welcome_payouts

            with open(DATA_FILE, "w") as file:
                dump(data, file, indent=4)
        except Exception as e:
            print(f"[MEMORY ERROR] Write failed: {e}")

    def get_bot_position(self) -> Position:
        try:
            with open(DATA_FILE, "r") as file:
                data = load(file)
                pos_data = data.get("bot_position", {"x": 0, "y": 0, "z": 0, "facing": "FrontRight"})
                return Position(pos_data["x"], pos_data["y"], pos_data["z"], pos_data["facing"])
        except Exception:
            return Position(0, 0, 0, "FrontRight")

    async def loop_emote_handler(self, user_id: str, emote_id: str, duration: float) -> None:
        try:
            while True:
                if user_id not in self.active_emote_loops or self.active_emote_loops[user_id]["emote_id"] != emote_id:
                    break
                await self.highrise.send_emote(emote_id, user_id)
                await asyncio.sleep(duration)
        except asyncio.CancelledError:
            pass
        except Exception:
            pass
        finally:
            if user_id in self.active_emote_loops and self.active_emote_loops[user_id]["emote_id"] == emote_id:
                del self.active_emote_loops[user_id]

    async def stop_user_emote(self, user_id: str) -> None:
        if user_id in self.active_emote_loops:
            task = self.active_emote_loops[user_id]["task"]
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            if user_id in self.active_emote_loops:
                del self.active_emote_loops[user_id]

    async def process_tip_queue_worker(self):
        while True:
            target_id, gold_bar_tier, username, reason = await self.tip_queue.get()
            try:
                await self.highrise.tip_user(target_id, gold_bar_tier)
                if reason == "welcome":
                    await self.highrise.chat(f"🎉 @{username}, enjoy your 1g welcome bonus!")
                elif reason == "stay_reward":
                    await self.highrise.chat(f"⏰ @{username} received 1g for supporting the room with their stay-time! 🎉")
                await asyncio.sleep(1.2)
            except Exception as e:
                if "closing transport" in str(e).lower() or "connection" in str(e).lower():
                    os._exit(1)
                await asyncio.sleep(2.0)
            finally:
                self.tip_queue.task_done()

    async def track_user_stay_durations_loop(self):
        while True:
            await asyncio.sleep(30)
            now = time.time()
            for user_id, data in list(self.room_stay_tracker.items()):
                elapsed_minutes = (now - data["join_time"]) / 60.0
                if not data["hit_30m"] and elapsed_minutes >= 30.0:
                    self.room_stay_tracker[user_id]["hit_30m"] = True
                    self.room_stay_tracker[user_id]["next_milestone_minutes"] = 90.0
                    await self.tip_queue.put((user_id, "gold_bar_1", data["username"], "stay_reward"))
                elif data["hit_30m"] and elapsed_minutes >= data["next_milestone_minutes"]:
                    self.room_stay_tracker[user_id]["next_milestone_minutes"] += 60.0
                    await self.tip_queue.put((user_id, "gold_bar_1", data["username"], "stay_reward"))

    async def connection_watchdog_loop(self) -> None:
        while True:
            await asyncio.sleep(45)
            try:
                await self.highrise.get_wallet()
            except Exception as e:
                if "closing transport" in str(e).lower() or "timeout" in str(e).lower():
                    os._exit(1)

    async def anti_idle_loop(self):
        while True:
            await asyncio.sleep(300)
            try:
                pos = self.get_bot_position()
                if pos.x != 0 or pos.y != 0 or pos.z != 0:
                    await self.highrise.walk_to(Position(pos.x + 0.05, pos.y, pos.z + 0.05, pos.facing))
                    await asyncio.sleep(1)
                    await self.highrise.teleport(self.bot_id, pos)
            except Exception:
                pass

    async def start_announcement_loop(self) -> None:
        announcements = [
            "✨ <color=#FF0000><b>Welcome!</b></color> Tip <color=#FFD700><b>500g+</b></color> to the Bot for permanent VIP access! 💎👑",
            "💡 <color=#00FF00><b>Need help?</b></color> Type <color=#00FFFF><b>!help</b></color> for commands and <color=#FF00FF><b>!list</b></color> for emotes! 🎭",
            "🎶 <color=#0000FF><b>Having fun?</b></color> Just type an emote name (like <color=#FFA500><b>cozy nap</b></color>) to start looping! 🕺💃"
        ]
        while True:
            try:
                room_users = await self.highrise.get_room_users()
                if room_users and len(room_users.content) > 1:
                    await self.highrise.chat(random.choice(announcements))
                await asyncio.sleep(90) # Announcements every 90 seconds
            except Exception:
                await asyncio.sleep(10)

    async def on_start(self, session_metadata: SessionMetadata) -> None:
        # Prevent SDK reconnects from duplicating background tasks
        if self.is_initialized:
            return
            
        print("Management Bot Connected")
        self.bot_id = session_metadata.user_id
        self.owner_id = session_metadata.room_info.owner_id
        self.is_initialized = True
        
        await self.place_bot()
        
        asyncio.create_task(self.process_tip_queue_worker())
        asyncio.create_task(self.track_user_stay_durations_loop())
        asyncio.create_task(self.connection_watchdog_loop())
        asyncio.create_task(self.anti_idle_loop())
        
        # Start announcement loop safely
        if self.announcement_task is None or self.announcement_task.done():
            self.announcement_task = asyncio.create_task(self.start_announcement_loop())

    async def place_bot(self):
        await asyncio.sleep(2.0)
        try:
            pos = self.get_bot_position()
            if pos != Position(0, 0, 0, 'FrontRight'):
                await self.highrise.teleport(self.bot_id, pos)
        except Exception:
            pass

    async def handle_welcome_flow(self, user: User):
        await asyncio.sleep(1.0)
        try:
            await self.highrise.chat(f"👋 Welcome to the room @{user.username}! Type '!help' for information.")
        except Exception:
            pass
            
        if user.id not in self.welcome_payouts:
            self.welcome_payouts.append(user.id)
            self.save_database_file()
            await asyncio.sleep(4.0) 
            await self.tip_queue.put((user.id, "gold_bar_1", user.username, "welcome"))

    async def on_user_join(self, user: User, position: Position | AnchorPosition) -> None:
        if user.id == self.bot_id or "bot" in user.username.lower():
            return
        self.room_stay_tracker[user.id] = {"username": user.username, "join_time": time.time(), "hit_30m": False, "next_milestone_minutes": 30.0}
        asyncio.create_task(self.handle_welcome_flow(user))

    async def on_user_leave(self, user: User) -> None:
        await self.stop_user_emote(user.id)
        if user.id in self.room_stay_tracker:
            del self.room_stay_tracker[user.id]

    async def on_tip(self, sender: User, receiver: User, tip: CurrencyItem | Item) -> None:
        if sender.id == self.bot_id:
            return
        if isinstance(tip, CurrencyItem) and receiver.id == self.bot_id:
            if sender.id not in self.tip_data:
                self.tip_data[sender.id] = {"username": sender.username, "total_tips": 0}
            self.tip_data[sender.id]['total_tips'] += tip.amount
            if tip.amount >= 500:
                if sender.id not in self.vip_users:
                    self.vip_users.append(sender.id)
                await self.highrise.chat(f"👑 VIP PROMOTION: @{sender.username} has unlocked Lifetime VIP permissions! 🎉")
            else:
                await self.highrise.chat(f"Thank you {sender.username} for tipping {tip.amount}g!")
            self.save_database_file()

    async def on_chat(self, user: User, message: str) -> None:
        await self.command_handler(user, message, "chat")

    async def on_whisper(self, user: User, message: str) -> None:
        await self.command_handler(user, message, "whisper")

    async def command_handler(self, user: User, message: str, source: str):
        # 1. Reject empty messages
        if not message or not message.strip():
            return

        clean_msg = message.lower().strip()
        
        # 2. DEBOUNCE LOCK: Prevent identical commands within 1.5 seconds
        now = time.time()
        user_history = self.last_command_time.get(user.id, {})
        last_time = user_history.get(clean_msg, 0)
        
        if now - last_time < 1.5:
            return # Block duplicate from double-firing events
            
        user_history[clean_msg] = now
        self.last_command_time[user.id] = user_history

        is_owner = (user.username.lower() == self.owner_username.lower())
        is_vip = (user.id in self.vip_users)

        # 3. Handle Emote Triggering
        normalized_msg = clean_msg.replace(" ", "")
        if normalized_msg in EMOTE_MAP:
            await self.stop_user_emote(user.id)
            task = asyncio.create_task(self.loop_emote_handler(user.id, EMOTE_MAP[normalized_msg]["id"], EMOTE_MAP[normalized_msg]["duration"]))
            self.active_emote_loops[user.id] = {"task": task, "emote_id": EMOTE_MAP[normalized_msg]["id"]}
            await self.respond(user, f"🎭 Now looping! Type '!stop' to end.", source)
            return

        # 4. Standard Commands
        if clean_msg == "!help":
            help_text = "⚡ Commands: !list | !stop | !vip | !down"
            if is_owner:
                help_text += " | !set | !top | !bal | !allvips | !giveall | !give | !givevip | !removevip"
            await self.respond(user, help_text, source)
            return

        elif clean_msg == "!list":
            await self.highrise.send_whisper(user.id, "💡 Just type any of these names in chat to loop the emote! Type '!stop' to cancel.")
            emotes = list(EMOTE_MAP.keys())
            current_msg = ""
            for e in emotes:
                if len(current_msg) + len(e) + 2 > 200:
                    await self.highrise.send_whisper(user.id, current_msg)
                    current_msg = e + ", "
                else:
                    current_msg += e + ", "
            if current_msg:
                await self.highrise.send_whisper(user.id, current_msg.rstrip(", "))
            return

        elif clean_msg == "!stop":
            await self.stop_user_emote(user.id)
            return
            
        elif clean_msg == "!vip" and (is_vip or is_owner):
            try:
                await self.highrise.teleport(user.id, random.choice(self.vip_spawn_points))
            except Exception:
                pass
            return
            
        elif clean_msg == "!down" and (is_vip or is_owner):
            try:
                await self.highrise.teleport(user.id, self.ground_spawn_position)
            except Exception:
                pass
            return

        # --- EVERYTHING BELOW THIS LINE IS OWNER ONLY ---
        if not is_owner:
            return

        if clean_msg.startswith("!giveall "):
            try:
                amount_str = clean_msg.split(" ")[1].strip()
                if amount_str in TIP_MAP:
                    room_users = await self.highrise.get_room_users()
                    count = 0
                    for u, _ in room_users.content:
                        if u.id != self.bot_id:
                            await self.tip_queue.put((u.id, TIP_MAP[amount_str], u.username, "manual_tip"))
                            count += 1
                    await self.respond(user, f"💸 Queued {amount_str} tip to {count} users in the room!", source)
                else:
                    await self.respond(user, "❌ Invalid amount. Use 1g, 5g, 10g, 50g, 100g, 500g, 1k, 5k, or 10k.", source)
            except IndexError:
                await self.respond(user, "❌ Invalid format. Use: !giveall 10g", source)
            return

        elif clean_msg.startswith("!give "):
            parts = clean_msg.split()
            if len(parts) >= 3:
                target_name = parts[1].replace("@", "")
                amount_str = parts[2]
                if amount_str in TIP_MAP:
                    room_users = await self.highrise.get_room_users()
                    for u, _ in room_users.content:
                        if u.username.lower() == target_name:
                            await self.tip_queue.put((u.id, TIP_MAP[amount_str], u.username, "manual_tip"))
                            await self.respond(user, f"💸 Queued {amount_str} tip to @{u.username}", source)
                            return
                    await self.respond(user, "❌ User not found in the room.", source)
                else:
                    await self.respond(user, "❌ Invalid amount. Use 1g, 5g, 10g, 50g, 100g, 500g, 1k, 5k, or 10k.", source)
            else:
                await self.respond(user, "❌ Invalid format. Use: !give @username 10g", source)
            return

        elif clean_msg.startswith("!givevip "):
            try:
                target_name = clean_msg.split("@")[1].strip()
                room_users = await self.highrise.get_room_users()
                for u, _ in room_users.content:
                    if u.username.lower() == target_name:
                        if u.id not in self.vip_users:
                            self.vip_users.append(u.id)
                            if u.id not in self.tip_data:
                                self.tip_data[u.id] = {"username": u.username, "total_tips": 0}
                            self.save_database_file()
                            await self.respond(user, f"✅ @{u.username} has been manually granted VIP status!", source)
                        else:
                            await self.respond(user, f"⚠️ @{u.username} is already a VIP.", source)
                        return
                await self.respond(user, "❌ User not found in the room.", source)
            except IndexError:
                await self.respond(user, "❌ Invalid format. Use: !givevip @username", source)
            return

        elif clean_msg.startswith("!removevip "):
            try:
                target_name = clean_msg.split("@")[1].strip()
                room_users = await self.highrise.get_room_users()
                for u, _ in room_users.content:
                    if u.username.lower() == target_name:
                        if u.id in self.vip_users:
                            self.vip_users.remove(u.id)
                            self.save_database_file()
                            await self.respond(user, f"🚫 @{u.username} has had their VIP status revoked.", source)
                        else:
                            await self.respond(user, f"⚠️ @{u.username} is not a VIP.", source)
                        return
                await self.respond(user, "❌ User not found in the room.", source)
            except IndexError:
                await self.respond(user, "❌ Invalid format. Use: !removevip @username", source)
            return
            
        elif clean_msg == "!allvips":
            if not self.vip_users:
                await self.highrise.send_whisper(user.id, "No VIPs found in database.")
                return
                
            vip_names = []
            for v_id in self.vip_users:
                name = self.tip_data.get(v_id, {}).get("username", "Unknown User")
                vip_names.append(name)
                
            vip_string = ", ".join(vip_names)
            await self.highrise.send_whisper(user.id, f"💎 Total VIPs ({len(vip_names)}): {vip_string}")
            return

        elif clean_msg == "!set":
            try:
                room_users = await self.highrise.get_room_users()
                position = None
                for u, pos in room_users.content:
                    if u.id == user.id:
                        position = pos
                        break
                
                if isinstance(position, Position):
                    data = {}
                    if os.path.exists(DATA_FILE):
                        with open(DATA_FILE, "r") as file:
                            try: data = load(file)
                            except Exception: data = {}
                    
                    data["bot_position"] = {"x": position.x, "y": position.y, "z": position.z, "facing": position.facing}
                    with open(DATA_FILE, "w") as file:
                        dump(data, file, indent=4)
                        
                    await self.highrise.teleport(self.bot_id, position)
                    await self.respond(user, "📍 Bot position updated successfully!", source)
            except Exception as e:
                print(f"Error handling !set: {e}")
            return

        elif clean_msg == "!top":
            sorted_tippers = sorted(self.tip_data.items(), key=lambda x: x[1]['total_tips'], reverse=True)[:10]
            formatted = [f"{i+1}. {d['username']} ({d['total_tips']}g)" for i, (_, d) in enumerate(sorted_tippers)]
            leaderboard_text = "\n".join(formatted)
            await self.respond(user, f"Top Tippers:\n{leaderboard_text}", source)
            return

        elif clean_msg == "!bal":
            try:
                wallet = await self.highrise.get_wallet()
                gold = next((currency.amount for currency in wallet.content if currency.type == 'gold'), 0)
                await self.highrise.send_whisper(user.id, f"💰 Balance: {gold}g")
            except Exception:
                pass
            return

    async def respond(self, user: User, msg: str, source: str):
        if source == "chat":
            await self.highrise.chat(msg)
        elif source == "whisper":
            await self.highrise.send_whisper(user.id, msg)

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

if __name__ == "__main__":
    web_worker = threading.Thread(target=run_web_server, daemon=True)
    web_worker.start()
    asyncio.run(main([BotDefinition(Bot(), ROOM_ID, API_TOKEN)]))
