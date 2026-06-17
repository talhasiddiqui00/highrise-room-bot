"""
Highrise Room Management Bot - Persistent, Emote Loop & Clean Announcement Edition
Target Room ID: 6a28b5b000b6151bd4c9641e
SDK Version: 25.1.0
Developer: sadi_key
"""

import os
import sys
import time
import random
import asyncio
from typing import Union
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

from highrise import BaseBot, User, Position, AnchorPosition
from highrise.models import SessionMetadata, CurrencyItem, Item

MEMORY_FILE = "tipped_users.txt"

EMOTE_MAP = {
    "rest": {"id": "sit-open", "duration": 17.062613},
    "zombie": {"id": "idle_zombie", "duration": 28.754937},
    "relaxed": {"id": "idle_layingdown2", "duration": 21.546653},
    "attentive": {"id": "idle_layingdown", "duration": 24.585168},
    "sleepy": {"id": "idle-sleep", "duration": 22.620446},
    "poutyface": {"id": "idle-sad", "duration": 24.377214},
    "posh": {"id": "idle-posh", "duration": 21.851256},
    "tired": {"id": "idle-loop-tired", "duration": 21.959007},
    "taploop": {"id": "idle-loop-tapdance", "duration": 6.261593},
    "sit": {"id": "idle-loop-sitfloor", "duration": 22.321055},
    "shy": {"id": "idle-loop-shy", "duration": 16.47449},
    "bummed": {"id": "idle-loop-sad", "duration": 6.052999},
    "chillin": {"id": "idle-loop-happy", "duration": 18.798322},
    "annoyed": {"id": "idle-loop-annoyed", "duration": 17.058522},
    "aerobics": {"id": "idle-loop-aerobics", "duration": 8.507535},
    "ponder": {"id": "idle-lookup", "duration": 22.339865},
    "heropose": {"id": "idle-hero", "duration": 21.877099},
    "relaxing": {"id": "idle-floorsleeping2", "duration": 17.253372},
    "cozynap": {"id": "idle-floorsleeping", "duration": 13.935264},
    "enthused": {"id": "idle-enthusiastic", "duration": 15.941537},
    "feelthebeat": {"id": "idle-dance-headbobbing", "duration": 25.367458},
    "irritated": {"id": "idle-angry", "duration": 25.427848},
    "fastsing": {"id": "emote-sicklycute-sing-fast", "duration": 10},
    "slowsing": {"id": "emote-sicklycute-sing-slow", "duration": 10},
    "yes": {"id": "emote-yes", "duration": 2.565001},
    "ibelieveicanfly": {"id": "emote-wings", "duration": 13.134487},
    "thewave": {"id": "emote-wave", "duration": 2.690873},
    "think": {"id": "emote-think", "duration": 3.691104},
    "theatrical": {"id": "emote-theatrical", "duration": 8.591869},
    "tapdance": {"id": "emote-tapdance", "duration": 11.057294},
    "superrun": {"id": "emote-superrun", "duration": 6.273226},
    "superpunch": {"id": "emote-superpunch", "duration": 3.751054},
    "sumofight": {"id": "emote-sumo", "duration": 10.868834},
    "thumbsuck": {"id": "emote-suckthumb", "duration": 4.185944},
    "splitsdrop": {"id": "emote-splitsdrop", "duration": 4.46931},
    "snowballfight": {"id": "emote-snowball", "duration": 5.230467},
    "snowangel": {"id": "emote-snowangel", "duration": 6.218627},
    "handshake": {"id": "emote-secrethandshake", "duration": 3.879024},
    "sad": {"id": "emote-sad", "duration": 5.411073},
    "pull": {"id": "emote-ropepull", "duration": 8.769656},
    "roll": {"id": "emote-roll", "duration": 3.560517},
    "rofl": {"id": "emote-rofl", "duration": 6.314731},
    "robot": {"id": "emote-robot", "duration": 7.607362},
    "rainbow": {"id": "emote-rainbow", "duration": 2.813373},
    "proposing": {"id": "emote-proposing", "duration": 4.27888},
    "peekaboo": {"id": "emote-peekaboo", "duration": 3.629867},
    "peace": {"id": "emote-peace", "duration": 5.755004},
    "panic": {"id": "emote-panic", "duration": 2.850966},
    "no": {"id": "emote-no", "duration": 2.703034},
    "ninjarun": {"id": "emote-ninjarun", "duration": 4.754721},
    "nightfever": {"id": "emote-nightfever", "duration": 5.488424},
    "monsterfail": {"id": "emote-monster_fail", "duration": 4.632708},
    "model": {"id": "emote-model", "duration": 6.490173},
    "levelup": {"id": "emote-levelup", "duration": 6.0545},
    "amused": {"id": "emote-laughing2", "duration": 5.056641},
    "laugh": {"id": "emote-laughing", "duration": 2.69161},
    "kiss": {"id": "emote-kiss", "duration": 2.387175},
    "superkick": {"id": "emote-kicking", "duration": 4.867992},
    "jump": {"id": "emote-jumpb", "duration": 3.584234},
    "judochop": {"id": "emote-judochop", "duration": 2.427442},
    "jetpack": {"id": "emote-jetpack", "duration": 16.759457},
    "hugyourself": {"id": "emote-hugyourself", "duration": 4.992751},
    "sweating": {"id": "emote-hot", "duration": 4.353037},
    "hello": {"id": "emote-hello", "duration": 2.734844},
    "harlemshake": {"id": "emote-harlemshake", "duration": 13.558597},
    "happy": {"id": "emote-happy", "duration": 3.483462},
    "handstand": {"id": "emote-handstand", "duration": 4.015678},
    "greedyemote": {"id": "emote-greedy", "duration": 4.639828},
    "moonwalk": {"id": "emote-gordonshuffle", "duration": 8.052307},
    "ghostfloat": {"id": "emote-ghost-idle", "duration": 19.570492},
    "gangnamstyle": {"id": "emote-gangnam", "duration": 7.275486},
    "faint": {"id": "emote-fainting", "duration": 18.423499},
    "clumsy": {"id": "emote-fail2", "duration": 6.475972},
    "fall": {"id": "emote-fail1", "duration": 5.617942},
    "facepalm": {"id": "emote-exasperatedb", "duration": 2.722748},
    "exasperated": {"id": "emote-exasperated", "duration": 2.367483},
    "elbowbump": {"id": "emote-elbowbump", "duration": 3.799768},
    "disco": {"id": "emote-disco", "duration": 5.366973},
    "blastoff": {"id": "emote-disappear", "duration": 6.195985},
    "faintdrop": {"id": "emote-deathdrop", "duration": 3.762728},
    "collapse": {"id": "emote-death2", "duration": 4.855549},
    "revival": {"id": "emote-death", "duration": 6.615967},
    "dab": {"id": "emote-dab", "duration": 2.717871},
    "curtsy": {"id": "emote-curtsy", "duration": 2.425714},
    "confusion": {"id": "emote-confused", "duration": 8.578827},
    "cold": {"id": "emote-cold", "duration": 3.664348},
    "charging": {"id": "emote-charging", "duration": 8.025079},
    "bunnyhop": {"id": "emote-bunnyhop", "duration": 12.380685},
    "bow": {"id": "emote-bow", "duration": 3.344036},
    "boo": {"id": "emote-boo", "duration": 4.501502},
    "homerun": {"id": "emote-baseball", "duration": 7.254841},
    "fallingapart": {"id": "emote-apart", "duration": 4.809542},
    "thumbsup": {"id": "emoji-thumbsup", "duration": 2.702369},
    "point": {"id": "emoji-there", "duration": 2.059095},
    "sneeze": {"id": "emoji-sneeze", "duration": 2.996694},
    "smirk": {"id": "emoji-smirking", "duration": 4.823158},
    "sick": {"id": "emoji-sick", "duration": 5.070367},
    "gasp": {"id": "emoji-scared", "duration": 3.008487},
    "punch": {"id": "emoji-punch", "duration": 1.755783},
    "pray": {"id": "emoji-pray", "duration": 4.503179},
    "stinky": {"id": "emoji-poop", "duration": 4.795735},
    "naughty": {"id": "emoji-naughty", "duration": 4.277602},
    "mindblown": {"id": "emoji-mind-blown", "duration": 2.397167},
    "lying": {"id": "emoji-lying", "duration": 6.313748},
    "levitate": {"id": "emoji-halo", "duration": 5.837754},
    "fireballlunge": {"id": "emoji-hadoken", "duration": 2.723709},
    "giveup": {"id": "emoji-give-up", "duration": 5.407888},
    "tummyache": {"id": "emoji-gagging", "duration": 5.500202},
    "stunned": {"id": "emoji-dizzy", "duration": 4.053049},
    "sob": {"id": "emoji-crying", "duration": 3.696499},
    "clap": {"id": "emoji-clapping", "duration": 2.161757},
    "raisetheroof": {"id": "emoji-celebrate", "duration": 3.412258},
    "arrogance": {"id": "emoji-arrogance", "duration": 6.869441},
    "angry": {"id": "emoji-angry", "duration": 5.760023},
    "voguehands": {"id": "dance-voguehands", "duration": 9.150634},
    "savagedance": {"id": "dance-tiktok8", "duration": 10.938702},
    "dontstartnow": {"id": "dance-tiktok2", "duration": 10.392353},
    "smoothwalk": {"id": "dance-smoothwalk", "duration": 6.690023},
    "ringonit": {"id": "dance-singleladies", "duration": 21.191372},
    "letsgoshopping": {"id": "dance-shoppingcart", "duration": 4.316035},
    "russian": {"id": "dance-russian", "duration": 10.252905},
    "pennywise": {"id": "dance-pennywise", "duration": 1.214349},
    "orangejuicedance": {"id": "dance-orangejustice", "duration": 6.475263},
    "rockout": {"id": "dance-metal", "duration": 15.076377},
    "macarena": {"id": "dance-macarena", "duration": 12.214141},
    "handsintheair": {"id": "dance-handsup", "duration": 22.283413},
    "duckwalk": {"id": "dance-duckwalk", "duration": 11.748784},
    "kpopdance": {"id": "dance-blackpink", "duration": 7.150958},
    "pushups": {"id": "dance-aerobics", "duration": 8.796402},
    "hyped": {"id": "emote-hyped", "duration": 7.492423},
    "jinglebell": {"id": "dance-jinglebell", "duration": 11},
    "nervous": {"id": "idle-nervous", "duration": 21.714221},
    "toilet": {"id": "idle-toilet", "duration": 32.174447},
    "attention": {"id": "emote-attention", "duration": 4.401206},
    "astronaut": {"id": "emote-astronaut", "duration": 13.791175},
    "dancezombie": {"id": "dance-zombie", "duration": 14.1}
}

