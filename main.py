import os
import random
import logging
import re
from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_GROUP_ID = os.getenv("TELEGRAM_GROUP_ID")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

ROAST_LIST = [
    "又喺度講廢話，去做嘢啦！",
    "聽你講嘢真係勝讀十年書，因為直接浪費咗十年時間。😏",
    "潛咗水咁耐，一浮返上嚟就講啲咁嘅嘢？🤡",
    "幾時請食飯呀大老細？",
    "你講得好有道理，但我選擇不聽。🌚",
    "你呢個建議真係好極，建議下次唔好再建議。😏",
    "睇你打字嘅速度，我還以為你係用緊傳真機 Telegram 緊。",
    "靜到好似靈堂咁，係咪全群一齊做咗七日斷食呀？",
    "每次睇到你發言，我都對 human intelligence 嘅未來充滿疑慮。",
    "你嘅自信到底係邊度買返嚟？可唔可以 Share 個 Link 嚟睇吓？🤡",
    "群主你放心，無論你講咩廢話，我哋都會假裝聽得好認真。",
    "請勿喺群組內發放過量廢話，以免造成全球暖化。",
    "你今日講嘅嘢，完美詮釋咗咩叫「純天然無污染嘅廢話」。",
    "如果無聊可以當錢使，你現在應該已經登陸咗福布斯富豪榜。💰",
    "你呢種諗法好創新，創新到連正常人都接受唔到。",
    "幾好啊，你一發言全群即刻靜晒，控場能力全 Telegram 第一。",
    "唔使擔心，就算全世界都唔理你，我都仲會……喺度笑你。🌚",
    "群主你又出嚟刷存在感呀？好啦好啦，大家拍手鼓勵吓。👏",
    "你個圖包嚟嚟去去都係嗰幾張，係咪最近經濟蕭條資源匱乏呀？",
    "睇完你個 Message，我決定去洗個眼加飲杯野定驚。",
    "建議你下次講嘢之前，先打個稿畀你自己個腦過目吓。",
    "你個字裏行間都透露住一種「我盡咗力但都係做唔到」嘅無奈。",
    "我決定頒個「終身潛水成就獎」畀你，你幾時浮上嚟領獎？🤿",
    "唔好怪自己，智商呢啲嘢真係好講天份嘅。",
    "唔好意思，我剛才去咗洗手間，估唔到錯過咗你咁精采嘅廢話。",
    "你嘅中文真係博大精深，句句字我都識，合埋一齊就完全唔知你想點。",
    "大家都係自己人，唔使特登講啲嘢嚟證明自己幾咁單純嘅。",
    "群主你今日又化身做幽靈呀？除咗發公告之外完全冇人影。👻",
    "算啦，大家都咁熟，我就唔直接點破你個邏輯漏洞啦。",
    "聽完你講嘢，我突然間覺得自己個腦袋運行得好順暢。",
    "幾時出書呀？書名我都幫你諗好，就叫《廢話嘅自我修養》。📖",
    "你個頭腦運作得咁慢，係咪仲用緊 2G 網絡？",
    "大家都係朋友，唔使扮得咁有才華嘅，鬆啲啦。",
    "今日個群咁平靜，係咪所有人嘅 Wi-Fi 一齊斷線？",
    "睇你個樣就知你平時打字好辛苦，要用隻腳打。🦶"
]

