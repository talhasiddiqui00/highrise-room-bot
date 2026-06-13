"""
Highrise Room Management Bot
Target Room ID: 6a28b5b000b6151bd4c9641e
Developer: sadi_key
Fixes: Combined greeting message into a single block and linked it to on_user_join.
"""

import sys
import asyncio
import random
import traceback
from typing import Union
from highrise import BaseBot, User, Position, AnchorPosition
from highrise.models import SessionMetadata, CurrencyItem, Item

class SecurityRoomBot(BaseBot):
    def __init__(self):
        super().__init__()
        self.vip_users = []      
        self.tipped_users = []   
        self.giveall_history = set()  
        self.owner_username = "sadi_key"
        self.owner_id = None  
        self.bot_id = None
        
        # Exact VIP Floor spawn matrix nodes
        self.vip_spawn_points = [
            Position(26.75, 23.0, 23.35, facing="FrontRight"),
            Position(19.00070, 23.0, 33.99, facing="FrontRight"),
            Position(27.5, 23.0, 30.0, facing="FrontRight")
        ]

    async def on_start(self, session_metadata: SessionMetadata) -> None:
        """Executed immediately upon successful API gateway handshake."""
        self.bot_id = session_metadata.user_id
        
        try:
            self.owner_id = session_metadata.room_info.owner_id
            print(f"[SYSTEM LOG] Verified Room Owner ID: {self.owner_id}")
        except AttributeError:
            print("[SYSTEM LOG] Room owner metadata schema unavailable. Resolving dynamically.")

        print(f"\n[SYSTEM LOG] Connection authorized successfully.")
        print(f"[SYSTEM LOG] Active Bot Registration ID: {self.bot_id}")
        print(f"[SYSTEM LOG] Administrative rights restricted to: @{self.owner_username}")
        print("[SYSTEM LOG] Session status: ACTIVE. Press Ctrl+C to safely terminate.\n")
        
        try:
            await self.highrise.chat("✨ Secure Room Bot is now online and active! ✨")
            asyncio.create_task(self.start_announcement_loop())
        except Exception as e:
            print(f"[ERROR CATCH] Core initialization chat sequence failed: {e}")

    async def start_announcement_loop(self) -> None:
        """Automated background loop executing room announcements every 300 seconds (5 minutes)."""
        while True:
            try:
                await asyncio.sleep(300)
                await self.highrise.chat(
                    "📢 Tip 500g to become permanent VIP! Invite your friends to this public hangout place "
                    "and have tips and fun. Apply for MOD DM @sadi_key ✨"
                )
            except Exception as e:
                print(f"[ERROR CATCH] Periodic announcement loop skipped an iteration: {e}")

    async def on_user_join(self, user: User, position: Union[Position, AnchorPosition]) -> None:
        """Triggers immediately when a player logs into the room instance."""
        if user.id == self.bot_id or "bot" in user.username.lower():
            return
        
        if user.username.lower() == self.owner_username.lower():
            self.owner_id = user.id

        try:
            # Combined info message delivered instantly on join
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
                    print(f"[ERROR CATCH] Registration tip disbursement failed for {user.username}: {tip_err}")
        except Exception as e:
            print(f"[ERROR CATCH] Fatal handling on user entry sequence: {e}")

    async def send_vip_welcome_packet(self, user_id: str, username: str) -> None:
        """Dispatches an absolute breakdown of commands privately to upgraded users via whisper."""
        try:
            await asyncio.sleep(1.0) 
            await self.highrise.send_whisper(user_id, f"👑 Welcome to Lifetime VIP, @{username}! Here are your exclusive commands:")
            await self.highrise.send_whisper(user_id, "🚀 Type: '!vip' to teleport up to the luxury lounge level.")
            await self.highrise.send_whisper(user_id, "⬇️ Type: '!down' to return immediately back to the main ground floor.")
        except Exception as e:
            print(f"[ERROR CATCH] Failed sending direct welcome instructions: {e}")

    async def on_tip(self, sender: User, receiver: User, tip: Union[CurrencyItem, Item]) -> None:
        """Listens to all incoming gold transfers (Direct bot tips + Room Tip Jars)."""
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
                print(f"[ERROR CATCH] Core gratitude engine processing failure: {e}")

    async def on_chat(self, user: User, message: str) -> None:
        """Monitors structural room chat and processes permission-restricted text commands."""
        clean_message = message.lower().strip().replace(" ", "")
        print(f"[ROOM CHAT] {user.username}: {message}") 
        
        # --- OWNER CONTROL CONSOLE ---
        if user.username.lower() == self.owner_username.lower():
            if message.lower().strip() == "!bal":
                try:
                    wallet_response = await self.highrise.get_wallet()
                    bot_gold = 0
                    for item in wallet_response.content:
                        if item.type == "gold":
                            bot_gold = item.amount
                            break
                    await self.highrise.chat(f"💰 [VAULT BALANCE] {bot_gold} gold remains in reserve.")
                except Exception as e:
                    print(f"[ERROR CATCH] Balance validation response timeout: {e}")
                    
            elif message.lower().strip().startswith("!with"):
                try:
                    parts = message.lower().strip().split()
                    if len(parts) > 1:
                        raw_amount = parts[1].replace("g", "")
                        if raw_amount in ["1", "5", "10", "50", "100", "500", "1k", "5000", "10k"]:
                            await self.highrise.chat(f"💸 [WITHDRAWAL] Transferring {raw_amount}g bar to Owner @{self.owner_username}...")
                            await self.highrise.tip_user(user.id, f"gold_bar_{raw_amount}")
                        else:
                            await self.highrise.send_whisper(user.id, "❌ Error: Use a valid Highrise gold bar size (1, 5, 10, 50, 100, 500, 1k).")
                except Exception as e:
                    print(f"[ERROR CATCH] Direct vault cashout failed: {e}")
                    
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
                                await self.highrise.chat(f"🎁 [GIFT] Gifting {amount_str}g from reserves straight to @{target_user}!")
                                await self.highrise.tip_user(user_id_found, f"gold_bar_{amount_str}")
                            else:
                                await self.highrise.send_whisper(user.id, f"❌ User @{target_user} was not found in this room.")
                        else:
                            await self.highrise.send_whisper(user.id, "❌ Invalid value size. Must match exact bar units.")
                except Exception as e:
                    print(f"[ERROR CATCH] Arbitrary bonus payment failed: {e}")

            elif message.lower().strip().startswith("!giveall "):
                try:
                    parts = message.lower().strip().split()
                    if len(parts) >= 2:
                        amount_str = parts[1].replace("g", "")
                        
                        valid_bars = ["1", "5", "10", "50", "100", "500", "1k", "5000", "10k"]
                        if amount_str not in valid_bars:
                            await self.highrise.chat("❌ [ERROR] Choose a valid bar unit size: 1, 5, 10, 50, 100, 500, 1k")
                            return
                        
                        await self.highrise.chat(f"📣 [GIVEAWAY STARTING] Distributing {amount_str}g to all qualifying users in the room...")
                        
                        room_data = await self.highrise.get_room_users()
                        
                        for room_user, pos in room_data.content:
                            if room_user.id == self.bot_id:
                                continue
                            
                            if room_user.id not in self.giveall_history:
                                try:
                                    self.giveall_history.add(room_user.id)
                                    await self.highrise.tip_user(room_user.id, f"gold_bar_{amount_str}")
                                    await self.highrise.chat(f"🎁 Sent {amount_str}g to @{room_user.username}!")
                                    await asyncio.sleep(0.8)
                                except Exception as tip_err:
                                    print(f"[ERROR CATCH] Giveaway push failure on user {room_user.username}: {tip_err}")
                        
                        await self.highrise.chat("✅ [GIVEAWAY COMPLETE] All eligible users processed successfully.")
                except Exception as e:
                    print(f"[ERROR CATCH] Giveaway execution engine failed: {e}")
                    
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
                            await self.highrise.chat(f"👑 [VIP GRANTED] @{target_user} has been promoted to Permanent VIP status by the Owner! 🚀")
                            await self.send_vip_welcome_packet(user_id_found, target_user)
                        else:
                            await self.highrise.send_whisper(user.id, "❌ User is not present in this room environment.")
                except Exception as e:
                    print(f"[ERROR CATCH] Administrative database promotion failed: {e}")
                    
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
                            await self.highrise.chat(f"⚡ [VIP REVOKED] @{target_user} has been removed from VIP status.")
                        else:
                            await self.highrise.chat(f"⚡ System cleared entry logs for @{target_user}...")
                            self.vip_users = [u for u in self.vip_users if u != user_id_found]
                except Exception as e:
                    print(f"[ERROR CATCH] Administrative database removal failed: {e}")

        # --- CUSTOM 'HEY !BOT' GREETING INTERACTION ---
        if clean_message == "hey!bot":
            try:
                # Combined all lines into one single message package block
                single_reply = (
                    f"👋 Hey there @{user.username}! Welcome to our public hangout space! 🎉\n"
                    f"💡 Type '!help' to view the Guest Commands.\n"
                    f"👑 Want permanent VIP access? Tip the Bot 500g+ or support our room by tipping the Jar! ❤️"
                )
                await self.highrise.chat(single_reply)
                return
            except Exception as e:
                print(f"[ERROR CATCH] Custom greeting responder failed: {e}")

        # --- PUBLIC UTILITY COMMANDS & ELEVATION MATRIX ---
        if message.lower().strip() == "!help":
            if user.username.lower() == self.owner_username.lower():
                await self.highrise.chat("⚡ [OWNER] Commands: !bal | !withdraw <amount> | !give @user <amount> | !giveall <amount>g | !givevip @user | !removevip @user")
            elif user.id in self.vip_users:
                await self.highrise.send_whisper(user.id, "💡 VIP Commands: Type '!vip' to go to the lounge or '!down' to return to ground floor.")
            else:
                await self.highrise.chat(f"💡 @{user.username} Guest Menu: Type '!vip' to check status. Tip 500g into the jar to claim permanent VIP features!")
                
        elif message.lower().strip() == "!vip":
            if user.id in self.vip_users or user.username.lower() == self.owner_username.lower():
                try:
                    await self.highrise.chat(f"🚀 Teleporting VIP @{user.username} up to the VIP Lounge Floor!")
                    chosen_point = random.choice(self.vip_spawn_points)
                    await self.highrise.teleport(user.id, chosen_point)
                except Exception as tp_err:
                    print(f"[ERROR CATCH] VIP Upper Teleportation structure failure: {tp_err}")
            else:
                await self.highrise.send_whisper(user.id, "❌ Access Denied. Regular User. Tip 500g or more to unlock the VIP floor.")

        elif message.lower().strip() == "!down":
            if user.id in self.vip_users or user.username.lower() == self.owner_username.lower():
                try:
                    await self.highrise.chat(f"⬇️ Sending @{user.username} back down to the ground floor corner!")
                    await self.highrise.teleport(user.id, Position(10.0, 4.5, 10.0, facing="FrontRight"))
                except Exception as tp_down_err:
                    print(f"[ERROR CATCH] VIP Downward Teleportation structure failure: {tp_down_err}")
            else:
                await self.highrise.send_whisper(user.id, "❌ Access Denied. Command restricted strictly to VIP members.")

# --- ORCHESTRATION GATEWAY ---
if __name__ == "__main__":
    ROOM_ID = "6a28b5b000b6151bd4c9641e"
    API_TOKEN = "43b31f6cce5c48257110021c11d9a509334e73b684836a545c0f67e33fc4ed92"
    
    from highrise.__main__ import main, BotDefinition
    definitions = [BotDefinition(SecurityRoomBot(), ROOM_ID, API_TOKEN)]
    
    try:
        asyncio.run(main(definitions=definitions))
    except KeyboardInterrupt:
        print("\n[SYSTEM LOG] Shutdown signal intercepted. Bot disconnected cleanly.")
    except Exception:
        print("\n=== FATAL API GATEWAY EXCEPTION ===")
        traceback.print_exc()
