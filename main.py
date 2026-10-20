import discord, datetime, time
from discord import app_commands
from discord.ext import commands, tasks
import logging
from dotenv import load_dotenv
import os
from datetime import datetime as dt
import random, string
from discord.ui import View, button
import psutil
import socket
import json


intents = discord.Intents.default()
intents.reactions = True
intents.members = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True

bot = commands.Bot(command_prefix="a!", intents=intents)

bot.launch_time = datetime.datetime.now(datetime.UTC) # This is for the uptime part of the stats command


# Sends a message in the terminal when the bot goes online
@bot.event
async def on_ready():
    on_start_ping = round(bot.latency * 1000)
    print(f"{bot.user.name} is online!\n My ping is {on_start_ping} ms!")
    #try:
     #   synced = await bot.tree.sync()
      #  print(f"Synced {len(synced)} command(s)")
    #except Exception as e:
     #   print(f"Error syncing commands: {e}")

@bot.event
async def on_message(message):
    with open('config.json', 'r') as file:
        data = json.load(file)

    server = str(message.author.guild.id)
    guild = data[server]
    channel = guild['Honeypot Channel']

    if message.channel.id == channel:
        if message.author.bot:
            await message.delete()
            return
        else:
            await message.delete()
            invite = guild['Invite']
            try:
                await message.author.send(f"You have been banned from {message.author.guild.name} for typing in the honeypot channel.\nIf you would like to appeal, go to https://appeal.gg/{invite}")
                dm_status=("A DM was Sent")
            except:
                dm_status=("No DM Sent")
            await message.author.ban(reason=f"User was banned from {message.author.guild.name} for typing in the honeypot channel, <#{channel}> ({dm_status})")

    await bot.process_commands(message)

# This bans users if they grab a honeypot role
@bot.event
async def on_member_update(before, after):
    with open('config.json', 'r') as file:
        data = json.load(file)

    server = str(after.guild.id)
    guild = data[server]
    honeypot = guild['Honeypot Role']
    invite = guild['Invite']

    honey_pot = discord.utils.get(after.guild.roles, id=honeypot)
    if honey_pot in after.roles and honey_pot not in before.roles:
        try:
            await before.send(f"You were banned from {before.guild.name} for grabbing the Honeypot Role.\nIf you would like to appeal, go to https://appeal.gg/{invite}")
            dm_status = ("A DM was sent")
        except:
                    dm_status = ("A DM was not Sent")

        await after.ban(reason = f"User grabbed the Honeypot role ({dm_status})")
        return

# This shows you your bots uptime and ping, (prefix)ping is a separate command, though
@bot.command()
@commands.cooldown(1, 15, commands.BucketType.user) # this prevents the command from being spammed
async def stats(ctx):
    delta_uptime = datetime.datetime.now(datetime.UTC) - bot.launch_time
    hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    latency = round(bot.latency * 1000)
    days, hours = divmod(hours, 24)

    embed = discord.Embed(title=f"{bot.user.name}'s stats", color=discord.Color.pink())
    embed.add_field(name="Ping:", value=f"{latency}ms")
    embed.add_field(name="Uptime:", value=f"{days}d, {hours}h, {minutes}m, {seconds}s")

    await ctx.message.reply(embed=embed)


# Command shows you the ping of your bot
@bot.command()
@commands.cooldown(1, 5, commands.BucketType.user) # this prevents the command from being spammed
async def ping(ctx):
    latency = round(bot.latency * 1000)
    await ctx.message.reply(f"Pong! {latency} ms")


# This shows the server's CPU and RAM usage
@app_commands.command(name="server", description="Check the server's CPU & RAM Usage + other stuff")
async def server(interaction: discord.Interaction):
    if interaction.user.id == 908055723659898902:
        ram = psutil.virtual_memory()

        delta_uptime = datetime.datetime.now(datetime.UTC) - bot.launch_time
        hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        latency = round(bot.latency * 1000)
        days, hours = divmod(hours, 24)

        hostname = socket.gethostname()
        IPAddr = socket.gethostbyname(hostname)

        embed = discord.Embed(title="Aurora", color=discord.Color.pink())
        embed.add_field(name="Host", value=hostname)
        embed.add_field(name="IPv4", value=IPAddr)
        embed.add_field(name="CPU", value=f"{psutil.cpu_percent(interval=1)}%")
        embed.add_field(name="RAM(%)", value=f"{ram.percent}%")
        embed.add_field(name="RAM(GB)", value=f"{round(ram.used / 1e9, 2)}/8 GB")
        embed.add_field(name="Uptime", value=f"{days}d, {hours}h, {minutes}m, {seconds}s")
        embed.add_field(name="Ping", value=f"{latency} ms")
        await interaction.response.send_message(embed = embed, ephemeral=True)
    else:
        await interaction.response.send_message("You aren't Lilly", ephemeral=True)

# If a command is on cooldown, it'll display this message
@bot.event
async def on_command_error(ctx, error):
    latency = round(bot.latency * 1000)
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.message.reply(f'This command is on cooldown, you can use it in {round(error.retry_after, 2)} seconds')
        print(f"{ctx.author.name} // {ctx.author.id} is spamming the {ctx.command.name} command || My ping is currently {latency}ms\nhttps://discord.com/channels/{ctx.guild.id}/{ctx.channel.id}/{ctx.message.id}")


bot.tree.add_command(server)


# This lets the bot run
bot.run(token, log_handler=handler, log_level=logging.DEBUG)
