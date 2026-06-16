"""
Highrise Room Management Bot - Scratch Web Service Edition
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
from multiprocessing import Process
from http.server import BaseHTTPRequestHandler, HTTPServer

from highrise import BaseBot, User, Position, AnchorPosition
from highrise.models import SessionMetadata, CurrencyItem, Item

MEMORY_FILE = "tipped_users.txt"

# =====================================================================
# 🚀 1. LIGHTWEIGHT NATIVE WEB LAYER (Zero External Dependencies)
# =====================================================================
class LightHealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Answers Render's port checks and your 5-minute cron job pings"""
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"status": "alive", "msg": "Web Service Operational"}')
        
    def log_message(self, format, *args):
        return  # Silences standard web logs to keep your Render terminal clean

def run_health_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), LightHealthCheckHandler)
    print(f"[WEB LAYER] Web engine listening on port {port} for cron pings...")
    server.serve_forever()

# =====================================================================
# 🤖 2. HIGHRISE CORE GAME ENGINE 
# =====================================================================
class SecurityRoomBot(BaseBot):
    def __init__(self):
        super().__init__()
        self.vip_users = []      
        self.tipped_users = []   
        self.owner_username = "sadi_key"
        self.owner_id = None  
        self.bot_id = None
        
        self.bot_spawn_position = Position(14.0, 2.0, 37.0, facing="FrontRight")
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
        try:
            await asyncio.sleep(1.0)
            await self.highrise.teleport(self.bot_id, self.bot_spawn_position)
            asyncio.create_task(self.start_announcement_loop())
        except Exception as e:
            print(f"[CRITICAL ERROR] Spawn failure: {e}")

    async def start_announcement_loop(self) -> None:
        while True:
            try:
                await asyncio.sleep(300)  
                await self.highrise.chat(
                    "📢 Tip 500g to become permanent VIP! Invite your friends to this public hangout place "
                    "and have tips and fun. Apply for MOD DM @sadi_key ✨"
                )
            except Exception as e:
                print(f"[ANN] Skipped: {e}")

    async def on_user_join(self, user: User, position: Union[Position, AnchorPosition]) -> None:
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
                except Exception as tip_err:
                    print(f"[TIP ERROR] Welcome gift failed: {tip_err}")
        except Exception as e:
            print(f"[JOIN ERROR] Failure processing: {e}")

    async def send_vip_welcome_packet(self, user_id: str, username: str) -> None:
        try:
            await asyncio.sleep(1.0) 
            await self.highrise.send_whisper(user_id, f"👑 Welcome to Lifetime VIP, @{username}! Here are your exclusive commands:")
            await self.highrise.send_whisper(user_id, "🚀 Type: '!vip' to teleport up to the luxury lounge level.")
            await self.highrise.send_whisper(user_id, "⬇️ Type: '!down' to return immediately back to the main ground floor.")
        except Exception as e:
            print(f"[WHISPER ERROR] Failed instructions packet: {e}")

    async def on_whisper(self, user: User, message: str) -> None:
        if user.id == self.bot_id: return
        try:
            await self.highrise.send_whisper(user.id, "Come to the room if you want to talk or command with me!")
        except Exception as e:
            print(f"[WHISPER RESPOND] Failed: {e}")

    async def on_tip(self, sender: User, receiver: User, tip: Union[CurrencyItem, Item]) -> None:
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
            except Exception as e:
                print(f"[TIP PAYLOAD] Processing error: {e}")

    async def on_chat(self, user: User, message: str) -> None:
        # --- 👑 OWNER UTILITY COMMANDS ---
        if user.username.lower() == self.owner_username.lower():
            if message.lower().strip() == "!bal":
                try:
                    wallet_response = await self.highrise.get_wallet()
                    bot_gold = next((item.amount for item in wallet_response.content if item.type == "gold"), 0)
                    await self.highrise.send_whisper(user.id, f"💰 [VAULT BALANCE] {bot_gold} gold remains securely in reserve.")
                except Exception as e: print(f"[BALANCE FAIL] timeout: {e}")
                    
            elif message.lower().strip().startswith("!with"):
                try:
                    parts = message.lower().strip().split()
                    if len(parts) > 1:
                        raw_amount = parts[1].replace("g", "")
                        if raw_amount in ["1", "5", "10", "50", "100", "500", "1k", "5000", "10k"]:
                            await self.highrise.send_whisper(user.id, f"💸 [WITHDRAWAL] Executing {raw_amount}g bar transfer...")
                            await self.highrise.tip_user(user.id, f"gold_bar_{raw_amount}")
                except Exception as e: print(f"[WITHDRAWAL FAIL] Error: {e}")
                    
            elif message.lower().strip().startswith("!give "):
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
                except Exception as e: print(f"[GIFT FAIL] Error: {e}")

        # --- 💡 GENERAL PRIVATE COMMAND UTILITIES ---
        if message.lower().strip() == "!help":
            if user.username.lower() == self.owner_username.lower():
                await self.highrise.send_whisper(user.id, "⚡ [OWNER LOG] Commands: !bal | !with <amount> | !give @user <amount>")
            elif user.id in self.vip_users:
                await self.highrise.send_whisper(user.id, "💡 VIP Commands: Type '!vip' or '!down'.")
            else:
                await self.highrise.send_whisper(user.id, f"💡 Menu: Type '!vip' to verify access status. Tip 500g to unlock features!")
                
        elif message.lower().strip() == "!vip":
            if user.id in self.vip_users or user.username.lower() == self.owner_username.lower():
                try:
                    await self.highrise.send_whisper(user.id, "🚀 Teleporting up to luxury lounge...")
                    await self.highrise.teleport(user.id, random.choice(self.vip_spawn_points))
                except Exception as tp_err: print(f"[TP ERROR] {tp_err}")
            else:
                await self.highrise.send_whisper(user.id, "❌ Access Denied. Tip 500g or more to unlock.")

        elif message.lower().strip() == "!down":
            if user.id in self.vip_users or user.username.lower() == self.owner_username.lower():
                try:
                    await self.highrise.send_whisper(user.id, "⬇️ Returning back to the ground floor...")
                    await self.highrise.teleport(user.id, Position(27.0, 0.5, 34.0, facing="FrontRight"))
                except Exception as tp_down_err: print(f"[TP DOWN ERROR] {tp_down_err}")

# =====================================================================
# ⚙️ 3. RUNTIME PROCESS MANAGER
# =====================================================================
def launch_game_bot():
    """ Runs completely isolated inside its own process loop """
    ROOM_ID = os.environ.get("HIGHRISE_ROOM_ID", "6a28b5b000b6151bd4c9641e")
    API_TOKEN = os.environ.get("HIGHRISE_API_TOKEN", "43b31f6cce5c48257110021c11d9a509334e73b684836a545c0f67e33fc4ed92")
    
    from highrise.__main__ import main, BotDefinition
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    print("[BACKGROUND PROCESS] Launching Highrise SDK Listener...")
    try:
        bot_instance = SecurityRoomBot()
        bot_instance.owner_username = os.environ.get("BOT_OWNER_USERNAME", "sadi_key")
        
        definitions = [BotDefinition(bot_instance, ROOM_ID, API_TOKEN)]
        loop.run_until_complete(main(definitions=definitions))
    except Exception as err:
        print(f"