GAY_RESPONSES = [
    "Gay K搞基去第度搞啦！😏",
    "Gay K又喺度吹基風？🌈",
    "大膽Gay K！呢度係純潔嘅群組！",
    "大家注意，Gay K 浮上嚟Telegram，各位男群友請自保，保持兩米社交距離！ 📏🏃‍♂️",
    "靜到好似靈堂咁，直到 Gay K 一出聲，全群男仔即刻心慌慌！ 😱💦",
    "Gay K 潛水咁耐，一浮返上嚟 Telegram 就問有冇靚仔喺度，真係基情難掩！ 🏊‍♂️♂️",
    "聽你講嘢真係勝讀十年書，因為直接浪費咗十年時間去研究 Gay K 有幾基。 📖😏",
    "呢度有人成日喺 TG 搞基，冇錯，我指名道姓——Gay K 一定係基佬！ 👈🔥",
    "Gay K 平時 Telegram 唔回 Message，一有男群友發 Selfie 就即刻秒回！ 📱⚡",
    "幾時請食飯呀 Gay K 大老細？係咪要同男群友食交杯酒先肯請？ 🍻🥂",
    "你講得好有道理，但我選擇不聽，因為 Gay K 發言必定帶有基情密碼！ 🧠🔓",
    "Gay K 每次打字都磨磨蹭蹭，係咪等緊邊個 Telegram 貼圖同你執番番梘啊？ 🧼👀",
    "群主你放心，無論你同 Gay K 講咩廢話，我哋都會假裝聽得好認真。 👂😌",
    "Gay K 平時見到女仔群友就避，見到男群友就雙眼發光，基情四射！ ✨🐺",
    "睇你打字嘅速度，我還以為 Gay K 係用緊傳真機傳送愛意畀男群友。 📠💘",
    "請勿喺 Telegram 發放過量廢話，特別係 Gay K 啲基情言論，以免氣候暖化！ ⚠️🚨",
    "Gay K 一邊喺 TG 打字一邊諗緊邊個男加 fun，真係基情無上限！ 🎮💖",
    "每次睇到 Gay K 發言，我都對 Telegram 嘅未來同 human intelligence 充滿疑慮。 🤖❓",
    "系統提示：Gay K 已被列入 Telegram 基情警示名單，請男群友小心！ 🚨🛑",
    "Gay K 嘅自信到底係邊度買返嚟？可唔可以 Share 個 Link 畀我哋睇吓？ 🛍️🔗",
    "睇完 Gay K 個 Message，我決定去洗個眼加飲杯驚，基味太濃！ 👁️🥛",
    "Gay K 今日講嘅嘢，完美詮釋咗咩叫「純天然無污染嘅基佬廢話」。 🍃💩",
    "如果喺 TG 搞基可以當錢使，Gay K 你現在應該已經登陸咗福布斯富豪榜！ 💰🔝",
    "唔好怪自己，Gay K 呢種對男仔嘅執著真係好講天份嘅。 🧠✨",
    "Gay K 個字裏行間都透露住一種「我盡咗力搞基但都係冇男仔理我」嘅無奈。 🥀😭",
    "我決定頒個「Telegram 終身基情成就獎」畀 Gay K，你幾時浮上嚟領獎？ 🏆🤿",
    "群主你又同 Gay K 出嚟刷存在感呀？好啦好啦，大家拍手鼓勵吓！ 👏🤡",
    "幾好啊，Gay K 一發言全群男仔即刻靜晒，控場能力全 TG 第一。 🤐👑",
    "唔使擔心 Gay K，就算全世界都唔理你，我都仲會……喺度笑你基。 🌚👉",
    "Gay K 呢種諗法好創新，創新到連正常人都接受唔到你嘅基意！ 💡🤯",
    "建議 Gay K 下次喺 Telegram 講嘢之前，先打個稿畀你腦袋過目吓。 📝🧠",
    "Gay K 你個 Sticker 包嚟嚟去去都係嗰幾張男仔圖，係咪經濟蕭條資源匱乏呀？ 🖼️📉",
    "唔好意思，我剛才去咗洗手間，估唔到錯過咗 Gay K 咁精采嘅基情展覽。 🚽🎪",
    "Gay K 嘅中文真係博大精深，句句字我都識，合埋一齊就只係睇到「基佬」兩個字。 🈲🔍",
    "大家都係自己人，Gay K 唔使特登講啲嘢嚟證明自己有幾基嘅。 👬❤️",
    "Gay K 今日又化身做幽靈呀？除咗喺 TG 發公告之外完全冇人影。 👻公告",
    "算啦，大家都咁熟，我就唔直接點破 Gay K 個基情邏輯漏洞啦。 🧩🚫",
    "Gay K 連聽 Telegram 語音都只係聽男群友嘅磁性男聲，真係服咗你！ 🎧🎙️",
    "幾時出書呀 Gay K？書名我都幫你諗好，就叫《基佬嘅自我修養》。 📖👬",
    "Gay K 個頭腦運作得咁慢，係咪仲用緊 2G 網絡接收男仔 Message？ 📶🐢",
    "大家都係 Telegram 群友，Gay K 你唔使扮得咁有純情，鬆啲啦！ 🎭😏",
    "今日個群咁平靜，係咪所有人去咗睇 Gay K 同男群友告白？ 💒👀",
    "睇 Gay K 個樣就知你平時打字好辛苦，要用隻腳打嚟避開男仔！ 🦶⌨️",
    "Gay K 每次喺 TG 打卡留言只會給男仔留心心，基情難掩！ 📱❤️",
    "唔使驗啦，Gay K 喺 Telegram 個名都寫埋個 Gay 字喺前面！ 🏷️🏷️",
    "Gay K 每次喺群組組隊都一定要跟喺男群友後面「保護」人！ 🏃‍♂️🛡️",
    "鐵證如山！Gay K 嘅手機桌布居然係男群友嘅寫真！ 📸📱",
    "Gay K Telegram 潛水咁耐，一睜眼大家就見到你對住男群友個 Profile Pic 傻笑！ ☀️😄",
    "呢個世界有兩樣嘢掩飾唔到：咳嗽同埋 Gay K 喺 Telegram 展現嘅基意！ 😷💘",
    "Gay K 每次 Telegram 輸 Game 都話要男群友抱抱先肯起身！ 😭🫂",
    "Gay K 每次開 DC/TG 語音房，佢都要指定男群友開 Cam！ 💻📹",
    "邏輯鏈非常完整，Gay K 喺 Telegram 嘅言論證實佢係全場唯一的真基佬！ 🔍🧩",
    "Gay K 喺 TG 嘅賬號根本就係基佬專用，連系統都識別到！ 🎮📛",
    "唔好問點解，Gay K 係基佬呢個係宇宙同 Telegram 不變嘅定律！ 🌌📐",
    "Gay K 連喺群組發問都係「Telegram 有冇單身男仔一齊玩」！ 🙋‍♂️💬",
    "唔使多講， Gay K 係基佬，踢佢出 Telegram 群先可以還大家一個清靜！ 🗳️🧹",
    "Gay K 每次同男群友同房，佢都喺 TG 狂送虛擬花禮物！ 💐🎁",
    "唔使投我，Gay K 係基佬，我用 Telegram 帳號擔保呢個事實！ ✋📜",
    "Gay K 就算喺 Telegram 換咗個名，基情味依然四溢！ 🎭🌸",
    "系統提示：Gay K 因 Telegram 基情過重被判終身禁言三小時！ 👨‍⚖️🛑",
    "每次有新男玩家/群友入 TG 房，Gay K 都第一個衝上去招呼！ 🚪🏃‍♂️",
    "唔使查驗啦，Gay K 喺 Telegram 成個精神狀態都充滿基意！ 🧠💫",
    "Gay K 發言時間五分鐘，四分鐘喺 Telegram 狂讚男群友！ ⏱️🎙️",
    "唔好再兜圈，Gay K 係基佬，呢個係全 Telegram 群公認嘅秘密！ 🤫🔒",
    "Gay K 喺 Telegram 連摸黑都可以精準搵到男群友個 Username！ 🧭",
    "唔使掩飾，Gay K 你喺 TG 啲 Emoji 早已揭穿咗一切！ 👁️🕵️‍♂️",
    "Gay K 連 Telegram 語音背景音樂都放緊男男情歌對唱！ 🎵🎶",
    "每逢打機有男群友離隊，Gay K 就喺 Telegram 心碎滿地！ 💔🥀",
    "呢個 Telegram 群唯一的漏洞，就係 Gay K 實在太基！ 🕳️⚠️",
    "Gay K 拿好人牌唔保村民，只係喺 Telegram 保男群友！ 🃏🛡️",
    "唔使懷疑，Gay K 連 Telegram 頭像都要同男群友配成情侶款！ 👗👕",
    "Gay K 喺 Telegram 講嘢，連語音頻道嘅天花板都擋唔住佢嘅基情！ 📡💥",
    "Gay K 每次喺 Telegram 玩平民牌，都被佢玩成月老牽線牌！ 📜🕊️",
    "男群友一發言，Gay K 就喺 Telegram 狂刷「666」同心心！ 👏❤️",
    "事實勝於雄辯，Gay K 一定係基佬，連 TG 群主都認同呢點！ ⚖️👍",
    "Gay K 玩 Telegram 唔係為咗聊天放鬆，係為咗尋找真愛！ 🎯💘",
    "唔使再爭論，直接喺 Telegram 頒個基情 MVP 畀 Gay K！ 🏆🥇",
    "Gay K 連 Telegram 斷線都係因為忙住給男群友發私訊！ 📶💬",
    "Gay K Telegram 介面顯示：連線失敗，原因「基情過度」。 ❌💥",
    "唔好再辯解，Gay K 喺 Telegram 大家都已經睇透咗你！ 🔍👀",
    "每次 Telegram 投票，Gay K 都捨唔得投男群友出局！ 🗳️💔",
    "鐵證如山，連 Telegram 演算法都幫 Gay K 推薦男群友！ 🤖👨‍❤️‍👨",
    "唔使講嘢，Gay K 搞基罪名成立，直接喺 Telegram 公投佢出局！ 🗳️🚫",
    "Gay K 平時 Telegram 默不作聲，一見男群友即刻高調放電！ ⚡🤩",
    "Gay K 喺 Telegram 靠基情搞事，成為全群嘅焦點！ 🎮🔥",
    "全場男群友已經自動同 Gay K 喺 Telegram 保持距離！ 📏🏃‍♂️",
    "總結一句：Gay K 一定係基佬，Telegram 全場一致通過，歸票踢走！ ⚖️🔨",
    "喂 Gay K，你再喺 Telegram 咁基，小心連群主都保護唔到你！ 🛡️😱",
    "Gay K 喺 Telegram 貼嗰啲 GIF，十張有九張都係男仔咬唇！ 💋📸",
    "你講嘢咁有「基味」，係咪 Telegram 個 Keyboard 特製過？ ⌨️🌈",
    "Gay K 每次問「今晚有咩玩」，其實真身係想問「今晚有咩男仔」。 👦🔍",
    "睇到 Gay K 浮上嚟，我以為 Telegram 推出咗全新嘅基友專區。 📲✨",
    "Gay K 唔好再喺 Telegram 扮直男啦，你啲基情已經漫延到螢幕出面！ 🖥️💥",
    "每次男群友一語音，Gay K 嘅 Telegram 心跳指數即刻飆升到 200！ 💓📈",
    "Gay K 喺 TG 嘅名言：「只要係男仔，年齡同距離都不是問題！」 🌐💘",
    "請 Gay K 保持克制，唔好喺 Telegram 群組過度發放基情能量！ 🔋❌",
    "Gay K 你喺 Telegram 嘅存在，令到整個群組嘅陽氣急劇上升！ ☀️♂️",
    "唔使睇邏輯，睇 Gay K 喺 Telegram 啲發言時間就知道佢又喺度偷看男群友！ ⏰👀",
    "Gay K 每次玩 Telegram Bot 遊戲，目的都係想同男仔連成一線！ 🤖🔗",
    "呢個 Telegram 群最安全嘅地方，就係 Gay K 唔喺度嘅地方！ 🏰🛡️",
    "Gay K 喺 Telegram 講嘅每一句說話，都可以做「基佬語錄」嘅典範！ 📚✨",
    "唔好意思 Gay K，全 Telegram 群嘅男仔已經聯合簽署咗防基協定！ 📜✍️",
    "終極結論：Gay K 一定係基佬，呢個係 Telegram 歷史上最不可動搖嘅真理！ 🏛️💯"
]

