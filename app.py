"""
Highrise Room Management Bot - Ultimate Persistence & Economy Edition
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

# =====================================================================
# 🤖 1. HIGHRISE CORE GAME ENGINE
# =====================================================================
class SecurityRoomBot(BaseBot):
    def __init__(self):
        super().__init__()
        self.vip_users = []      
        self.tipped_users = []   
        self.owner_username = "sadi_key"
        self.owner_id = None  
        self.bot_id = None
        self.last_highrise_activity = time.time()
        
        # 📍 TARGET LOCATION: Bot will hold this exact spot naturally
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
        
        # Initial placement right out of the gate
        await asyncio.sleep(3.0)
        try:
            await self.highrise.teleport(self.bot_id, self.bot_spawn_position)
        except Exception: pass
                
        # Start background runtime tasks safely
        asyncio.create_task(self.start_announcement_loop())
        asyncio.create_task(self.connection_watchdog_loop())

    async def connection_watchdog_loop(self) -> None:
        while True:
            await asyncio.sleep(60)
            try:
                # 1. Keep alive ping
                await self.highrise.get_wallet()
                self.last_highrise_activity = time.time()
                
                # 2. Smart Drift Anchor: Only teleports if bumped or moved away!
                room_users = await self.highrise.get_room_users()
                for user, position in room_users.content:
                    if user.id == self.bot_id:
                        if isinstance(position, Position):
                            # If bot drifted away from target coordinates, snap it back cleanly
                            if abs(position.x - 14.0) > 0.5 or abs(position.z - 31.0) > 0.5:
                                print("[ANCHOR] Bot drifted. Re-centering position smoothly.")
                                await self.highrise.teleport(self.bot_id, self.bot_spawn_position)
                        break
            except Exception as e:
                print(f"[WATCHDOG KICK] Room likely closed or empty: {e}")
                
            # If server hasn't responded in 8 minutes, force Render to restart the engine completely
            if time.time() - self.last_highrise_activity > 480:
                print("[CRITICAL ALERT] Game connection frozen entirely. Hard cycling container...")
                sys.exit(1)

    async def start_announcement_loop(self) -> None:
        while True:
            try:
                await asyncio.sleep(300)  
                await self.highrise.chat(
                    "📢 Tip 500g to become permanent VIP! Invite your friends to this public hangout place "
                    "and have tips and fun. Apply for MOD DM @sadi_key ✨"
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

            # 🌟 NEW WORKING !GIVEALL COMMAND LOGIC
            elif clean_msg.startswith("!giveall "):
                try:
                    parts = clean_msg.split()
                    if len(parts) >= 2:
                        amount_str = parts[1].replace("g", "")
                        if amount_str in ["1", "5", "10"]:
                            room_users = await self.highrise.get_room_users()
                            # Loop over all active players inside your room
                            target_count = 0
                            for u, pos in room_users.content:
                                if u.id != self.bot_id and u.username.lower() != self.owner_username.lower():
                                    target_count += 1
                                    asyncio.create_task(self.highrise.tip_user(u.id, f"gold_bar_{amount_str}"))
                                    await asyncio.sleep(0.2) # anti-spam delay split
                            
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
                await self.highrise.send_whisper(user.id, "💡 VIP Commands: Type '!vip' or '!down'.")
            else:
                await self.highrise.send_whisper(user.id, f"💡 Menu: Type '!vip' to verify access status. Tip 500g to unlock features!")
                
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