# =====================================================================
# 🤖 1. HIGHRISE CORE GAME ENGINE
# =====================================================================
class SecurityRoomBot(BaseBot):
    def __init__(self):
        super().__init__()
        self.vip_users = []      
        self.tipped_users = []   
        self.active_emote_loops = {} 
        self.owner_username = "sadi_key"
        self.owner_id = None  
        self.bot_id = None
        self.last_highrise_activity = time.time()
        
        self.bot_spawn_position = Position(14.0, 0.5, 31.0, facing="FrontRight")
        
        self.vip_spawn_points = [
            Position(26.75, 23.0, 23.35, facing="FrontRight"),
            Position(19.00070, 23.0, 33.99, facing="FrontRight"),
            Position(27.5, 23.0, 30.0, facing="FrontRight")
        ]
        self.load_tipped_users()

    def load_tipped_users(self):
        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, "r") as f:
                    self.tipped_users = [line.strip() for line in f.readlines() if line.strip()]
                print(f"[MEMORY LOG] Loaded {len(self.tipped_users)} remembered users.")
            except Exception as e:
                print(f"[MEMORY ERROR] Failed to read storage: {e}")

    def save_tipped_user(self, user_id: str):
        if user_id not in self.tipped_users:
            self.tipped_users.append(user_id)
            try:
                with open(MEMORY_FILE, "a") as f:
                    f.write(f"{user_id}\n")
            except Exception as e:
                print(f"[MEMORY ERROR] Failed to save storage: {e}")

    async def on_start(self, session_metadata: SessionMetadata) -> None:
        self.bot_id = session_metadata.user_id
        try:
            self.owner_id = session_metadata.room_info.owner_id
        except AttributeError: pass

        print(f"\n[BOT ACTIVE] Handshake confirmed with Highrise server via SDK 25.1.0.")
        self.last_highrise_activity = time.time()
        
        await asyncio.sleep(3.0)
        try:
            await self.highrise.teleport(self.bot_id, self.bot_spawn_position)
        except Exception: pass
                
        asyncio.create_task(self.start_announcement_loop())
        asyncio.create_task(self.connection_watchdog_loop())

    async def connection_watchdog_loop(self) -> None:
        while True:
            await asyncio.sleep(60)
            try:
                await self.highrise.get_wallet()
                self.last_highrise_activity = time.time()
                
                room_users = await self.highrise.get_room_users()
                for user, position in room_users.content:
                    if user.id == self.bot_id:
                        if isinstance(position, Position):
                            if abs(position.x - 14.0) > 0.5 or abs(position.z - 31.0) > 0.5:
                                print("[ANCHOR] Bot drifted. Re-centering position smoothly.")
                                await self.highrise.teleport(self.bot_id, self.bot_spawn_position)
                        break
            except Exception as e:
                print(f"[WATCHDOG KICK] Room likely closed or empty: {e}")
                
            if time.time() - self.last_highrise_activity > 480:
                print("[CRITICAL ALERT] Game connection frozen entirely. Hard cycling container...")
                sys.exit(1)

    # Clean public announcement pathway loop
    async def start_announcement_loop(self) -> None:
        while True:
            try:
                await asyncio.sleep(300)  
                await self.highrise.chat(
                    "✨ Type !help to see commands! Tip 500g for permanent VIP 👑 | "
                    "To loop an emote, type '!loop <name>' and type '!stop' to halt 🕺 | "
                    "Let's hang out and spread love! ❤️"
                )
            except Exception: pass

    async def on_user_join(self, user: User, position: Union[Position, AnchorPosition]) -> None:
        self.last_highrise_activity = time.time()
        if user.id == self.bot_id or "bot" in user.username.lower(): return
        if user.username.lower() == self.owner_username.lower(): self.owner_id = user.id

        try:
            welcome_text = (
                f"👋 Welcome to the room @{user.username}! 🎉\n"
                f"💡 Type '!help' to view Guest Commands.\n"
                f"👑 Want permanent VIP? Tip the Bot 500g+ or support us by tipping the Jar! ❤️"
            )
            await self.highrise.chat(welcome_text)
            
            if user.id not in self.tipped_users:
                self.save_tipped_user(user.id)
                try:
                    await asyncio.sleep(0.8)
                    await self.highrise.tip_user(user.id, "gold_bar_1")
                    await self.highrise.chat(f"🎉 @{user.username}, enjoy your 1g welcome bonus!")
                except Exception: pass
        except Exception as e: print(f"[JOIN ERROR] {e}")

    async def on_user_leave(self, user: User) -> None:
        self.last_highrise_activity = time.time()
        asyncio.create_task(self.stop_emote(user.id))

    async def loop_emote(self, user_id: str, emote_id: str, duration: float) -> None:
        try:
            while True:
                if user_id not in self.active_emote_loops or self.active_emote_loops[user_id]["emote_id"] != emote_id:
                    break
                await self.highrise.send_emote(emote_id, user_id)
                await asyncio.sleep(duration)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"Error in loop_emote for user {user_id}: {e}")
            try:
                await self.highrise.send_whisper(user_id, f"Error performing emote: {e}")
            except Exception: pass
        finally:
            if user_id in self.active_emote_loops and self.active_emote_loops[user_id]["emote_id"] == emote_id:
                del self.active_emote_loops[user_id]

    async def stop_emote(self, user_id: str) -> None:
        try:
            if user_id in self.active_emote_loops:
                task = self.active_emote_loops[user_id]["task"]
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                if user_id in self.active_emote_loops:
                    del self.active_emote_loops[user_id]
        except Exception as e:
            print(f"Error stopping emote for user {user_id}: {e}")

    async def send_vip_welcome_packet(self, user_id: str, username: str) -> None:
        try:
            await asyncio.sleep(1.0) 
            await self.highrise.send_whisper(user_id, f"👑 Welcome to Lifetime VIP, @{username}! Here are your exclusive commands:")
            await self.highrise.send_whisper(user_id, "🚀 Type: '!vip' to teleport up to the luxury lounge level.")
            await self.highrise.send_whisper(user_id, "⬇️ Type: '!down' to return immediately back to the main ground floor.")
        except Exception: pass

    async def on_whisper(self, user: User, message: str) -> None:
        self.last_highrise_activity = time.time()
        if user.id == self.bot_id: return
        try:
            await self.highrise.send_whisper(user.id, "Come to the room if you want to talk or command with me!")
        except Exception: pass

    async def on_tip(self, sender: User, receiver: User, tip: Union[CurrencyItem, Item]) -> None:
        self.last_highrise_activity = time.time()
        if sender.id == self.bot_id: return

        if isinstance(tip, CurrencyItem):
            try:
                is_to_bot = (receiver.id == self.bot_id)
                is_to_owner = (receiver.id == self.owner_id or receiver.username.lower() == self.owner_username.lower())

                if is_to_bot or is_to_owner:
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
                        await self.highrise.chat(f"✨ [ROOM CONTRIBUTION] ✨\nThank you profoundly @{sender.username} for supporting our space with a {tip.amount}g tip! ❤️")
            except Exception as e: print(f"[TIP ERROR] {e}")

    async def on_chat(self, user: User, message: str) -> None:
        self.last_highrise_activity = time.time()
        clean_msg = message.lower().strip()
        
        # --- 🌐 PUBLIC DANCE LOOP PARSER HANDLERS ---
        if clean_msg.startswith("!loop "):
            emote_name = clean_msg.replace("!loop ", "").strip()
            if emote_name in EMOTE_MAP:
                await self.stop_emote(user.id)
                emote_id = EMOTE_MAP[emote_name]["id"]
                duration = EMOTE_MAP[emote_name]["duration"]
                
                task = asyncio.create_task(self.loop_emote(user.id, emote_id, duration))
                self.active_emote_loops[user.id] = {"emote_id": emote_id, "task": task}
                await self.highrise.send_whisper(user.id, f"🕺 Started loop for '{emote_name}'. Type '!stop' to halt.")
            else:
                await self.highrise.send_whisper(user.id, "❌ Unknown dance name. Check spelling format!")
                
        elif clean_msg == "!stop":
            await self.stop_emote(user.id)
            await self.highrise.send_whisper(user.id, "🛑 Your current dance loop has been stopped.")

        # --- ⚡ OWNER ONLY COMMAND PATHWAYS ---
        if user.username.lower() == self.owner_username.lower():
            
            if clean_msg == "!bal":
                try:
                    wallet_response = await self.highrise.get_wallet()
                    bot_gold = next((item.amount for item in wallet_response.content if item.type == "gold"), 0)
                    await self.highrise.send_whisper(user.id, f"💰 [VAULT BALANCE] {bot_gold} gold remains securely in reserve.")
                except Exception as e: print(f"[BALANCE FAIL] {e}")
                    
            elif clean_msg.startswith("!with"):
                try:
                    parts = clean_msg.split()
                    if len(parts) > 1:
                        raw_amount = parts[1].replace("g", "")
                        if raw_amount in ["1", "5", "10", "50", "100", "500", "1k", "5000", "10k"]:
                            await self.highrise.send_whisper(user.id, f"💸 [WITHDRAWAL] Executing {raw_amount}g bar transfer...")
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
                            if user_id_found:
                                await self.highrise.send_whisper(user.id, f"🎁 [GIFT SENT] Transferred {amount_str}g straight to @{target_user}!")
                                await self.highrise.tip_user(user_id_found, f"gold_bar_{amount_str}")
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
                                    asyncio.create_task(self.highrise.tip_user(u.id, f"gold_bar_{amount_str}"))
                                    await asyncio.sleep(0.2)
                            
                            if target_count > 0:
                                await self.highrise.chat(f"🎁 [RAIN DROP] @{self.owner_username} tipped {amount_str}g to all {target_count} players in the room! 🎉")
                            else:
                                await self.highrise.send_whisper(user.id, "❌ No other eligible players found in the room to tip.")
                except Exception as e: print(f"[GIVEALL FAIL] {e}")

            elif clean_msg.startswith("!givevip "):
                try:
                    parts = message.split()
                    if len(parts) >= 2:
                        target_user = parts[1].replace("@", "").strip()
                        room_users = await self.highrise.get_room_users()
                        user_id_found = next((u.id for u, pos in room_users.content if u.username.lower() == target_user.lower()), None)
                        if user_id_found:
                            if user_id_found not in self.vip_users:
                                self.vip_users.append(user_id_found)
                                await self.highrise.chat(f"👑 VIP Status manually granted to @{target_user} by the Room Owner! ✨")
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
                            await self.highrise.chat(f"🚫 VIP Status has been removed from @{target_user}.")
                except Exception as e: print(f"[REMOVEVIP FAIL] {e}")

        # --- 💡 GENERAL PUBLIC COMMAND UTILITIES ---
        if clean_msg == "!help":
            if user.username.lower() == self.owner_username.lower():
                await self.highrise.send_whisper(user.id, "⚡ Commands: !bal | !with <amt> | !give @user <amt> | !giveall <amt> | !givevip @user")
            elif user.id in self.vip_users:
                await self.highrise.send_whisper(user.id, "💡 VIP Commands: Type '!vip' or '!down'.\nDances: Type '!loop <name>' or '!stop'.")
            else:
                await self.highrise.send_whisper(user.id, "💡 Menu: Type '!vip' to verify access status. Tip 500g to unlock features!\nDances: Type '!loop <name>' or '!stop'.")
                
        elif clean_msg == "!vip":
            if user.id in self.vip_users or user.username.lower() == self.owner_username.lower():
                try:
                    await self.highrise.send_whisper(user.id, "🚀 Teleporting up to luxury lounge...")
                    await self.highrise.teleport(user.id, random.choice(self.vip_spawn_points))
                except Exception: pass
            else:
                await self.highrise.send_whisper(user.id, "❌ Access Denied. Tip 500g or more to unlock.")

        elif clean_msg == "!down":
            if user.id in self.vip_users or user.username.lower() == self.owner_username.lower():
                try:
                    await self.highrise.send_whisper(user.id, "⬇️ Returning back to the ground floor...")
                    await self.highrise.teleport(user.id, Position(27.0, 0.5, 34.0, facing="FrontRight"))
                except Exception: pass

