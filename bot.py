import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta, timezone
from keep_alive import keep_alive
import os

# Запускаем сервер для keep-alive
keep_alive()

# Настройка intents
intents = discord.Intents.default()
intents.members = True
intents.voice_states = True  # важно для отслеживания мьютов

bot = commands.Bot(command_prefix="!", intents=intents)

# Словарь для хранения времени мьюта
muted_users = {}

# ID канала, куда перемещать пользователей
TARGET_CHANNEL_ID = 1475490692880138472  # замени на свой ID

# Проверка каждые 30 секунд
@tasks.loop(seconds=30)
async def check_muted_users():
    now = datetime.now(timezone.utc)
    for guild in bot.guilds:
        for vc in guild.voice_channels:
            for member in vc.members:
                if member.voice is None:
                    continue
                # Если пользователь замьютил себя
                if member.voice.self_mute:
                    if member.id not in muted_users:
                        muted_users[member.id] = now
                    else:
                        elapsed = now - muted_users[member.id]
                        if elapsed >= timedelta(minutes=5):
                            target_channel = guild.get_channel(1475490692880138472)
                            if target_channel:
                                try:
                                    await member.move_to(target_channel)
                                    print(f"Moved {member.name} due to 5+ min mute")
                                    del muted_users[member.id]
                                except Exception as e:
                                    print(f"Error moving {member.name}: {e}")
                else:
                    if member.id in muted_users:
                        del muted_users[member.id]

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    check_muted_users.start()

# Токен берём из переменной окружения
bot.run(os.environ["DISCORD_TOKEN"])
