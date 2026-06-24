"""
Highrise Room Management Bot - Unified JSON Storage Engine
Includes: Role-Based Help, Refreshed Announcements, and YouTube Link DJ Engine
"""

import os
import sys
import time
import random
import asyncio
from typing import Union, Dict, Any, List
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
from json import load, dump

from highrise import BaseBot, User, Position, AnchorPosition, SessionMetadata, CurrencyItem, Item
from highrise.__main__ import main, BotDefinition
from youtube_search import YoutubeSearch

# Ensure terminal printing prints live logs immediately without buffering drops
sys.stdout.reconfigure(line_buffering=True)
os.environ["PYTHONUNBUFFERED"] = "1"

# CONFIGURATION VARIABLES
ROOM_ID = "6a28b5b000b6151bd4c9641e"
API_TOKEN = "fd250294097b09a7fd05aa523c63b77ef0b980cc28f7f09742b22d0db30b53a0"
DATA_FILE = "./data.json"

EMOTE_MAP = {
    "rest": {"id": "sit-open", "duration": 17.0}, "zombie": {"id": "idle_zombie", "duration": 28.0},
    "relaxed": {"id": "idle_layingdown2", "duration": 21.0}, "attentive": {"id": "idle_layingdown", "duration": 24.0},
    "sleepy": {"id": "idle-sleep", "duration": 22.0}, "poutyface": {"id": "idle-sad", "duration": 24.0},
    "posh": {"id": "idle-posh", "duration": 21.0}, "tired": {"id": "idle-loop-tired", "duration": 21.0},
    "taploop": {"id": "idle-loop-tapdance", "duration": 6.0}, "sit": {"id": "idle-loop-sitfloor", "duration": 22.0},
    "shy": {"id": "idle-loop-shy", "duration": 16.0}, "bummed": {"id": "idle-loop-sad", "duration": 6.0},
    "chillin": {"id": "idle-loop-happy", "duration": 18.0}, "annoyed": {"id": "idle-loop-annoyed", "duration": 17.0},
    "aerobics": {"id": "idle-loop-aerobics", "duration": 8.0}, "ponder": {"id": "idle-lookup", "duration": 22.0},
    "heropose": {"id": "idle-hero", "duration": 21.0}, "relaxing": {"id": "idle-floorsleeping2", "duration": 17.0},
    "cozynap": {"id": "idle-floorsleeping", "duration": 13.0}, "enthused": {"id": "idle-enthusiastic", "duration": 15.0},
    "feelthebeat": {"id": "idle-dance-headbobbing", "duration": 25.0}, "irritated": {"id": "idle-angry", "duration": 25.0},
    "fastsing": {"id": "emote-sicklycute-sing-fast", "duration": 10.0}, "slowsing": {"id": "emote-sicklycute-sing-slow", "duration": 10.0},
    "yes": {"id": "emote-yes", "duration": 2.5}, "ibelieveicanfly": {"id": "emote-wings", "duration": 13.0},
    "thewave": {"id": "emote-wave", "duration": 2.6}, "think": {"id": "emote-think", "duration": 3.6},
    "theatrical": {"id": "emote-theatrical", "duration": 8.5}, "tapdance": {"id": "emote-tapdance", "duration": 11.0},
    "superrun": {"id": "emote-superrun", "duration": 6.2}, "superpunch": {"id": "emote-superpunch", "duration": 3.7},
    "sumofight": {"id": "emote-sumo", "duration": 10.8}, "thumbsuck": {"id": "emote-suckthumb", "duration": 4.1},
    "splitsdrop": {"id": "emote-splitsdrop", "duration": 4.4}, "snowballfight": {"id": "emote-snowball", "duration": 5.2},
    "snowangel": {"id": "emote-snowangel", "duration": 6.2}, "handshake": {"id": "emote-secrethandshake", "duration": 3.8},
    "sad": {"id": "emote-sad", "duration": 5.4}, "pull": {"id": "emote-ropepull", "duration": 8.7},
    "roll": {"id": "emote-roll", "duration": 3.5}, "rofl": {"id": "emote-rofl", "duration": 6.3},
    "robot": {"id": "emote-robot", "duration": 7.6}, "rainbow": {"id": "emote-rainbow", "duration": 2.8},
    "proposing": {"id": "emote-proposing", "duration": 4.2}, "peekaboo": {"id": "emote-peekaboo", "duration": 3.6},
    "peace": {"id": "emote-peace", "duration": 5.7}, "panic": {"id": "emote-panic", "duration": 2.8},
    "no": {"id": "emote-no", "duration": 2.7}, "ninjarun": {"id": "emote-ninjarun", "duration": 4.7},
    "nightfever": {"id": "emote-nightfever", "duration": 5.4}, "monsterfail": {"id": "emote-monster_fail", "duration": 4.6},
    "model": {"id": "emote-model", "duration": 6.4}, "levelup": {"id": "emote-levelup", "duration": 6.0},
    "amused": {"id": "emote-laughing2", "duration": 5.0}, "laugh": {"id": "emote-laughing", "duration": 2.6},
    "kiss": {"id": "emote-kiss", "duration": 2.3}, "superkick": {"id": "emote-kicking", "duration": 4.8},
    "jump": {"id": "emote-jumpb", "duration": 3.5}, "judochop": {"id": "emote-judochop", "duration": 2.4},
    "jetpack": {"id": "emote-jetpack", "duration": 16.7}, "hugyourself": {"id": "emote-hugyourself", "duration": 4.9},
    "sweating": {"id": "emote-hot", "duration": 4.3}, "hello": {"id": "emote-hello", "duration": 2.7},
    "harlemshake": {"id": "emote-harlemshake", "duration": 13.5}, "happy": {"id": "emote-happy", "duration": 3.4},
    "handstand": {"id": "emote-handstand", "duration": 4.0}, "greedyemote": {"id": "emoji-greedy", "duration": 4.6},
    "moonwalk": {"id": "emote-gordonshuffle", "duration": 8.0}, "ghostfloat": {"id": "emote-ghost-idle", "duration": 19.5},
    "gangnamstyle": {"id": "emote-gangnam", "duration": 7.2}, "faint": {"id": "emote-fainting", "duration": 18.4},
    "clumsy": {"id": "emote-fail2", "duration": 6.4}, "fall": {"id": "emote-fail1", "duration": 5.6},
    "facepalm": {"id": "emote-exasperatedb", "duration": 2.7}, "exasperated": {"id": "emote-exasperated", "duration": 2.3},
    "elbowbump": {"id": "emote-elbowbump", "duration": 3.7}, "disco": {"id": "emote-disco", "duration": 5.3},
    "blastoff": {"id": "emote-disappear", "duration": 6.1}, "faintdrop": {"id": "emote-deathdrop", "duration": 3.7},
    "collapse": {"id": "emote-death2", "duration": 4.8}, "revival": {"id": "emote-death", "duration": 6.6},
    "dab": {"id": "emote-dab", "duration": 2.7}, "curtsy": {"id": "emote-curtsy", "duration": 2.4},
    "confusion": {"id": "emote-confused", "duration": 8.5}, "cold": {"id": "emote-cold", "duration": 3.6},
    "charging": {"id": "emote-charging", "duration": 8.0}, "bunnyhop": {"id": "emote-bunnyhop", "duration": 12.3},
    "bow": {"id": "bow", "duration": 3.3}, "boo": {"id": "emote-boo", "duration": 4.5},
    "homerun": {"id": "emote-baseball", "duration": 7.2}, "fallingapart": {"id": "emote-apart", "duration": 4.8},
    "thumbsup": {"id": "emoji-thumbsup", "duration": 2.7}, "point": {"id": "emoji-there", "duration": 2.0},
    "sneeze": {"id": "emoji-sneeze", "duration": 2.9}, "smirk": {"id": "emoji-smirking", "duration": 4.8},
    "sick": {"id": "emoji-sick", "duration": 5.0}, "gasp": {"id": "emoji-scared", "duration": 3.0},
    "punch": {"id": "emoji-punch", "duration": 1.7}, "pray": {"id": "emoji-pray", "duration": 4.5},
    "stinky": {"id": "emoji-poop", "duration": 4.7}, "naughty": {"id": "emoji-naughty", "duration": 4.2},
    "mindblown": {"id": "emoji-mind-blown", "duration": 2.3}, "lying": {"id": "emoji-lying", "duration": 6.3},
    "levitate": {"id": "emoji-halo", "duration": 5.8}, "fireballlunge": {"id": "emoji-hadoken", "duration": 2.7},
    "giveup": {"id": "emoji-give-up", "duration": 5.4}, "tummyache": {"id": "emoji-gagging", "duration": 5.5},
    "stunned": {"id": "emoji-dizzy", "duration": 4.0}, "sob": {"id": "emoji-crying", "duration": 3.6},
    "clap": {"id": "emoji-clapping", "duration": 2.1}, "raisetheroof": {"id": "emoji-celebrate", "duration": 3.4},
    "arrogance": {"id": "emoji-arrogance", "duration": 6.8}, "angry": {"id": "emoji-angry", "duration": 5.7},
    "voguehands": {"id": "dance-voguehands", "duration": 9.1}, "savagedance": {"id": "dance-tiktok8", "duration": 10.9},
    "dontstartnow": {"id": "dance-tiktok2", "duration": 10.3}, "smoothwalk": {"id": "dance-smoothwalk", "duration": 6.6},
    "ringonit": {"id": "dance-singleladies", "duration": 21.1}, "letsgoshopping": {"id": "dance-shoppingcart", "duration": 4.3},
    "russian": {"id": "dance-russian", "duration": 10.2}, "pennywise": {"id": "dance-pennywise", "duration": 1.2},
    "orangejuicedance": {"id": "dance-orangejustice", "duration": 6.4}, "rockout": {"id": "dance-metal", "duration": 15.0},
    "macarena": {"id": "dance-macarena", "duration": 12.2}, "handsintheair": {"id": "dance-handsup", "duration": 22.2},
    "duckwalk": {"id": "dance-duckwalk", "duration": 11.7}, "kpopdance": {"id": "dance-blackpink", "duration": 7.1},
    "pushups": {"id": "dance-aerobics", "duration": 8.7}, "hyped": {"id": "emote-hyped", "duration": 7.4},
    "jinglebell": {"id": "dance-jinglebell", "duration": 11.0}, "nervous": {"id": "idle-nervous", "duration": 21.7},
    "toilet": {"id": "idle-toilet", "duration": 32.1}, "attention": {"id": "emote-attention", "duration": 4.4},
    "astronaut": {"id": "emote-astronaut", "duration": 13.7}, "dancezombie": {"id": "dance-zombie", "duration": 14.1}
}

