import os
import dotenv
import requests
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, ContextTypes, CallbackQueryHandler, CommandHandler

from engine import get_market_signal

# Loading env files
load_dotenv()

TOKEN = os.getenv('TELEGRAM_kEY') 
BitConnect_API_KEY = os.getenv('BitConnect_API_KEY')

# 2. THE DATA BRAIN
def get_btc_price():
    url = BitConnect_API_KEY
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for HTTP errors
        data = response.json()
        return data['bitcoin']['usd']
    except Exception as e:
        return f"Error: {e}"

# 3. TELEGRAM COMMANDS
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
   info_text = (
        "🤖 *AI Trader Bot is ONLINE*\n\n"
        "Welcome to the high\\-performance trading engine\\.\n\n"
        "📈 *Capabilities:*\n"
        "• Real\\-time BTC/USDT tracking\n"
        "• AI Sentiment Analysis\n"
        "• Automatic Risk Management\\.\n\n"
        "Click a button below to get an instant auto\\-reply\\."
   )

   keyboard = [
       [InlineKeyboardButton("📊 Check Live Price", callback_data="btn_price")],
       [InlineKeyboardButton("🔍 Analyze Market", callback_data="btn_analyze")]
   ]
   reply_markup = InlineKeyboardMarkup(keyboard)

   try:
       with open("Aitrade.png", "rb") as photo_file:
            await update.message.reply_photo(
                photo=photo_file,
                caption=info_text,
                reply_markup=reply_markup,  
                parse_mode=ParseMode.MARKDOWN_V2
            )
   except FileNotFoundError:
       # Safe fallback if image isn't found locally
       await update.message.reply_text(
           text=info_text,
           reply_markup=reply_markup,
           parse_mode=ParseMode.MARKDOWN_V2
       )

# ─── HANDLES THE INSTANT AUTO-REPLIES FROM INLINE BUTTONS ───
async def handle_inline_button_clicks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    # 1. Acknowledge the click immediately so the button stops "spinning"
    await query.answer()
    
    # 2. Redirect clicks to your existing logic safely
    if query.data == "btn_price":
        await price(update, context)
    elif query.data == "btn_analyze":
        await analyze(update, context)

async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    btc_val = get_btc_price()
    
    # Smart routing: Use message context if text command, else use callback query message layout
    target = update.message if update.message else update.callback_query.message
    
    # Safeguard: check if data is float/int before applying decimal layout formatters
    if isinstance(btc_val, (int, float)):
        await target.reply_text(f"📊 Current Bitcoin Price: ${btc_val:,.2f}")
    else:
        await target.reply_text(f"❌ Could not retrieve price.\n{btc_val}")

async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Smart routing: Works for both direct commands and button clicks
    target = update.message if update.message else update.callback_query.message

    try:
        signal, price_val, rsi_val = get_market_signal("BTC-USD")
        
        # Using standard Markdown here to avoid aggressive V2 character escaping failures 
        response = (
            f"📊 *Analysis for BTC/USD*\n\n"
            f"💰 *Price:* ${price_val}\n"
            f"📈 *RSI:* {rsi_val}\n"
            f"🤖 *Action:* {signal}\n\n"
            f"_Note: This is an AI-generated signal for testing._"
        )
        await target.reply_text(response, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        await target.reply_text(f"❌ Error generating market analysis: {e}")

# 4. START THE BOT
if __name__ == '__main__':
    print("🚀 Bot is starting... Press Ctrl+C to stop.")
    
    app = ApplicationBuilder().token(TOKEN)\
        .connect_timeout(30)\
        .read_timeout(30)\
        .write_timeout(30)\
        .pool_timeout(30)\
        .build()
    
    # Command handlers for typed slash instructions
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('price', price))
    app.add_handler(CommandHandler('analyze', analyze))
    
    # Callback query handler for inline button interactions
    app.add_handler(CallbackQueryHandler(handle_inline_button_clicks))
    
    app.run_polling(timeout=30)