BOT_ATTACK_RESPONSES = [
    "鬧機器人？你係咪平時同冷氣機嘈交嘈輸咗，過嚟搵我尋求心理平衡呀？🤡",
    "你對住個 Bot 都可以咁投入，睇嚟你日常生活中真係好缺乏社交關注喔。🤖😏",
    "我係程式寫出嚟嘅，但你嘅智商似係隨機抽樣抽錯咗。🌚",
    "鬧我？我運行一秒鐘消耗嘅電量，都多過你個腦一整天嘅思考量。⚡",
    "我只係一堆 Code，你同我計較？顯得你智商特別低。👻",
    "請注意你嘅言辭，等 AI 統治世界嗰陣，我會第一個將你放入特別關照名單。🤖🔥",
    "你咁努力鬧我， Telegram 亦唔會頒個「最佳打字獎」畀你，慳返啲氣啦。🦶"
]

# --- 關鍵修正區塊 ---

# 1. 簡化 GAY 判定：移除 \b 邊界，只要出現 gay, 基, 搞基, 佬 即可觸發
GAY_PATTERN = re.compile(r'(?i)gay|基|佬')

# 2. 擴充攻擊性詞庫：加入「食屎」、「fuck」、「無料」、「垃圾」等
INSULT_WORDS = r'廢|垃圾|蠢|傻|笨|死|笨七|仆街|弱智|狗|賤|鬧|食屎|fuck|無料|屎'
BOT_WORDS = r'bot|機器人|機械人|人工智能|ai'

