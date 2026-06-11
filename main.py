import threading
from flask import Flask
from highrise import BaseBot, User, Position, AnchorPosition
from highrise.models import SessionMetadata, CurrencyItem, Item
from typing import Union

# --- TINY BACKGROUND WEB SERVER FOR RENDER ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive and running 24/7!"

def run_web_server():
    # Render requires port 10000 by default
    app.run(host='0.0.0.0', port=10000)

# --- YOUR HIGHRISE BOT CODE ---
class MyBot(BaseBot):
    def __init__(self):
        super().__init__()
        self.vip_users = []
        self.tipped_users = []
        # ⚠️ CRITICAL: Replace this with your exact Highrise username
        self.owner_username = "sadi_key"

    async def on_start(self, session_metadata: SessionMetadata) -> None:
        print(f"Bot is online! Owner restricted to: {self.owner_username}")
        await self.highrise.chat("Hello Highrise! Secure Room Bot is now active.")

    async def on_user_join(self, user: User, position: Union[Position, AnchorPosition]) -> None:
        await self.highrise.chat(f"Welcome to the room @{user.username}! ✨ Tip 500g for Lifetime VIP access!")
        if user.id not in self.tipped_users:
            try:
                await self.highrise.tip_user(user.id, "gold_bar_1")
                self.tipped_users.append(user.id) 
                await self.highrise.chat(f"🎉 Enjoy your 1g welcome bonus, @{user.username}!")
            except Exception as e:
                print(f"Failed to tip {user.username}: {e}")

    async def on_tip(self, sender: User, receiver: User, tip: Union[CurrencyItem, Item]) -> None:
        if isinstance(tip, CurrencyItem):
            if tip.amount >= 500:
                if sender.id not in self.vip_users:
                    self.vip_users.append(sender.id)
                    await self.highrise.chat(f"🎉 LIFETIME VIP UNLOCKED @{sender.username}! Type '!vip' to go up! 🚀")
            else:
                await self.highrise.chat(f"Thank you for the {tip.amount}g tip, @{sender.username}! ❤️")

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
                    await self.highrise.chat(f"💰 Balance Report: {bot_gold} gold remains.")
                except Exception as e:
                    print(f"Balance error: {e}")
            elif clean_message.startswith("!with"):
                try:
                    parts = clean_message.split()
                    if len(parts) > 1:
                        amount = int(parts[1].replace("g", ""))
                        await self.highrise.chat(f"Processing transfer of {amount}g to owner...")
                        await self.highrise.tip_user(user.id, f"gold_bar_{amount}")
                except Exception as e:
                    print(f"Withdrawal failed: {e}")

        if clean_message == "!vip":
            if user.id in self.vip_users:
                await self.highrise.teleport(user.id, Position(5.0, 15.0, 5.0, "FrontLeft"))
            else:
                await self.highrise.send_whisper(user.id, "❌ Access Denied. Tip 500g to unlock.")

# --- LAUNCH BOTH AT THE SAME TIME ---
if __name__ == "__main__":
    # Start Flask web server in a side thread so it doesn't block the bot
    threading.Thread(target=run_web_server, daemon=True).start()
    
    # Run the Highrise Bot directly using the framework runner
    from highrise.__main__ import arun, main
    import sys
    
    # We simulate your terminal command parameters directly inside the code
    room_id = "6a28b5b000b6151bd4c9641e"
    api_token = "43b31f6cce5c48257110021c11d9a509334e73b684836a545c0f67e33fc4ed92"
    bot_definition = f"main:MyBot"
    
    sys.argv = ["highrise", bot_definition, room_id, api_token]
    arun(main())