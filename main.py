import sys
import asyncio
import traceback
from highrise import BaseBot, User, Position, AnchorPosition
from highrise.models import SessionMetadata, CurrencyItem, Item
from typing import Union
from aiohttp import web  # Added to prevent Render from sleeping

class MyBot(BaseBot):
    def __init__(self):
        super().__init__()
        self.vip_users = []      
        self.tipped_users = []   
        self.owner_username = "sadi_key"
        self.bot_id = None

    async def on_start(self, session_metadata: SessionMetadata) -> None:
        self.bot_id = session_metadata.user_id
        print(f"[SYSTEM LOG] Handshake successful. Bot ID registered: {self.bot_id}")
        try:
            await self.highrise.chat("✨ Secure Room Bot is now online and active! ✨")
            asyncio.create_task(self.start_announcement_loop())
        except Exception as e:
            print(f"[ERROR CATCH] Initial chat loop failed: {e}")

    async def start_announcement_loop(self):
        while True:
            try:
                await asyncio.sleep(120)
                await self.highrise.chat("📢 Tip 500g to become permanent VIP! Invite your friends to this public hangout place and have tips and fun. Apply for MOD DM @sadi_key ✨")
            except Exception as e:
                print(f"[ERROR CATCH] Announcement skipped: {e}")

    async def on_user_join(self, user: User, position: Union[Position, AnchorPosition]) -> None:
        if user.id == self.bot_id or "bot" in user.username.lower():
            return
        try:
            await self.highrise.chat(f"👋 Welcome to the room @{user.username}! ✨ Tip 500g for Lifetime VIP access!")
            if user.id not in self.tipped_users:
                self.tipped_users.append(user.id) 
                try:
                    await self.highrise.tip_user(user.id, "gold_bar_1")
                    await self.highrise.chat(f"🎉 @{user.username}, enjoy your 1g welcome bonus!")
                except Exception as tip_err:
                    print(f"[ERROR CATCH] Gold Tipping failed: {tip_err}")
        except Exception as e:
            print(f"[ERROR CATCH] Join handler error: {e}")

    async def on_tip(self, sender: User, receiver: User, tip: Union[CurrencyItem, Item]) -> None:
        if isinstance(tip, CurrencyItem):
            try:
                await self.highrise.chat(f"❤️ Thank you so much for the {tip.amount}g tip, @{sender.username}! ❤️")
                if tip.amount >= 500:
                    if sender.id not in self.vip_users:
                        self.vip_users.append(sender.id)
                        await self.highrise.chat(f"👑 LIFETIME VIP UNLOCKED! Congratulations @{sender.username}! 🚀 Double-tap the ground or type '!move' to go to the VIP roof deck!")
            except Exception as e:
                print(f"[ERROR CATCH] Tip error: {e}")

    async def on_user_move(self, user: User, destination: Union[Position, AnchorPosition]) -> None:
        if user.id == self.bot_id:
            return
        if user.id in self.vip_users or user.username.lower() == self.owner_username.lower():
            if isinstance(destination, Position) and destination.y < 2.0:
                try:
                    await self.highrise.teleport(user.id, Position(10.0, 15.0, 10.0, "FrontLeft"))
                except Exception as e:
                    print(f"[ERROR CATCH] Double-tap warp failed: {e}")

    async def on_chat(self, user: User, message: str) -> None:
        clean_message = message.lower().strip()
        
        if user.username.lower() == self.owner_username.lower():
            if clean_message == "!bal":
                try:
                    wallet_response = await self.highrise.get_wallet()
                    bot_gold = 0
                    for item in wallet_response.content:
                        if item.type == "gold":
                            bot_gold = item.amount
                            break
                    await self.highrise.chat(f"💰 [VAULT BALANCE] {bot_gold} gold remains in reserve.")
                except Exception as e:
                    print(f"[ERROR CATCH] Balance fetch failed: {e}")
            elif clean_message.startswith("!with"):
                try:
                    parts = clean_message.split()
                    if len(parts) > 1:
                        amount = int(parts[1].replace("g", ""))
                        await self.highrise.chat(f"💸 [WITHDRAWAL] Transferring {amount}g to Owner @{self.owner_username}...")
                        await self.highrise.tip_user(user.id, f"gold_bar_{amount}")
                except Exception as e:
                    print(f"[ERROR CATCH] Withdrawal failed: {e}")

        if clean_message == "!help":
            if user.username.lower() == self.owner_username.lower():
                await self.highrise.chat("⚡ [OWNER] Commands: !bal | !withdraw <amount> | !givevip @user | !removevip @user | !move")
            elif user.id in self.vip_users:
                await self.highrise.chat(f"💡 @{user.username} VIP Menu: !vip | !move. Double-tap the floor to jump!")
            else:
                await self.highrise.chat(f"💡 @{user.username} Guest Menu: !vip. Tip 500g into the room jar to unlock VIP!")

# --- MULTI-PORT RENDER KEEP ALIVE ENGINE ---
async def handle_ping(request):
    return web.Response(text="Bot Engine Operational")

async def run_services():
    room_id = "6a28b5b000b6151bd4c9641e"
    api_token = "43b31f6cce5c48257110021c11d9a509334e73b684836a545c0f67e33fc4ed92"
    
    from highrise.__main__ import main, BotDefinition
    definitions = [BotDefinition(MyBot(), room_id, api_token)]
    
    # Setup dummy background web port so Render remains active
    app = web.Application()
    app.router.add_get('/', handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 10000)
    await site.start()
    print("[SYSTEM LOG] Local port gateway mapped. Free tier anti-sleep active.")

    try:
        await main(definitions=definitions)
    except Exception:
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_services())
