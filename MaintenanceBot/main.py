from translate_funcs import extractURL, translate_text, translate_url, translate_image
from al_maintenance import getTweets, getStatus
from discord.ext import commands
from dotenv import load_dotenv
import discord
import os


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="?", intents=intents)


@bot.event
async def on_ready():
    print(f'{bot.user} is connected to the following discord servers:')
    for guild in bot.guilds:
        print(f'{guild.name} (id:{guild.id})')


@bot.command(name='maintenance', help='Tells you the current maintenance status')
async def getMaintenance(ctx):
    status = getStatus(getTweets('AzurLane_EN', 25))
    await ctx.send(status)


@bot.command(name='translate', help='Translates text and images')
async def getTranslation(ctx):

    # split URLS and text
    url, text = extractURL(ctx.message.content)

    # TEXT INPUT
    text = [item for item in text.split(' ') if item != '']
    if len(text) > 1:
        await ctx.send(f"```Text:\n{translate_text(text)}```")

    # URL INPUT
    i = 1
    if len(url) > 0:
        text = translate_url(url)
        for translation in text:
            await ctx.send(f"```Image {i} (URL):\n{translation}```")
            i += 1

    # IMAGE INPUT
    for image in ctx.message.attachments:
        img_bytes = await image.read()
        text = translate_image(img_bytes)
        await ctx.send(f"```Image {i}:\n{text}```")
        i += 1

    # NO INPUT
    if ctx.message.content.strip() == "?translate" and not ctx.message.attachments:
        await ctx.send('```No input text or images detected.```')

bot.run(TOKEN)
