import random
import discord
from discord.ext import commands
from numpy import number
from settings import *

client = commands.Bot(command_prefix='$')

@client.event
async def on_ready():
    print(f'{client.user.name} has connected to Discord!')


@client.command()
@commands.has_role('deception')
async def clear(ctx, amount=10):
    await ctx.channel.purge(limit=amount)

@client.command(aliases=['reset'])
@commands.has_role('deception')
async def _reset(ctx):
    objShuffleCards.resetDeck()
    objShuffleCards.shuffle_clue()
    objShuffleCards.shuffle_mean()
    objShuffleCards.shuffle_hint()
    await ctx.send("Reset Card")

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command.')

@client.command(aliases = ['card'])
@commands.has_role('deception')
async def _card(ctx, *, NUM):
    NUM_PLAYER, NUM_CARD = NUM.split(' ')
    total_mean, total_clue = show_card(NUM_PLAYER, NUM_CARD)
    for i in range(1, int(NUM_PLAYER) + 1):
        embed = discord.Embed(title = f"Player {i}", colour = discord.Color.red())
        embed.add_field(name = "Hung khí", value= "   -   ".join(s for s in total_mean[i-1]), inline= False)
        embed.add_field(name = "Manh mối", value= "   -   ".join(s for s in total_clue[i-1]), inline= False)
        await ctx.send(embed = embed)

@client.command(aliases = ['clue'])
@commands.has_role('deception')
async def _clue(ctx, *, locate):
    cause_of_death = show_death()
    global location_choice
    location_choice = show_location(locate)
    hints = show_hint()
    embed = discord.Embed(title = f"Hint", colour = discord.Color.blue())
    embed.add_field(name = cause_of_death[0], value= "\n".join(cause_of_death[s] for s in range(1,len(cause_of_death))), inline= True)
    embed.add_field(name = location_choice[0], value= "\n".join(location_choice[s] for s in range(1,len(location_choice))), inline= True)
    for i in range(4):
        embed.add_field(name = hints[i][0], value="\n".join(hints[i][s] for s in range(1,len(hints[i]))), inline = True)
    await ctx.send(embed = embed)

@client.command()
@commands.has_role('deception')
async def startgame(ctx, num_player):
    global NUMBERS
    NUMBERS = list(range(1,int(num_player) + 1))
    shuffle(NUMBERS)
    if int(num_player) > 7:
        await ctx.send(f"Game bắt đầu với {num_player} người chơi trong đó có: 1 Hung thủ, 1 Đồng phạm, 1 Nhân chứng và {int(num_player)-3} Điều tra viên")
    else:
        await ctx.send(f"Game bắt đầu với {num_player} người chơi trong đó có: 1 Hung thủ, 1 Nhân chứng và {int(num_player)-2} Điều tra viên")

@client.command()
@commands.has_role('Deception Player')
async def getnumber(ctx):
    if len(NUMBERS) == 0:
        await ctx.send("Hì")
    else:
        await ctx.send(NUMBERS.pop())

@client.command()
@commands.has_role('deception')
async def murder(ctx):  
    global num_murder
    num_murder = random.choice(NUMBERS)
    await ctx.send(f"Hung thủ là Player {num_murder}")
    
@client.command()
@commands.has_role('deception')
async def witness(ctx):  
    global num_witness
    while True:
        num_witness = random.choice(NUMBERS)
        if num_witness != num_murder:
            break
    await ctx.send(f"Nhân chứng là Player {num_witness}")

@client.command()
@commands.has_role('deception')
async def accomplice(ctx):  
    global num_accomplice
    while True:
        num_accomplice = random.choice(NUMBERS)
        if num_accomplice != num_murder and num_accomplice != num_witness:
            break
    await ctx.send(f"Đồng phạm là Player {num_accomplice}")


@client.command()
@commands.has_role('deception')
async def answer(ctx, arg1, arg2):
    global answer1, answer2
    answer1, answer2 = arg1, arg2
    await ctx.send(f"Hung khí hung thủ chọn là thẻ số {answer1}\nManh mối liên quan đến hung thủ là thẻ số {answer2}")

@client.command(aliases=['pick'])
@commands.has_role('Deception Player')
async def _pick(ctx, player, mean, clue):
    if mean == str(answer1) and clue == str(answer2) and player == str(num_murder):
        await ctx.send(f"{ctx.author} đã chọn Player {num_murder} là hung thủ với hung khí số {answer1} và manh mối số {answer2}\nKết quả cuối cùng là chính xác, Congrats!.")
    else:
        await ctx.send(f"{ctx.author} đã chọn Player {num_murder} là hung thủ với hung khí số {answer1} và manh mối số {answer2}\nKết quả là sai. Player {ctx.author} đã mất danh dự của mình không thể vote lần nữa những vẫn có quyền thảo luận.")
client.run(TOKEN)
