"""
Highrise Room Management Bot (With Threaded Port Scan Fix & Auto-Reconnect Loop)
Target Room ID: 6a28b5b000b6151bd4c9641e
Developer: sadi_key
Fixes: Loops the execution block with 15s cooling windows to prevent ghost drops.
"""

import sys
import asyncio
import random
import os
import traceback
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer
from typing import Union
from highrise import BaseBot, User, Position, AnchorPosition
from highrise.models import SessionMetadata, CurrencyItem, Item

# --- 🚀 RECON-SAFE WEB PORT THREAD ---
class SilentServer(SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot hosting engine active 24/7.")

    def log_message(self, format, *args):
        pass

def start_background_web_server():
    try:
        port = int(os.environ.get("PORT", 10000))
        server = HTTPServer(('0.0.0.0', port), SilentServer)
        print(f"[SYSTEM LOG] Dedicated port server opened cleanly on channel: {port}")
        server.serve_forever()
    except Exception as e:
        print(f"[ERROR CATCH] Background web thread failed to bind: {e}")

# Fire up the port server immediately on a parallel system thread
web_thread = threading.Thread(target=start_background_web_server, daemon=True)
web_thread.start()


# --- 🤖 HIGHRISE BOT CORE ENGINE ---
class SecurityRoomBot(BaseBot):
    def __init__(self):
        super().__init__()
        self.vip_users = []      
        self.tipped_users = []   
        self.giveall_history = set()  
        self.owner_username = "sadi_key"
        self.owner_id = None  
        self.bot_id = None
        
        self.vip_spawn_points = [
            Position(26.75, 23.0, 23.35, facing="FrontRight"),
            Position(19.00070, 23.0, 33.99, facing="FrontRight"),
            Position(27.5, 23.0, 30.0, facing="FrontRight")
        ]

    async def on_start(self, session_metadata: SessionMetadata) -> None:
        self.bot_id = session_metadata.user_id
        try:
            self.owner_id = session_metadata.room_info.owner_id
            print(f"[SYSTEM LOG] Verified Room Owner ID: {self.owner_id}")
        except AttributeError:
            print("[SYSTEM LOG] Room owner metadata schema unavailable.")

        print(f"\n[SYSTEM LOG] Connection authorized successfully.")
        try:
            await self.highrise.chat("✨ Secure Room Bot is now online and active! ✨")
            asyncio.create_task(self.start_announcement_loop())
        except Exception as e:
            print(f"[ERROR CATCH] Core initialization failed: {e}")

    async def start_announcement_loop(self) -> None:
        while True:
            try:
                await asyncio.sleep(300)
                await self.highrise.chat(
                    "📢 Tip 500g to become permanent VIP! Invite your friends to this public hangout place "
                    "and have tips and fun. Apply for MOD DM @sadi_key ✨"
                )
            except Exception as e:
                print(f"[ERROR CATCH] Announcement skipped: {e}")

    async def on_user_join(self, user: User, position: Union[Position, AnchorPosition]) -> None:
        if user.id == self.bot_id or "bot" in user.username.lower():
            return
        if user.username.lower() == self.owner_username.lower():
            self.owner_id = user.id

        try:
            welcome_text = (
                f"👋 Welcome to the room @{user.username}! 🎉\n"
                f"💡 Type '!help' to view Guest Commands.\n"
                f"👑 Want permanent VIP? Tip the Bot 500g+ or support us by tipping the Jar! ❤️"
            )
            await self.highrise.chat(welcome_text)
            
            if user.id not in self.tipped_users:
                self.tipped_users.append(user.id) 
                try:
                    await asyncio.sleep(0.8)
                    await self.highrise.tip_user(user.id, "gold_bar_1")
                    await self.highrise.chat(f"🎉 @{user.username}, enjoy your 1g welcome bonus!")
                except Exception as tip_err:
                    print(f"[ERROR CATCH] Welcome tip failed: {tip_err}")
        except Exception as e:
            print(f"[ERROR CATCH] Fatal handling on user entry: {e}")

    async def send_vip_welcome_packet(self, user_id: str, username: str) -> None:
        try:
            await asyncio.sleep(1.0) 
            await self.highrise.send_whisper(user_id, f"👑 Welcome to Lifetime VIP, @{username}! Here are your exclusive commands:")
            await self.highrise.send_whisper(user_id, "🚀 Type: '!vip' to teleport up to the luxury lounge level.")
            await self.highrise.send_whisper(user_id, "⬇️ Type: '!down' to return immediately back to the main ground floor.")
        except Exception as e:
            print(f"[ERROR CATCH] Failed sending direct welcome instructions: {e}")

    async def on_whisper(self, user: User, message: str) -> None:
        if user.id == self.bot_id:
            return
        try:
            await self.highrise.send_whisper(user.id, "Come to the room if you want to talk or command with me!")
        except Exception as e:
            print(f"[ERROR CATCH] Whisper responder failed: {e}")

    async def on_tip(self, sender: User, receiver: User, tip: Union[CurrencyItem, Item]) -> None:
        if sender.id == self.bot_id:
            return

        if isinstance(tip, CurrencyItem):
            try:
                print(f"[TRANSACTION LOG] {sender.username} tipped {tip.amount}g to {receiver.username}")
                is_to_bot = (receiver.id == self.bot_id)
                is_to_owner = (receiver.id == self.owner_id or receiver.username.lower() == self.owner_username.lower())

                if is_to_bot or is_to_owner:
                    if tip.amount >= 500:
                        is_new = sender.id not in self.vip_users
                        if is_new:
                            self.vip_users.append(sender.id)
                            
                        await self.highrise.chat(
                            f"✨ 👑 [VIP PROMOTION] 👑 ✨\n"
                            f"Deep gratitude to @{sender.username} for the generous {tip.amount}g tip! "
                            f"LIFETIME VIP ACCESS granted successfully! Check your whispers for commands. 🚀"
                        )
                        if is_new:
                            await self.send_vip_welcome_packet(sender.id, sender.username)
                    else:
                        await self.highrise.chat(
                            f"✨ [ROOM CONTRIBUTION] ✨\n"
                            f"Thank you profoundly @{sender.username} for supporting our space with a {tip.amount}g tip! ❤️"
                        )
            except Exception as e:
                print(f"[ERROR CATCH] Core gratitude engine failed: {e}")

    async def on_chat(self, user: User, message: str) -> None:
        clean_message = message.lower().strip().replace(" ", "")
        print(f"[ROOM CHAT] {user.username}: {message}") 
        
        if user.username.lower() == self.owner_username.lower():
            if message.lower().strip() == "!bal":
                try:
                    wallet_response = await self.highrise.get_wallet()
                    bot_gold = 0
                    for item in wallet_response.content:
                        if item.type == "gold":
                            bot_gold = item.amount
                            break
                    await self.highrise.send_whisper(user.id, f"💰 [VAULT BALANCE] {bot_gold} gold remains securely in reserve.")
                except Exception as e:
                    print(f"[ERROR CATCH] Balance check timeout: {e}")
                    
            elif message.lower().strip().startswith("!with"):
                try:
                    parts = message.lower().strip().split()
                    if len(parts) > 1:
                        raw_amount = parts[1].replace("g", "")
                        if raw_amount in ["1", "5", "10", "50", "100", "500", "1k", "5000", "10k"]:
                            await self.highrise.chat(f"💸 [WITHDRAWAL] Transferring {raw_amount}g bar to Owner @{self.owner_username}...")
                            await self.highrise.tip_user(user.id, f"gold_bar_{raw_amount}")
                        else:
                            await self.highrise.send_whisper(user.id, "❌ Error: Use a valid Highrise gold bar size.")
                except Exception as e:
                    print(f"[ERROR CATCH] Vault cashout failed: {e}")
                    
            elif message.lower().strip().startswith("!give "):
                try:
                    parts = message.split()  
                    if len(parts) >= 3:
                        target_user = parts[1].replace("@", "").strip()
                        amount_str = parts[2].lower().replace("g", "")
                        
                        if amount_str in ["1", "5", "10", "50", "100", "500", "1k", "5000", "10k"]:
                            room_users = await self.highrise.get_room_users()
                            user_id_found = None
                            for room_user, pos in room_users.content:
                                if room_user.username.lower() == target_user.lower():
                                    user_id_found = room_user.id
                                    break
                            if user_id_found:
                                await self.highrise.chat(f"🎁 [GIFT] Gifting {amount_str}g straight to @{target_user}!")
                                await self.highrise.tip_user(user_id_found, f"gold_bar_{amount_str}")
                            else:
                                await self.highrise.send_whisper(user.id, f"❌ User @{target_user} not found.")
                except Exception as e:
                    print(f"[ERROR CATCH] Gift failed: {e}")

            elif message.lower().strip().startswith("!giveall "):
                try:
                    parts = message.lower().strip().split()
                    if len(parts) >= 2:
                        amount_str = parts[1].replace("g", "")
                        valid_bars = ["1", "5", "10", "50", "100", "500", "1k", "5000", "10k"]
                        if amount_str not in valid_bars:
                            await self.highrise.chat("❌ Choose a valid bar unit size.")
                            return
                        
                        await self.highrise.chat(f"📣 Distributing {amount_str}g to room...")
                        room_data = await self.highrise.get_room_users()
                        for room_user, pos in room_data.content:
                            if room_user.id == self.bot_id: continue
                            if room_user.id not in self.giveall_history:
                                try:
                                    self.giveall_history.add(room_user.id)
                                    await self.highrise.tip_user(room_user.id, f"gold_bar_{amount_str}")
                                    await self.highrise.chat(f"🎁 Sent {amount_str}g to @{room_user.username}!")
                                    await asyncio.sleep(0.8)
                                except Exception: pass
                except Exception as e:
                    print(f"[ERROR CATCH] Giveall failed: {e}")
                    
            elif message.lower().strip().startswith("!givevip "):
                try:
                    parts = message.split()
                    if len(parts) >= 2:
                        target_user = parts[1].replace("@", "").strip()
                        room_users = await self.highrise.get_room_users()
                        user_id_found = None
                        for room_user, pos in room_users.content:
                            if room_user.username.lower() == target_user.lower():
                                user_id_found = room_user.id
                                break
                        if user_id_found:
                            if user_id_found not in self.vip_users:
                                self.vip_users.append(user_id_found)
                            await self.highrise.chat(f"👑 @{target_user} has been promoted to Permanent VIP! 🚀")
                            await self.send_vip_welcome_packet(user_id_found, target_user)
                except Exception as e:
                    print(f"[ERROR CATCH] VIP promo failed: {e}")
                    
            elif message.lower().strip().startswith("!removevip "):
                try:
                    parts = message.split()
                    if len(parts) >= 2:
                        target_user = parts[1].replace("@", "").strip()
                        room_users = await self.highrise.get_room_users()
                        user_id_found = None
                        for room_user, pos in room_users.content:
                            if room_user.username.lower() == target_user.lower():
                                user_id_found = room_user.id
                                break
                        if user_id_found and user_id_found in self.vip_users:
                            self.vip_users.remove(user_id_found)
                            await self.highrise.chat(f"⚡ [VIP REVOKED] @{target_user} removed.")
                except Exception as e:
                    print(f"[ERROR CATCH] VIP removal failed: {e}")

        if clean_message == "hey!bot":
            try:
                single_reply = (
                    f"👋 Hey there @{user.username}! Welcome to our public hangout space! 🎉\n"
                    f"💡 Type '!help' to view the Guest Commands.\n"
                    f"👑 Want permanent VIP access? Tip the Bot 500g+ or support our room by tipping the Jar! ❤️"
                )
                await self.highrise.chat(single_reply)
                return
            except Exception as e:
                print(f"[ERROR CATCH] Greeting failed: {e}")

        if message.lower().strip() == "!help":
            if user.username.lower() == self.owner_username.lower():
                await self.highrise.chat("⚡ [OWNER] Commands: !bal | !with <amount> | !give @user <amount> | !giveall <amount>g | !givevip @user | !removevip @user")
            elif user.id in self.vip_users:
                await self.highrise.send_whisper(user.id, "💡 VIP Commands: Type '!vip' or '!down'.")
            else:
                await self.highrise.chat(f"💡 @{user.username} Guest Menu: Type '!vip' to check status. Tip 500g into the jar to claim permanent VIP features!")
                
        elif message.lower().strip() == "!vip":
            if user.id in self.vip_users or user.username.lower() == self.owner_username.lower():
                try:
                    await self.highrise.chat(f"🚀 Teleporting VIP @{user.username} up to the VIP Lounge Floor!")
                    chosen_point = random.choice(self.vip_spawn_points)
                    await self.highrise.teleport(user.id, chosen_point)
                except Exception as tp_err:
                    print(f"[ERROR CATCH] Teleport failed: {tp_err}")
            else:
                await self.highrise.send_whisper(user.id, "❌ Access Denied. Tip 500g or more to unlock.")

        elif message.lower().strip() == "!down":
            if user.id in self.vip_users or user.username.lower() == self.owner_username.lower():
                try:
                    await self.highrise.chat(f"⬇️ Sending @{user.username} back down!")
                    await self.highrise.teleport(user.id, Position(27.0, 0.5, 34.0, facing="FrontRight"))
                except Exception as tp_down_err:
                    print(f"[ERROR CATCH] Teleport down failed: {tp_down_err}")
            else:
                await self.highrise.send_whisper(user.id, "❌ Access Denied.")

# --- AUTOMATED CONTINUOUS RECONNECT GATEWAY ---
async def start_bot_loop():
    ROOM_ID = "6a28b5b000b6151bd4c9641e"
    API_TOKEN = "43b31f6cce5c48257110021c11d9a509334e73b684836a545c0f67e33fc4ed92"
    
    from highrise.__main__ import main, BotDefinition
    
    while True:
        print("[SYSTEM LOG] Launching core Highrise API connection sequence...")
        try:
            definitions = [BotDefinition(SecurityRoomBot(), ROOM_ID, API_TOKEN)]
            await main(definitions=definitions)
        except Exception as err:
            print(f"\n[NETWORK ALERT] Highrise gateway disconnected or closed by server: {err}")
        
        print("[SYSTEM LOG] Room connection dropped or room sleeping. Retrying handshake in 15 seconds...")
        await asyncio.sleep(15)

if __name__ == "__main__":
    try:
        asyncio.run(start_bot_loop())
    except KeyboardInterrupt:
        print("\n[SYSTEM LOG] Bot disconnected cleanly.")
    except Exception:
        print("\n=== FATAL API GATEWAY EXCEPTION ===")
        traceback.print_exc()