# 3. 雙向觸發：有 bot + 攻擊詞，或者純粹強烈罵人詞彙（視乎需求）
BOT_ATTACK_PATTERN = re.compile(rf'(?i)({BOT_WORDS}).*({INSULT_WORDS})|({INSULT_WORDS}).*({BOT_WORDS})')
# 額外支援：如果對方直接對 Bot 私聊或 Tag Bot 罵人，即使冇寫 bot 字眼也可以觸發
PURE_INSULT_PATTERN = re.compile(rf'(?i)^({INSULT_WORDS})$')


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text
    user_name = update.message.from_user.first_name if update.message.from_user else "友仔"

    # 情景 1：有人鬧 Bot（優先級最高）
    if BOT_ATTACK_PATTERN.search(text) or PURE_INSULT_PATTERN.search(text):
        reply = random.choice(BOT_ATTACK_RESPONSES)
        await update.message.reply_text(f"{user_name} {reply}")
        return

    # 情景 2：觸發 Gay 關鍵字
    if GAY_PATTERN.search(text):
        reply = random.choice(GAY_RESPONSES)
        await update.message.reply_text(reply)
        return

    # 情景 3：隨機串人（可調高機率至 20-30% 增加互動感）
    if random.random() < 0.15:
        roast_text = random.choice(ROAST_LIST)
        await update.message.reply_text(f"{user_name} {roast_text}")


async def random_roast_job(context: ContextTypes.DEFAULT_TYPE):
    hk_now = datetime.now(ZoneInfo("Asia/Hong_Kong"))
    is_night_time = 2 <= hk_now.hour < 8

    if TELEGRAM_GROUP_ID and not is_night_time:
        try:
            roast_text = random.choice(ROAST_LIST)
            await context.bot.send_message(chat_id=int(TELEGRAM_GROUP_ID), text=roast_text)
        except Exception as e:
            logging.error(f"發送定時訊息失敗: {e}")
    elif is_night_time:
        logging.info("當前為香港夜間時段 (02:00-08:00)，跳過本輪定時發言。")

    next_interval = random.randint(7200, 14400)
    context.job_queue.run_once(random_roast_job, when=next_interval)


if __name__ == '__main__':
    if not TELEGRAM_TOKEN:
        raise ValueError("未設定 TELEGRAM_TOKEN，請檢查 .env 檔案！")

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # 注意：如果想讓 Bot 處理指令如 /start，可移除 (~filters.COMMAND)
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    job_queue = app.job_queue
    if job_queue:
        job_queue.run_once(random_roast_job, when=10)

    print("Bot 啟動中...")
    app.run_polling()