# =====================================================================
# 🚀 2. LIGHTWEIGHT WEB LAYER WITH AUTO-RECOVERY PIPELINE
# =====================================================================
class LightHealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"status": "alive", "msg": "Web Interface Active"}')
    def log_message(self, format, *args): return

def run_health_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), LightHealthCheckHandler)
    server.serve_forever()

async def start_bot_engine():
    ROOM_ID = "6a28b5b000b6151bd4c9641e"
    API_TOKEN = "fd250294097b09a7fd05aa523c63b77ef0b980cc28f7f09742b22d0db30b53a0"
    
    from highrise.__main__ import main, BotDefinition
    
    while True:
        try:
            bot_instance = SecurityRoomBot()
            bot_instance.owner_username = "sadi_key"
            definitions = [BotDefinition(bot_instance, ROOM_ID, API_TOKEN)]
            print("[MAIN ENGINE] Launching integrated Highrise Client...")
            await main(definitions=definitions)
        except Exception as engine_err:
            print(f"[RECOVERY PIPELINE] Session dropped ({engine_err}). Retrying connection loop in 60s...")
            await asyncio.sleep(60)

if __name__ == "__main__":
    web_worker = threading.Thread(target=run_health_server, daemon=True)
    web_worker.start()
    print("[WEB LAYER] Non-blocking server listening on port 10000...")
    
    try:
        asyncio.run(start_bot_engine())
    except KeyboardInterrupt:
        print("Manual exit caught.")
