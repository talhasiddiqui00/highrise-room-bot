"""
Highrise Room Management Bot - Main Core Engine (app.py)
Manages Room Controls, Loops, Saves Shared VIP data, and exposes an API endpoint.
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
    # --- IDLES & LOOPS (Slightly adjusted to loop seamlessly) ---
    "rest": {"id": "sit-open", "duration": 14.5}, 
    "zombie": {"id": "idle_zombie", "duration": 25.0},
    "relaxed": {"id": "idle_layingdown2", "duration": 18.0}, 
    "attentive": {"id": "idle_layingdown", "duration": 21.0},
    "sleepy": {"id": "idle-sleep", "duration": 19.0}, 
    "poutyface": {"id": "idle-sad", "duration": 21.0},
    "posh": {"id": "idle-posh", "duration": 18.0}, 
    "tired": {"id": "idle-loop-tired", "duration": 18.5},
    "taploop": {"id": "idle-loop-tapdance", "duration": 4.8}, 
    "sit": {"id": "idle-loop-sitfloor", "duration": 19.0},
    "shy": {"id": "idle-loop-shy", "duration": 13.0}, 
    "bummed": {"id": "idle-loop-sad", "duration": 4.8},
    "chillin": {"id": "idle-loop-happy", "duration": 15.0}, 
    "annoyed": {"id": "idle-loop-annoyed", "duration": 14.0},
    "aerobics": {"id": "idle-loop-aerobics", "duration": 6.8}, 
    "ponder": {"id": "idle-lookup", "duration": 19.0},
    "heropose": {"id": "idle-hero", "duration": 18.0}, 
    "relaxing": {"id": "idle-floorsleeping2", "duration": 14.0},
    "cozynap": {"id": "idle-floorsleeping", "duration": 10.5}, # ✨ No more standing pause
    "enthused": {"id": "idle-enthusiastic", "duration": 12.0},
    "feelthebeat": {"id": "idle-dance-headbobbing", "duration": 22.0}, 
    "irritated": {"id": "idle-angry", "duration": 22.0},

    # --- EMOTES & ACTIONS (Cut tight to prevent snapping to attention) ---
    "fastsing": {"id": "emote-sicklycute-sing-fast", "duration": 8.0}, 
    "slowsing": {"id": "emote-sicklycute-sing-slow", "duration": 8.0},
    "yes": {"id": "emote-yes", "duration": 1.8}, 
    "ibelieveicanfly": {"id": "emote-wings", "duration": 10.8},
    "thewave": {"id": "emote-wave", "duration": 1.9}, 
    "think": {"id": "emote-think", "duration": 2.8},
    "theatrical": {"id": "emote-theatrical", "duration": 7.2}, 
    "tapdance": {"id": "emote-tapdance", "duration": 8.8},
    "superrun": {"id": "emote-superrun", "duration": 5.0}, 
    "superpunch": {"id": "emote-superpunch", "duration": 3.0},
    "sumofight": {"id": "emote-sumo", "duration": 8.5}, 
    "thumbsuck": {"id": "emote-suckthumb", "duration": 3.4},
    "splitsdrop": {"id": "emote-splitsdrop", "duration": 3.7}, 
    "snowballfight": {"id": "emote-snowball", "duration": 4.0},
    "snowangel": {"id": "emote-snowangel", "duration": 5.0}, 
    "handshake": {"id": "emote-secrethandshake", "duration": 3.1},
    "sad": {"id": "emote-sad", "duration": 4.2}, 
    "pull": {"id": "emote-ropepull", "duration": 7.5},
    "roll": {"id": "emote-roll", "duration": 2.8}, 
    "rofl": {"id": "emote-rofl", "duration": 5.0},
    "robot": {"id": "emote-robot", "duration": 6.4}, 
    "rainbow": {"id": "emote-rainbow", "duration": 2.1},
    "proposing": {"id": "emote-proposing", "duration": 3.5}, 
    "peekaboo": {"id": "emote-peekaboo", "duration": 2.9},
    "peace": {"id": "emote-peace", "duration": 4.5}, 
    "panic": {"id": "emote-panic", "duration": 2.1},
    "no": {"id": "emote-no", "duration": 2.0}, 
    "ninjarun": {"id": "emote-ninjarun", "duration": 4.0},
    "nightfever": {"id": "emote-nightfever", "duration": 4.2}, 
    "monsterfail": {"id": "emote-monster_fail", "duration": 3.9},
    "model": {"id": "emote-model", "duration": 5.2}, 
    "levelup": {"id": "emote-levelup", "duration": 4.8},
    "amused": {"id": "emote-laughing2", "duration": 3.8}, 
    "laugh": {"id": "emote-laughing", "duration": 1.9},
    "kiss": {"id": "emote-kiss", "duration": 1.6}, 
    "superkick": {"id": "emote-kicking", "duration": 4.1},
    "jump": {"id": "emote-jumpb", "duration": 2.8}, 
    "judochop": {"id": "emote-judochop", "duration": 1.7},
    "jetpack": {"id": "emote-jetpack", "duration": 14.0}, 
    "hugyourself": {"id": "emote-hugyourself", "duration": 4.2},
    "sweating": {"id": "emote-hot", "duration": 3.6}, 
    "hello": {"id": "emote-hello", "duration": 2.0},
    "harlemshake": {"id": "emote-harlemshake", "duration": 11.2}, 
    "happy": {"id": "emote-happy", "duration": 2.7},
    "handstand": {"id": "emote-handstand", "duration": 3.3}, 
    "greedyemote": {"id": "emoji-greedy", "duration": 3.9},
    "moonwalk": {"id": "emote-gordonshuffle", "duration": 6.8}, 
    "ghostfloat": {"id": "emote-ghost-idle", "duration": 16.5},
    "gangnamstyle": {"id": "emote-gangnam", "duration": 6.0}, 
    "faint": {"id": "emote-fainting", "duration": 15.5},
    "clumsy": {"id": "emote-fail2", "duration": 5.2}, 
    "fall": {"id": "emote-fail1", "duration": 4.4},
    "facepalm": {"id": "emote-exasperatedb", "duration": 2.0}, 
    "exasperated": {"id": "emote-exasperated", "duration": 1.6},
    "elbowbump": {"id": "emote-elbowbump", "duration": 3.0}, 
    "disco": {"id": "emote-disco", "duration": 4.1},
    "blastoff": {"id": "emote-disappear", "duration": 4.9}, 
    "faintdrop": {"id": "emote-deathdrop", "duration": 3.0},
    "collapse": {"id": "emote-death2", "duration": 4.1}, 
    "revival": {"id": "emote-death", "duration": 5.4},
    "dab": {"id": "emote-dab", "duration": 2.0}, 
    "curtsy": {"id": "emote-curtsy", "duration": 1.7},
    "confusion": {"id": "emote-confused", "duration": 7.2}, 
    "cold": {"id": "emote-cold", "duration": 2.9},
    "charging": {"id": "emote-charging", "duration": 6.8}, 
    "bunnyhop": {"id": "emote-bunnyhop", "duration": 10.0},
    "bow": {"id": "bow", "duration": 2.6}, 
    "boo": {"id": "emote-boo", "duration": 3.8},
    "homerun": {"id": "emote-baseball", "duration": 6.0}, 
    "fallingapart": {"id": "emote-apart", "duration": 4.1},

    # --- EMOJIS & SHORT BURSTS ---
    "thumbsup": {"id": "emoji-thumbsup", "duration": 2.0}, 
    "point": {"id": "emoji-there", "duration": 1.3},
    "sneeze": {"id": "emoji-sneeze", "duration": 2.2}, 
    "smirk": {"id": "emoji-smirking", "duration": 4.1},
    "sick": {"id": "emoji-sick", "duration": 3.8}, 
    "gasp": {"id": "emoji-scared", "duration": 2.3},
    "punch": {"id": "emoji-punch", "duration": 1.0}, 
    "pray": {"id": "emoji-pray", "duration": 3.8},
    "stinky": {"id": "emoji-poop", "duration": 4.0}, 
    "naughty": {"id": "emoji-naughty", "duration": 3.5},
    "mindblown": {"id": "emoji-mind-blown", "duration": 1.6}, 
    "lying": {"id": "emoji-lying", "duration": 5.0},
    "levitate": {"id": "emoji-halo", "duration": 4.5}, 
    "fireballlunge": {"id": "emoji-hadoken", "duration": 2.0},
    "giveup": {"id": "emoji-give-up", "duration": 4.2}, 
    "tummyache": {"id": "emoji-gagging", "duration": 4.2},
    "stunned": {"id": "emoji-dizzy", "duration": 3.3}, 
    "sob": {"id": "emoji-crying", "duration": 2.9},
    "clap": {"id": "emoji-clapping", "duration": 1.4}, 
    "raisetheroof": {"id": "emoji-celebrate", "duration": 2.7},
    "arrogance": {"id": "emoji-arrogance", "duration": 5.5}, 
    "angry": {"id": "emoji-angry", "duration": 4.5},

    # --- DANCES (Optimized for fluid floor action) ---
    "voguehands": {"id": "dance-voguehands", "duration": 7.8}, 
    "savagedance": {"id": "dance-tiktok8", "duration": 8.5},
    "dontstartnow": {"id": "dance-tiktok2", "duration": 8.0}, 
    "smoothwalk": {"id": "dance-smoothwalk", "duration": 5.3},
    "ringonit": {"id": "dance-singleladies", "duration": 18.0}, 
    "letsgoshopping": {"id": "dance-shoppingcart", "duration": 3.5},
    "russian": {"id": "dance-russian", "duration": 8.0}, 
    "pennywise": {"id": "dance-pennywise", "duration": 0.9},
    "orangejuicedance": {"id": "dance-orangejustice", "duration": 5.1}, 
    "rockout": {"id": "dance-metal", "duration": 12.0},
    "macarena": {"id": "dance-macarena", "duration": 9.8}, 
    "handsintheair": {"id": "dance-handsup", "duration": 19.0},
    "duckwalk": {"id": "dance-duckwalk", "duration": 9.3}, 
    "kpopdance": {"id": "dance-blackpink", "duration": 5.8},
    "pushups": {"id": "dance-aerobics", "duration": 7.3}, 
    "hyped": {"id": "emote-hyped", "duration": 6.1},
    "jinglebell": {"id": "dance-jinglebell", "duration": 8.7}, 
    "nervous": {"id": "idle-nervous", "duration": 18.5},
    "toilet": {"id": "idle-toilet", "duration": 29.0}, 
    "attention": {"id": "emote-attention", "duration": 3.6},
    "astronaut": {"id": "emote-astronaut", "duration": 11.2}, 
    "dancezombie": {"id": "dance-zombie", "duration": 11.8}
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
        self.bot_status = False
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
        except Exception as e:
            print(f"Error looping emote: {e}")
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
                elif reason == "manual_tip":
                    pass
                await asyncio.sleep(1.2)
            except Exception as e:
                if "closing transport" in str(e).lower() or "connection" in str(e).lower():
                    os._exit(1) # Forces cloud host to instantly restart the bot
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
        """Micro-movement every 5 minutes to prevent Highrise server from flagging bot as idle"""
        while True:
            await asyncio.sleep(300)
            try:
                pos = self.get_bot_position()
                if pos != Position(0,0,0,"FrontRight"):
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
                await asyncio.sleep(60)
            except Exception:
                await asyncio.sleep(10)

    async def on_start(self, session_metadata: SessionMetadata) -> None:
        print("Management Bot Connected")
        self.bot_id = session_metadata.user_id
        self.owner_id = session_metadata.room_info.owner_id
        self.bot_status = True
        await self.place_bot()
        asyncio.create_task(self.process_tip_queue_worker())
        asyncio.create_task(self.track_user_stay_durations_loop())
        asyncio.create_task(self.start_announcement_loop())
        asyncio.create_task(self.connection_watchdog_loop())
        asyncio.create_task(self.anti_idle_loop())

    async def place_bot(self):
        await asyncio.sleep(2.0) # Ensure server is ready before attempting teleport
        try:
            pos = self.get_bot_position()
            if pos != Position(0, 0, 0, 'FrontRight'):
                await self.highrise.teleport(self.bot_id, pos)
        except Exception:
            pass

    async def handle_welcome_flow(self, user: User):
        """Processes the 1-second chat delay and 5-second tip delay"""
        await asyncio.sleep(1.0) # 1 sec delay for chat
        try:
            await self.highrise.chat(f"👋 Welcome to the room @{user.username}! Type '!help' for information.")
        except Exception:
            pass
            
        if user.id not in self.welcome_payouts:
            self.welcome_payouts.append(user.id)
            self.save_database_file()
            await asyncio.sleep(4.0) # 4 more secs = 5 total secs before tip
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
        clean_msg = message.lower().strip()
        is_owner = (user.username.lower() == self.owner_username.lower())
        is_vip = (user.id in self.vip_users)

        # 1. Handle Emote Triggering
        normalized_msg = clean_msg.replace(" ", "")
        if normalized_msg in EMOTE_MAP:
            await self.stop_user_emote(user.id)
            task = asyncio.create_task(self.loop_emote_handler(user.id, EMOTE_MAP[normalized_msg]["id"], EMOTE_MAP[normalized_msg]["duration"]))
            self.active_emote_loops[user.id] = {"task": task, "emote_id": EMOTE_MAP[normalized_msg]["id"]}
            await self.respond(user, f"🎭 Now looping! Type '!stop' to end.", source)
            return

        # 2. Standard Commands
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

        # 3. Owner Economy/Tipping Commands
        if clean_msg.startswith("!giveall "):
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
            return

        elif clean_msg.startswith("!give @"):
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
            return

        # 4. Owner VIP Management Commands
        elif clean_msg.startswith("!givevip @"):
            target_name = clean_msg.split("@")[1].strip()
            room_users = await self.highrise.get_room_users()
            for u, _ in room_users.content:
                if u.username.lower() == target_name:
                    if u.id not in self.vip_users:
                        self.vip_users.append(u.id)
                        self.save_database_file()
                        await self.respond(user, f"✅ @{u.username} has been manually granted VIP status!", source)
                    else:
                        await self.respond(user, f"⚠️ @{u.username} is already a VIP.", source)
                    return
            await self.respond(user, "❌ User not found in the room.", source)
            return

        elif clean_msg.startswith("!removevip @"):
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
            return
            
        elif clean_msg == "!allvips":
            if not self.vip_users:
                await self.highrise.send_whisper(user.id, "No VIPs found in database.")
                return
                
            vip_names = []
            for v_id in self.vip_users:
                # Attempt to get username from tip data, fallback to ID
                name = self.tip_data.get(v_id, {}).get("username", "Unknown User")
                vip_names.append(name)
                
            vip_string = ", ".join(vip_names)
            await self.highrise.send_whisper(user.id, f"💎 Total VIPs ({len(vip_names)}): {vip_string}")
            return

        # 5. Owner Utility Commands
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

        elif clean_msg == "!top":
            sorted_tippers = sorted(self.tip_data.items(), key=lambda x: x[1]['total_tips'], reverse=True)[:10]
            formatted = [f"{i+1}. {d['username']} ({d['total_tips']}g)" for i, (_, d) in enumerate(sorted_tippers)]
            leaderboard_text = "\n".join(formatted)
            await self.respond(user, f"Top Tippers:\n{leaderboard_text}", source)

        elif clean_msg == "!bal":
            try:
                wallet = await self.highrise.get_wallet()
                gold = next((currency.amount for currency in wallet.content if currency.type == 'gold'), 0)
                await self.highrise.send_whisper(user.id, f"💰 Balance: {gold}g")
            except Exception:
                pass

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
