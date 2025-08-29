import yfinance as yf
import requests
from telegram import Bot
import asyncio
import time

# Cấu hình bot
BOT_TOKEN = "8176805125:AAEaZT4JrgRAdMfbAPqbq7XLWu2JZ0sGNL4"  # Thay bằng Bot Token từ BotFather
CHANNEL_ID = "-1002975080742"  # Thay bằng Channel ID (bắt đầu bằng -100)

# Hàm lấy giá cổ phiếu
def get_stock_price(symbol):
    try:
        stock = yf.Ticker(symbol)
        price = stock.history(period="1d")['Close'].iloc[-1]
        return round(price, 2)
    except Exception as e:
        return f"Lỗi khi lấy giá cổ phiếu {symbol}: {e}"

# Hàm lấy giá Bitcoin
def get_bitcoin_price():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
        response = requests.get(url)
        data = response.json()
        return round(data["bitcoin"]["usd"], 2)
    except Exception as e:
        return f"Lỗi khi lấy giá Bitcoin: {e}"

# Hàm gửi tin nhắn lên channel
async def send_message_to_channel(message):
    bot = Bot(token=BOT_TOKEN)
    try:
        await bot.send_message(chat_id=CHANNEL_ID, text=message)
        print("Tin nhắn đã được gửi!")
    except Exception as e:
        print(f"Lỗi khi gửi tin nhắn: {e}")

# Hàm chính
async def main():
    # Mã cổ phiếu (ví dụ: AAPL cho Apple, VNM cho Vinamilk)
    stock_symbol = "AAPL"  # Thay bằng mã cổ phiếu bạn muốn
    stock_price = get_stock_price(stock_symbol)
    btc_price = get_bitcoin_price()
    
    # Tạo tin nhắn
    message = f"📈 Giá cổ phiếu {stock_symbol}: ${stock_price}\n" \
              f"₿ Giá Bitcoin: ${btc_price}"
    
    # Gửi tin nhắn
    await send_message_to_channel(message)

# Chạy chương trình
if __name__ == "__main__":
    while True:
        asyncio.run(main())
        time.sleep(3600)  # Gửi mỗi giờ (3600 giây)