class Bot(BaseBot):
    def __init__(self):
        super().__init__()
        self.bot_id = None
        self.owner_id = None
        self.owner_username = "sadi_key"
        self.bot_status = False
        self.tip_data = {}
        self.vip_users = []
        self.welcome_payouts = []
        
        self.load_database_file()

        # Teleport Locations
        self.vip_spawn_points = [
            Position(26.75, 23.0, 23.35, facing="FrontRight"),
            Position(19.00070, 23.0, 33.99, facing="FrontRight"),
            Position(27.5, 23.0, 30.0, facing="FrontRight")
        ]
        self.ground_spawn_position = Position(27.0, 0.5, 34.0, facing="FrontRight")

        # Memory Run-time Components
        self.active_emote_loops = {}
        self.tip_queue = asyncio.Queue()
        self.room_stay_tracker = {}

    def load_database_file(self) -> None:
        try:
            with open(DATA_FILE, "r") as file:
                data = load(file)
                self.tip_data = data.get("users", {})
                self.vip_users = data.get("vip_users", [])
                self.welcome_payouts = data.get("welcome_payouts", [])
                print(f"[MEMORY LOG] Database loaded. Tippers={len(self.tip_data)}, VIPs={len(self.vip_users)}")
        except Exception as e:
            print(f"[MEMORY ERROR] Failed to parse local database file: {e}")

    def save_database_file(self) -> None:
        try:
            with open(DATA_FILE, "r+") as file:
                data = load(file)
                file.seek(0)
                data["users"] = self.tip_data
                data["vip_users"] = self.vip_users
                data["welcome_payouts"] = self.welcome_payouts
                dump(data, file)
                file.truncate()
        except Exception as e:
            print(f"[MEMORY ERROR] Saving execution aborted: {e}")

    def get_bot_position(self) -> Position:
        try:
            with open(DATA_FILE, "r") as file:
                data = load(file)
                pos_data = data.get("bot_position", {"x": 0, "y": 0, "z": 0, "facing": "FrontRight"})
                return Position(pos_data["x"], pos_data["y"], pos_data["z"], pos_data["facing"])
        except Exception:
            return Position(0, 0, 0, "FrontRight")

    # —— ASYNCHRONOUS EMOTE LOOPS ENGINE ——
    async def loop_emote_handler(self, user_id: str, emote_id: str, duration: float) -> None:
        try:
            while True:
                if user_id not in self.active_emote_loops or self.active_emote_loops[user_id]["emote_id"] != emote_id:
                    break
                await self.highrise.send_emote(emote_id, user_id)
                await asyncio.sleep(duration)
        except asyncio.CancelledError: pass
        except Exception as e: print(f"Error in loop_emote for user {user_id}: {e}")
        finally:
            if user_id in self.active_emote_loops and self.active_emote_loops[user_id]["emote_id"] == emote_id:
                del self.active_emote_loops[user_id]

    async def stop_user_emote(self, user_id: str) -> None:
        if user_id in self.active_emote_loops:
            task = self.active_emote_loops[user_id]["task"]
            task.cancel()
            try: await task
            except asyncio.CancelledError: pass
            if user_id in self.active_emote_loops: del self.active_emote_loops[user_id]

    # —— SERIALIZED QUEUE WORKER ENGINE ——
    async def process_tip_queue_worker(self):
        print("[QUEUE WORKER] Serialization processor activated.")
        while True:
            target_id, gold_bar_tier, username, reason = await self.tip_queue.get()
            try:
                await self.highrise.tip_user(target_id, gold_bar_tier)
                if reason == "welcome":
                    await self.highrise.chat(f"🎉 @{username}, enjoy your 1g welcome bonus!")
                elif reason == "stay_reward":
                    await self.highrise.chat(f"⏰ @{username} received 1g for supporting the room with their stay-time! 🎉")
                print(f"[RENDER LOG - TIP] Sent {gold_bar_tier} to @{username}. Reason: {reason}")
                await asyncio.sleep(1.2)
            except Exception as queue_err:
                error_str = str(queue_err).lower()
                if "closing transport" in error_str or "connection closed" in error_str:
                    os._exit(1)
                await asyncio.sleep(2.0)
            finally:
                self.tip_queue.task_done()

    # —— BACKGROUND STAY TIME ENGINE ——
    async def track_user_stay_durations_loop(self):
        print("[STAY TIME ENGINE] Tracking loop activated.")
        while True:
            await asyncio.sleep(30)
            now = time.time()
            for user_id, data in list(self.room_stay_tracker.items()):
                elapsed_seconds = now - data["join_time"]
                elapsed_minutes = elapsed_seconds / 60.0
                
                if not data["hit_30m"] and elapsed_minutes >= 30.0:
                    self.room_stay_tracker[user_id]["hit_30m"] = True
                    self.room_stay_tracker[user_id]["next_milestone_minutes"] = 90.0
                    await self.tip_queue.put((user_id, "gold_bar_1", data["username"], "stay_reward"))
                elif data["hit_30m"] and elapsed_minutes >= data["next_milestone_minutes"]:
                    self.room_stay_tracker[user_id]["next_milestone_minutes"] += 60.0
                    await self.tip_queue.put((user_id, "gold_bar_1", data["username"], "stay_reward"))

    # —— SAFE HARD-RESTART WATCHDOG ——
    async def connection_watchdog_loop(self) -> None:
        while True:
            await asyncio.sleep(45)
            try:
                await self.highrise.get_wallet()
            except Exception as e:
                error_msg = str(e).lower()
                if "closing transport" in error_msg or "broken pipe" in error_msg or "connection closed" in error_msg:
                    os._exit(1)

            try:
                room_users = await self.highrise.get_room_users()
                if room_users and hasattr(room_users, "content"):
                    pos_data = self.get_bot_position()
                    for user, position in room_users.content:
                        if user.id == self.bot_id:
                            if isinstance(position, Position):
                                if abs(position.x - pos_data.x) > 0.5 or abs(position.z - pos_data.z) > 0.5:
                                    if pos_data != Position(0,0,0, 'FrontRight'):
                                        await self.highrise.teleport(self.bot_id, pos_data)
                            break
            except Exception as e:
                error_msg = str(e).lower()
                if "closing transport" in error_msg or "connection closed" in error_msg:
                    os._exit(1)

    # —— RICH MULTI-COLORED PUBLIC ANNOUNCEMENTS ——
    async def start_announcement_loop(self) -> None:
        announcements = [
            "✨ <color=#00FFFF><b>Welcome to the room!</b></color> Grab a drink, make friends, and enjoy the vibe! 🎵🥂",
            "👑 <color=#FFD700><b>PERMANENT VIP ACCESS:</b></color> Support us by tipping the Bot <b>500g+</b> to unlock permanent VIP perks & entry to our luxury lounge! 💎🚀",
            "⚠️ <color=#FF4500><b>NEED ASSISTANCE?</b></color> If you have any questions or issues, please text a <b>MOD</b> or the <b>Owner</b> directly! 🛡️💬"
        ]
        while True:
            try:
                room_users = await self.highrise.get_room_users()
                if room_users and hasattr(room_users, "content") and len(room_users.content) > 1:
                    chosen_broadcast = random.choice(announcements)
                    await self.highrise.chat(chosen_broadcast)
                await asyncio.sleep(240)
            except Exception as e:
                error_msg = str(e).lower()
                if "closing transport" in error_msg or "connection closed" in error_msg:
                    os._exit(1)
                await asyncio.sleep(10)

    # —— HIGHRISE EVENTS API HANDLERS ——
    async def on_start(self, session_metadata: SessionMetadata) -> None:
        print("Bot Connected")
        self.bot_id = session_metadata.user_id
        self.owner_id = session_metadata.room_info.owner_id
        
        if self.bot_status:
            await self.place_bot()
        self.bot_status = True

        asyncio.create_task(self.process_tip_queue_worker())
        asyncio.create_task(self.track_user_stay_durations_loop())
        asyncio.create_task(self.start_announcement_loop())
        asyncio.create_task(self.connection_watchdog_loop())

    async def place_bot(self):
        while self.bot_status is False:
            await asyncio.sleep(0.5)
        try:
            bot_position = self.get_bot_position()
            if bot_position != Position(0, 0, 0, 'FrontRight'):
                await self.highrise.teleport(self.bot_id, bot_position)
        except Exception as e: print(f"Error with starting position {e}")

    async def on_user_join(self, user: User, position: Position | AnchorPosition) -> None:
        if user.id == self.bot_id or "bot" in user.username.lower(): return
        print(f"{user.username} joined the room")
        
        self.room_stay_tracker[user.id] = {
            "username": user.username, "join_time": time.time(), "hit_30m": False, "next_milestone_minutes": 30.0
        }

        try:
            welcome_text = (
                f"👋 Welcome to the room @{user.username}! 🎉\n"
                f"💡 Type '!help' to view Room Commands.\n"
                f"👑 Want permanent VIP? Tip the Bot 500g+ or support us by tipping the Jar! ❤️"
            )
            await self.highrise.chat(welcome_text)
            
            if user.id not in self.welcome_payouts:
                self.welcome_payouts.append(user.id)
                self.save_database_file()
                await self.tip_queue.put((user.id, "gold_bar_1", user.username, "welcome"))
        except Exception as e: print(f"[JOIN ERROR] {e}")

    async def on_user_leave(self, user: User) -> None:
        await self.stop_user_emote(user.id)
        if user.id in self.room_stay_tracker: del self.room_stay_tracker[user.id]

    async def send_vip_welcome_packet(self, user_id: str, username: str) -> None:
        try:
            await asyncio.sleep(1.0)
            await self.highrise.send_whisper(user_id, f"👑 Welcome to Lifetime VIP, @{username}! Here are your exclusive commands:")
            await self.highrise.send_whisper(user_id, "🚀 Type: '!vip' to teleport up to the luxury lounge level.")
            await self.highrise.send_whisper(user_id, "⬇️ Type: '!down' to return immediately back to the main ground floor.")
            await self.highrise.send_whisper(user_id, "🎵 Type: '!play <song name>' to generate a YouTube audio link for the room chat!")
        except Exception: pass

    async def on_tip(self, sender: User, receiver: User, tip: CurrencyItem | Item) -> None:
        if sender.id == self.bot_id: return
        if isinstance(tip, CurrencyItem):
            if receiver.id == self.bot_id:
                if sender.id not in self.tip_data:
                    self.tip_data[sender.id] = {"username": sender.username, "total_tips": 0}
                self.tip_data[sender.id]['total_tips'] += tip.amount
                
                if tip.amount >= 500:
                    is_new = sender.id not in self.vip_users
                    if is_new: self.vip_users.append(sender.id)
                    await self.highrise.chat(
                        f"✨ 👑 [VIP PROMOTION] 👑 ✨\n"
                        f"Deep gratitude to @{sender.username} for the generous {tip.amount}g tip! "
                        f"LIFETIME VIP ACCESS granted successfully! Check your whispers for commands. 🚀"
                    )
                    if is_new: await self.send_vip_welcome_packet(sender.id, sender.username)
                else:
                    await self.highrise.chat(f"Thank you {sender.username} for the generous {tip.amount}g tip!")
                self.save_database_file()

    async def on_chat(self, user: User, message: str) -> None:
        await self.command_handler(user, message, source="chat")

    async def on_whisper(self, user: User, message: str) -> None:
        await self.command_handler(user, message, source="whisper")

    async def on_message(self, user_id: str, conversation_id: str, is_new_conversation: bool) -> None:
        conversation = await self.highrise.get_messages(conversation_id)
        message = conversation.messages[0].content
        room_users = await self.highrise.get_room_users()
        user_obj = next((u for u, pos in room_users.content if u.id == user_id), None)
        if not user_obj: user_obj = User(id=user_id, username=f"User_{user_id}")
        await self.command_handler(user_obj, message, source="message", conv_id=conversation_id)

    # —— CORE UNIFIED COMMANDS ROUTER ENGINE ——
    async def command_handler(self, user: User, message: str, source: str, conv_id: str = None):
        clean_msg = message.lower().strip()
        is_owner = (user.id == self.owner_id or user.username.lower() == self.owner_username.lower())
        is_vip = (user.id in self.vip_users)

        # ROLE-BASED HELP INTERCEPTOR (Delivers as a private whisper)
        if clean_msg == "!help":
            if is_owner:
                help_text = "⚡ Host Panel: !bal | !with <amt> | !give @user <amt> | !giveall <amt> | !givevip @user | !removevip @user | !set | !top | !get @user | !wallet"
            elif is_vip:
                help_text = "💡 VIP Lounge Access: Type '!vip' to teleport up or '!down' to return.\n🎵 Request Music: Type '!play <song name>'.\n🕺 Dance Engine: Type '!loop <name>' or '!stop'."
            else:
                help_text = "✨ Guest Info: Support us by tipping 500g+ to automatically unlock Permanent VIP!\n🕺 Dance Engine: Type '!loop <name>' or '!stop' to control animation tracks."
            
            try: await self.highrise.send_whisper(user.id, help_text)
            except Exception as e: print(f"Error handling help whisper: {e}")
            return

        # —— FREE MOUNTED YOUTUBE DJ LINK SEARCH TRIGGER ——
        if clean_msg.startswith("!play "):
            if not (is_vip or is_owner):
                await self.respond(user, "❌ Music link requests are exclusive to VIP members.", source, conv_id)
                return
            
            requested_track = message[6:].strip()
            if not requested_track:
                await self.respond(user, "❌ Please specify a track name or artist. Example: !play Lo-Fi Beats", source, conv_id)
                return

            try:
                print(f"[DJ ENGINE] Searching YouTube index for matching query: {requested_track}")
                results = YoutubeSearch(requested_track, max_results=1).to_dict()
                
                if results:
                    video = results[0]
                    video_title = video.get('title', 'Unknown Track')
                    video_id = video.get('id')
                    duration = video.get('duration', '0:00')
                    youtube_url = f"https://youtu.be/{video_id}"
                    
                    # Announce click-to-play link directly to the Highrise text room stream
                    announcement = f"🎵 @{user.username} is DJing! Playing: '{video_title}' [{duration}]. Tap to listen: {youtube_url}"
                    await self.highrise.chat(announcement)
                else:
                    await self.respond(user, f"❌ Zero track matches found for '{requested_track}'.", source, conv_id)
            except Exception as e:
                print(f"[DJ ENGINE ERROR] Lookup aborted: {e}")
                await self.respond(user, "⚠️ Link engine temporarily busy. Try your request again.", source, conv_id)
            return

        # 1. PUBLIC GUEST INTERACTIVE COMMANDS
        if clean_msg.startswith("!loop "):
            emote_name = clean_msg.replace("!loop ", "").strip()
            if emote_name in EMOTE_MAP:
                await self.stop_user_emote(user.id)
                emote_id = EMOTE_MAP[emote_name]["id"]
                duration = EMOTE_MAP[emote_name]["duration"]
                task = asyncio.create_task(self.loop_emote_handler(user.id, emote_id, duration))
                self.active_emote_loops[user.id] = {"task": task, "emote_id": emote_id}
                await self.respond(user, f"✅ Started your loops for '{emote_name}'. Type '!stop' to end.", source, conv_id)
            else:
                await self.respond(user, "❌ Unknown emote name. Please check your command.", source, conv_id)
            return

        elif clean_msg == "!stop":
            if user.id in self.active_emote_loops:
                await self.stop_user_emote(user.id)
                await self.respond(user, "✅ Your active loops have been closed.", source, conv_id)
            return

        elif clean_msg == "!vip":
            if is_vip or is_owner:
                try: await self.highrise.teleport(user.id, random.choice(self.vip_spawn_points))
                except Exception: pass
            else:
                await self.respond(user, "❌ Access Denied. Tip 500g or more to unlock.", source, conv_id)
            return

        elif clean_msg == "!down":
            if is_vip or is_owner:
                try: await self.highrise.teleport(user.id, self.ground_spawn_position)
                except Exception: pass
            return

        # 2. RESTRICTED HOST ADMINISTRATIVE CONTROLS
        if not is_owner: return

        if clean_msg.startswith("!set"):
            position = None
            try:
                room_users = await self.highrise.get_room_users()
                for room_user, pos in room_users.content:
                    if user.id == room_user.id and isinstance(pos, Position): position = pos
                if position is not None:
                    with open(DATA_FILE, "r+") as file:
                        data = load(file)
                        file.seek(0)
                        data["bot_position"] = {"x": position.x, "y": position.y, "z": position.z, "facing": position.facing}
                        dump(data, file)
                        file.truncate()
                    set_position = Position(position.x, (position.y + 0.0000001), position.z, facing=position.facing)
                    await self.highrise.teleport(self.bot_id, set_position)
                    await self.highrise.teleport(self.bot_id, position)
                    await self.highrise.walk_to(position)
                    await self.respond(user, "Updated bot position.", source, conv_id)
            except Exception as e: print(f"Error setting bot position: {e}")

        elif clean_msg.startswith("!top"):
            sorted_tippers = sorted(self.tip_data.items(), key=lambda x: x[1]['total_tips'], reverse=True)[:10]
            formatted_tippers = [f"{i + 1}. {d['username']} ({d['total_tips']}g)" for i, (_, d) in enumerate(sorted_tippers)]
            await self.respond(user, f"Top Tippers:\n{str('\n'.join(formatted_tippers))}", source, conv_id)

        elif clean_msg.startswith("!get "):
            username = clean_msg.split(" ", 1)[1].replace("@", "").strip()
            tip_amount = None
            for _, d in self.tip_data.items():
                if d['username'].lower() == username.lower(): tip_amount = d['total_tips']
            if tip_amount is not None: await self.respond(user, f"{username} has tipped {tip_amount}g", source, conv_id)

        elif clean_msg == "!wallet" or clean_msg == "!bal":
            wallet = await self.highrise.get_wallet()
            gold = next((currency.amount for currency in wallet.content if currency.type == 'gold'), 0)
            await self.respond(user, f"💰 [VAULT BALANCE] {gold} gold remains securely in reserve.", source, conv_id)

        elif clean_msg.startswith("!with"):
            try:
                parts = clean_msg.split()
                if len(parts) > 1:
                    raw_amount = parts[1].replace("g", "")
                    if raw_amount in ["1", "5", "10", "50", "100", "500", "1k", "5000", "10k"]:
                        await self.highrise.tip_user(user.id, f"gold_bar_{raw_amount}")
            except Exception as e: print(f"[WITHDRAWAL FAIL] {e}")

        elif clean_msg.startswith("!give "):
            try:
                parts = message.split()
                if len(parts) >= 3:
                    target_user = parts[1].replace("@", "").strip()
                    amount_str = parts[2].lower().replace("g", "")
                    if amount_str in ["1", "5", "10", "50", "100", "500", "1k", "5000", "10k"]:
                        room_users = await self.highrise.get_room_users()
                        user_id_found = next((u.id for u, pos in room_users.content if u.username.lower() == target_user.lower()), None)
                        if user_id_found: await self.highrise.tip_user(user_id_found, f"gold_bar_{amount_str}")
            except Exception as e: print(f"[GIFT FAIL] {e}")

        elif clean_msg.startswith("!giveall "):
            try:
                parts = clean_msg.split()
                if len(parts) >= 2:
                    amount_str = parts[1].replace("g", "")
                    if amount_str in ["1", "5", "10"]:
                        room_users = await self.highrise.get_room_users()
                        target_count = 0
                        for u, pos in room_users.content:
                            if u.id != self.bot_id and u.username.lower() != self.owner_username.lower():
                                target_count += 1
                                await self.tip_queue.put((u.id, f"gold_bar_{amount_str}", u.username, "giveall"))
            except Exception as e: print(f"[GIVEALL FAIL] {e}")

        elif clean_msg.startswith("!givevip "):
            try:
                parts = message.split()
                if len(parts) >= 2:
                    target_user = parts[1].replace("@", "").strip()
                    room_users = await self.highrise.get_room_users()
                    user_id_found = next((u.id for u, pos in room_users.content if u.username.lower() == target_user.lower()), None)
                    if user_id_found and user_id_found not in self.vip_users:
                        self.vip_users.append(user_id_found)
                        self.save_database_file()
                        await self.highrise.chat(f"👑 VIP Status manually granted to @{target_user}! ✨")
                        await self.send_vip_welcome_packet(user_id_found, target_user)
            except Exception as e: print(f"[GIVEVIP FAIL] {e}")

        elif clean_msg.startswith("!removevip "):
            try:
                parts = message.split()
                if len(parts) >= 2:
                    target_user = parts[1].replace("@", "").strip()
                    room_users = await self.highrise.get_room_users()
                    user_id_found = next((u.id for u, pos in room_users.content if u.username.lower() == target_user.lower()), None)
                    if user_id_found and user_id_found in self.vip_users:
                        self.vip_users.remove(user_id_found)
                        self.save_database_file()
                        await self.highrise.chat(f"🚫 VIP Status has been removed from @{target_user}.")
            except Exception as e: print(f"[REMOVEVIP FAIL] {e}")

    async def respond(self, user: User, msg: str, source: str, conv_id: str = None):
        try:
            if source == "chat": await self.highrise.chat(msg)
            elif source == "whisper": await self.highrise.send_whisper(user.id, msg)
            elif source == "message" and conv_id: await self.highrise.send_message(conv_id, msg)
        except Exception as e: print(f"Response Delivery Error: {e}")

# —— LIVE MONITORING NETWORK LAYER ——
class LightHealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"status": "alive", "msg": "Integrated Client Online"}')
    def log_message(self, format, *args): return

def run_health_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), LightHealthCheckHandler)
    server.serve_forever()

async def start_bot_engine():
    while True:
        try:
            bot_instance = Bot()
            definitions = [BotDefinition(bot_instance, ROOM_ID, API_TOKEN)]
            await main(definitions=definitions)
        except Exception as engine_err:
            await asyncio.sleep(30)

def data_file(filename: str, default_data: str) -> None:
    if not os.path.exists(filename):
        with open(filename, 'w') as file: file.write(default_data)

if __name__ == "__main__":
    DEFAULT_DATA = '{"users": {}, "vip_users": [], "welcome_payouts": [], "bot_position": {"x": 0, "y": 0, "z": 0, "facing": "FrontRight"}}'
    data_file(DATA_FILE, DEFAULT_DATA)

    web_worker = threading.Thread(target=run_health_server, daemon=True)
    web_worker.start()
    
    try: asyncio.run(start_bot_engine())
    except KeyboardInterrupt: print("Closed pipeline manually.")
