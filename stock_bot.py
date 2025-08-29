import yfinance as yf
import requests
from telegram import Bot
import asyncio
import time
from datetime import datetime
import pytz

# Cấu hình bot
BOT_TOKEN = "8176805125:AAEaZT4JrgRAdMfbAPqbq7XLWu2JZ0sGNL4"
CHANNEL_ID = "-1002975080742"

# Danh sách mã cổ phiếu VN30
VN30_STOCKS = [
    "ACB.VN", "BCM.VN", "BID.VN", "BVH.VN", "CTG.VN", "FPT.VN", "GAS.VN",
    "GVR.VN", "HDB.VN", "HPG.VN", "MBB.VN", "MSN.VN", "MWG.VN", "PLX.VN",
    "POW.VN", "SAB.VN", "SHB.VN", "SSB.VN", "SSI.VN", "STB.VN", "TCB.VN",
    "TPB.VN", "VCB.VN", "VHM.VN", "VIC.VN", "VJC.VN", "VNM.VN", "VPB.VN",
    "VRE.VN", "LPB.VN"
]

# Hàm kiểm tra kết nối Telegram
async def check_telegram_connection():
    try:
        bot = Bot(token=BOT_TOKEN)
        await bot.get_me()
        return True
    except Exception as e:
        print(f"Lỗi kết nối Telegram: {e}")
        with open("C:\\Dell\\bot_log.txt", "a", encoding="utf-8") as f:
            f.write(f"Lỗi kết nối Telegram: {e}\n")
        return False

# Hàm lấy giá cổ phiếu
def get_stock_prices(symbols):
    prices = []
    for symbol in symbols:
        try:
            stock = yf.Ticker(symbol)
            price = stock.history(period="1d")['Close'].iloc[-1]
            prices.append(f"{symbol.replace('.VN', '')}: {round(price, 2)} VND")
        except Exception as e:
            prices.append(f"Lỗi khi lấy giá {symbol}: {e}")
    return prices

# Hàm lấy giá các đồng coin
def get_crypto_prices(coins):
    try:
        coin_ids = ",".join(coins)
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_ids}&vs_currencies=usd"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        prices = []
        for coin in coins:
            if coin in data and "usd" in data[coin]:
                prices.append(f"{coin.capitalize()}: ${data[coin]['usd']:.2f}")
            else:
                prices.append(f"Lỗi khi lấy giá {coin}")
        return prices
    except Exception as e:
        return [f"Lỗi khi lấy giá coin: {e}"]

# Hàm gửi tin nhắn lên channel
async def send_message_to_channel(message):
    bot = Bot(token=BOT_TOKEN)
    for attempt in range(5):
        try:
            await bot.send_message(chat_id=CHANNEL_ID, text=message)
            log_message = f"Tin nhắn đã được gửi lúc {datetime.now(pytz.timezone('Asia/Ho_Chi_Minh'))}!"
            print(log_message)
            with open("C:\\Dell\\bot_log.txt", "a", encoding="utf-8") as f:
                f.write(log_message + "\n")
            return
        except Exception as e:
            log_message = f"Lỗi khi gửi tin nhắn (thử {attempt + 1}/5): {e}"
            print(log_message)
            with open("C:\\Dell\\bot_log.txt", "a", encoding="utf-8") as f:
                f.write(log_message + "\n")
            if attempt < 4:
                await asyncio.sleep(20)
            else:
                print("Không thể gửi tin nhắn sau 5 lần thử.")

# Hàm kiểm tra thời gian
def is_time_in_range(start_hour, start_minute, end_hour, end_minute):
    vn_tz = pytz.timezone("Asia/Ho_Chi_Minh")
    now = datetime.now(vn_tz)
    current_time = now.hour * 60 + now.minute
    start_time = start_hour * 60 + start_minute
    end_time = end_hour * 60 + end_minute
    return start_time <= current_time <= end_time

# Hàm tính thời gian chờ đến mốc 15 phút tiếp theo
def wait_for_next_15_minute_mark():
    vn_tz = pytz.timezone("Asia/Ho_Chi_Minh")
    now = datetime.now(vn_tz)
    minutes = now.minute
    seconds = now.second
    # Tính phút còn lại để đến mốc 15 phút tiếp theo (0, 15, 30, 45)
    next_mark = ((minutes // 15) + 1) * 15
    if next_mark == 60:
        next_mark = 0
    seconds_to_wait = (next_mark - minutes) * 60 - seconds
    if seconds_to_wait < 0:
        seconds_to_wait += 3600  # Chuyển sang giờ tiếp theo
    return seconds_to_wait

# Hàm chính
async def main():
    # Kiểm tra kết nối Telegram
    if not await check_telegram_connection():
        print("Không thể kết nối đến Telegram. Bỏ qua lần gửi này.")
        return
    
    # Danh sách coin
    crypto_coins = ["bitcoin", "ethereum", "solana", "binancecoin", "cardano", "avalanche-2", "chainlink", "ripple"]
    
    # Kiểm tra thời gian và gửi tin nhắn phù hợp
    message = ""
    if is_time_in_range(5, 30, 22, 30):  # 5:30 - 22:30: Giá coin
        crypto_prices = get_crypto_prices(crypto_coins)
        message += "💰 Giá các đồng coin:\n" + "\n".join(crypto_prices)
    if is_time_in_range(9, 15, 14, 30):  # 9:15 - 14:30: Giá VN30
        stock_prices = get_stock_prices(VN30_STOCKS)
        message += ("\n\n" if message else "") + "📈 Giá cổ phiếu VN30:\n" + "\n".join(stock_prices)
    
    # Gửi tin nhắn nếu có nội dung
    if message:
        await send_message_to_channel(message)
    else:
        log_message = f"Không gửi tin nhắn: Ngoài khung giờ quy định, hiện tại {datetime.now(pytz.timezone('Asia/Ho_Chi_Minh'))}"
        print(log_message)
        with open("C:\\Dell\\bot_log.txt", "a", encoding="utf-8") as f:
            f.write(log_message + "\n")

# Chạy chương trình
if __name__ == "__main__":
    while True:
        try:
            # Chờ đến mốc 15 phút tiếp theo
            sleep_time = wait_for_next_15_minute_mark()
            print(f"Chờ {sleep_time} giây đến mốc 15 phút tiếp theo...")
            time.sleep(sleep_time)
            asyncio.run(main())
        except Exception as e:
            log_message = f"Lỗi chính: {e}"
            print(log_message)
            with open("C:\\Dell\\bot_log.txt", "a", encoding="utf-8") as f:
                f.write(log_message + "\n")
            time.sleep(60)  # Chờ 1 phút nếu lỗi