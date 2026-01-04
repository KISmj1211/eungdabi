import os 
from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord import app_commands
import json
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "qa_data.json")
PROHIBITED_WORDS_FILE = os.path.join(BASE_DIR, "prohibited_words.json")

def load_qa_data():
    global qa_dict
    try:
        with open(DATA_FILE, 'r', encoding = "utf-8") as f:
            content = f.read().strip()
            if not content:
                qa_dict = {}
            else:
                qa_dict = json.loads(content)
            
    except FileNotFoundError:
        qa_dict = {}
    except json.JSONDecodeError:
        print(f"경고: {DATA_FILE} 파일의 JSON 형식이 올바르지 않습니다. 초기화합니다.")
        qa_dict = {}

def save_qa_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(qa_dict,f, ensure_ascii=False, indent = 2)

def load_prohibited_words():
    try:
        with open(PROHIBITED_WORDS_FILE, "r", encoding = "utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def contains_prohibited_word(text, prohibited):
    for word in prohibited:
        if word in text:
            return word
    return None
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix = "!", intents=intents)



@bot.event
async def on_ready():
    load_qa_data()

    print(f"봇 접속됨: {bot.user}")
    try: 
        synced = await bot.tree.sync()
        print(f"슬래시 명령 {len(synced)}개 등록됨")
    except Exception as e:
        print(f"슬래시 명령 등록 실패: {e}")

# qa_dict = {"1+1은?":"2입니다."}
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    if message.content.startswith("응답아"):
        question = message.content[4:].strip()
        answer = qa_dict.get(question)

        if answer:
            await message.channel.send(f"응답이: {answer}")
        else:
            await message.channel.send("응답이: 그런건 응답할 수 없습니다.")

@bot.tree.command(name="궁금증", description="응답이가 대답할 질문과 답을 등록해요.")
@app_commands.describe(question = "예: 1+1은?", answer = "예: 2입니다")
async def enroll_question(interaction: discord.Interaction, question: str,answer: str):
    prohibited = load_prohibited_words()
    bad_in_q = contains_prohibited_word(question, prohibited)

    if bad_in_q:
        await interaction.response.send_message(
            f"응답이: 질문에 금지된단어 '{bad_in_q}'가 포함되어 있어요",
            ephemeral = True
        )
        return
    
    bad_in_a = contains_prohibited_word(answer, prohibited)
    if bad_in_a:
        await interaction.response.send_message(
            f"응답이: 대답에 금지된단어 '{bad_in_a}'가 포함되어 있어요.",
            ephemeral= True
        )
        return
    if question in qa_dict:
        await interaction.response.send_message(f"응답이: '{question}'은 이미 등록된 질문이에요.",ephemeral= True)
        return
    qa_dict[question] = answer
    save_qa_data()
    await interaction.response.send_message(
        f"응답이: 질문 '{question}'에 대한 답변을 등록했어요!",
        ephemeral=True
    )
bot.run(TOKEN)