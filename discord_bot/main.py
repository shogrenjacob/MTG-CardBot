
import discord
import os
import requests
from discord.ext import commands
from dotenv import load_dotenv

intents = discord.Intents.all()
intents.members = True

load_dotenv()

# Give the bot a prefix to listen for commands. Will respond to !{command name}
client = commands.Bot(command_prefix='!', intents=intents)

# Discord Events-----------------------------------------------------------------------------------

#Console statement to show when bot is booted
@client.event
async def on_ready():
    print("Bot is ready")
    print("------------")

#Makes sure that the command given by user exists
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"ERROR: {error}. Use !usage to view a list of supported commands")

# Discord Commands----------------------------------------------------------------------------------

#Displays a list of valud commands to user
@client.command()
async def usage(ctx):
    command_list = """-----Commands-----\nNOTE: All commands require exact spelling but are case insensitive
------------------------------------------------------------------------------------------
!card (card name) - Shows an image of the specified card.
------------------------------------------------------------------------------------------
!legalities (card name) - Shows all formats and whether or not the specified card is legal in each format.
------------------------------------------------------------------------------------------
!legal (format) (card name) - Shows whether or not a card is legal in the specified format.
------------------------------------------------------------------------------------------
!price (card name) - Shows the price of the given card in USD, EUR, and MTGO Tix.
------------------------------------------------------------------------------------------
"""
    await ctx.send(command_list)

#Given a card name, returns an image of the card specified to show users card info
@client.command()
async def card(ctx, *, card_name: str):

    formatted_card_name = card_name.replace(' ', '+')
    response = requests.get("https://api.scryfall.com/cards/named?fuzzy=" + formatted_card_name + "&format=image")

    if response.status_code == 200:
        await ctx.send("https://api.scryfall.com/cards/named?fuzzy=" + formatted_card_name + "&format=image")
    elif response.status_code == 404:
        await ctx.send("Card not found, ensure your spelling is correct")
    else:
        await ctx.send(f"An error occured, status code: {response.status_code}")

#Handles missing arguments when user calls the !card command
@card.error
async def card_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"ERROR: {error} Ensure that you are formatting your command as - !card (card name)")

#Given a card name, returns a list of all MTG formats and whether or not the given card is legal in that format
@client.command()
async def legalities(ctx, *, card_name: str):
    formatted_card_name = card_name.replace(' ', '+')
    response = requests.get("https://api.scryfall.com/cards/named?fuzzy=" + formatted_card_name)
    
    if response.status_code == 200:
        data = response.json()
        legalities = data.get("legalities")
        name = data.get("name")
        answer = f"-----{name}-----\n"

        for format, legality in legalities.items():
            if legality == "not_legal":
                answer = answer + f"{format}: not legal\n"
            else:
                answer = answer + f"{format}: {legality}\n"
        await ctx.send(answer)
    elif response.status_code == 404:
        await ctx.send("Card not found, ensure your spelling is correct")
    else:
        print(f"Failed to fetch data: {response.status_code}")
        await ctx.send(f"An error occured, status code: {response.status_code}")

#Handles missing argument exception for !legalities command
@legalities.error
async def legalities_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"ERROR: {error} Ensure that you are formatting your command as - !legalities (card name)")

#Given a specific card and format, return whether or not the given card is legal in the given format
@client.command()
async def legal(ctx, format: str, *, card_name: str):
    formatted_card_name = card_name.replace(' ', '+')
    formatted_format = format.lower().replace(' ', '')
    response = requests.get("https://api.scryfall.com/cards/named?fuzzy=" + formatted_card_name)

    if response.status_code == 200:
        data = response.json()
        legal_in_format = data.get("legalities").get(f"{formatted_format}")
        name = data.get("name")

        if legal_in_format == "legal":
            await ctx.send(f"{name} is legal in {format}")
        elif legal_in_format == "not_legal":
            await ctx.send(f"{name} is not legal in {format}")
        else:
            await ctx.send("An error has occured, check the spelling of the format you provided")
    elif response.status_code == 404:
        await ctx.send("Card not found, ensure your spelling is correct")
    else:
        print(f"Failed to fetch data: {response.status_code}")
        await ctx.send(f"An error occured, status code: {response.status_code}")

#Handles missing argument exception for !legal command
@legal.error
async def legal_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"ERROR: {error} Ensure that you are formatting your command as - !legal (format) (card name)")

#Given a card, return the current price of the card in USD, EUR, and MTG Online TIX. Also returns links to buy the card online
@client.command()
async def price(ctx, *, card_name: str):
    formatted_card_name = card_name.replace(' ', '+')
    response = requests.get("https://api.scryfall.com/cards/named?fuzzy=" + formatted_card_name)

    if response.status_code == 200:
        data = response.json()
        name = data.get("name")
        price_usd = data.get("prices").get("usd")
        price_eur = data.get("prices").get("eur")
        tix = data.get("prices").get("tix")
        tcg_player = data.get("purchase_uris").get("tcgplayer")
        card_market = data.get("purchase_uris").get("cardmarket")
        card_hoarder = data.get("purchase_uris").get("cardhoarder")
        answer = f"-----{name} Prices-----\nUSD: ${price_usd}\nEUR: €{price_eur}\nTIX: {tix}\n\n-----Buy Online-----\nTCG Player: {tcg_player}\nCard Market: {card_market}\nCard Hoarder: {card_hoarder}"
        await ctx.send(answer)
    elif response.status_code == 404:
        await ctx.send("Card not found, ensure your spelling is correct")
    else:
        print(f"Failed to fetch data: {response.status_code}")
        await ctx.send(f"An error occured, status code: {response.status_code}")    

#Handles missing argument exception for !price command
@price.error
async def price_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"ERROR: {error} Ensure that you are formatting your command as - !price (card name)")

#Runs the bot using discord bot token from account
client.run(os.getenv('token'))

