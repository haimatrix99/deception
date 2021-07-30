import random
import discord
from discord import embeds
from discord.ext import commands
from settings import *

client = commands.Bot(command_prefix='$', help_command= None)

@client.event
async def on_ready():
    print(f'{client.user.name} has connected to Discord!')

@client.command()
async def ping(ctx):
    await ctx.send("pong")

@client.command()
@commands.has_role('deception')
async def clear(ctx, amount=10):
    await ctx.channel.purge(limit=amount)

@client.command()
@commands.has_role('deception')
async def reset(ctx):
    objShuffleCards.resetDeck()
    objShuffleCards.shuffle_clue()
    objShuffleCards.shuffle_mean()
    objShuffleCards.shuffle_hint()
    list_id.clear()
    await ctx.send("Reset Card")

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command.')

@client.command()
@commands.has_role('deception')
async def card(ctx, *, NUM):
    NUM_PLAYER, NUM_CARD = NUM.split(' ')
    total_mean, total_clue = show_card(NUM_PLAYER, NUM_CARD)
    for i in range(1, int(NUM_PLAYER) + 1):
        embed = discord.Embed(title = f"Player {i}", colour = discord.Color.red())
        embed.add_field(name = "Hung khí", value= "   -   ".join(s for s in total_mean[i-1]), inline= False)
        embed.add_field(name = "Manh mối", value= "   -   ".join(s for s in total_clue[i-1]), inline= False)
        await ctx.send(embed = embed)

@client.command()
@commands.has_role('deception')
async def clue(ctx, *, locate):
    global cause_of_death
    cause_of_death = show_death()
    global location_choice
    location_choice = show_location(locate)
    global hints
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
        if ctx.author.id not in list_id:
            num_player = NUMBERS.pop()
            if num_player == num_murder:
                await ctx.message.author.send('Bạn là Hung thủ, vui lòng xem bài rồi dùng lệnh $select để chọn hung khí và manh mối. VD:    $select 2 2 là chọn hung khí số 2 và manh mối số 2 nhìn từ trái qua phải.')
                name_murder.append(ctx.author.id)
                list_id.append(ctx.author.id)
            elif num_player == num_witness and num_accomplice != 0:
                await ctx.message.author.send(f'Bạn là Nhân chứng, 2 kẻ tình nghi của Vụ án này là Player {num_murder} và Player    {num_accomplice}')
                list_id.append(ctx.author.id)
            elif num_player == num_witness and num_accomplice == 0:
                await ctx.message.author.send(f'Bạn là Nhân chứng, Hung thủ của Vụ án này là Player {num_murder}')
                list_id.append(ctx.author.id)
            elif num_player == num_accomplice:
                await ctx.message.author.send(f'Bạn là Đồng phạm của Hung thủ, Hung thủ mà bạn biết là Player {num_murder}')
                list_id.append(ctx.author.id)
            else: 
                await ctx.message.author.send("Bạn là điều tra viên, Nhiệm vụ của bạn là tìm ra đúng chính xác Hung khí và Manh mối mà  Hung thủ đã dùng.")
                list_id.append(ctx.author.id)
            await ctx.send(f'{ctx.author.name} sẽ là Player số {num_player}')
        else:
            await ctx.send("Bạn đã nhận số của mình rồi :3")

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
async def select(ctx, arg1, arg2):
    if ctx.author.id == name_murder[-1]:
        global answer1, answer2
        answer1, answer2 = arg1, arg2
        channel = client.get_channel(870307166886711309)
        await channel.send(f"Hung khí hung thủ chọn là thẻ số {answer1}\nManh mối liên quan đến hung thủ là thẻ số {answer2}")
    else: await ctx.send("Bạn không phải là hung thủ nên không thể chọn hung khí và manh mối.")

@client.command()
@commands.has_role('Deception Player')
async def pick(ctx, player, mean, clue, role: discord.Role):
    if mean == str(answer1) and clue == str(answer2) and player == str(num_murder):
        await ctx.send(f"{ctx.author.name} đã chọn Player {player} là hung thủ với hung khí số {answer1} và manh mối số {answer2}\nKết quả cuối cùng là chính xác, Congrats!.")
    else:
        await ctx.send(f"{ctx.author.name} đã chọn Player {player} là hung thủ với hung khí số {answer1} và manh mối số {answer2}\nKết quả là sai. Player {ctx.author.name} đã mất danh dự của mình không thể vote lần nữa những vẫn có quyền thảo luận.")
        await ctx.author.remove_roles(role)

@client.command()
async def help(ctx):
    embed = discord.Embed(title = f"Help commands for player", colour = discord.Color.green())
    embed.add_field(name = "getnumber", value = "Lệnh này cho player dùng để nhận số, khi nhận xong thì player sẽ nhận được message role của mình, Nếu là hung thủ thì sẽ xem bài và dùng lệnh để chọn hung khí và manh mối.")
    embed.add_field(name = "pick", value= "Lệnh này để có thể vote ai là Hung thủ, nếu vote đúng thì sẽ Endgame chờ hung thủ lật kèo. còn sai thì sẽ k được vote lần nữa. VD: $pick 2 2 2 @Deception Player, Lưu ý phải tag role @Deception Player, cái này được tính như danh dự. Phải tag mới được tính. còn 2 2 2 kia sẽ là Player 2 là hung thủ với hung khí số 2 và manh mối số 2", inline= False)
    embed.add_field(name = "select", value = "Lệnh dành cho ai làm hung thủ để chọn hung khí và manh mối. VD: $select 2 2 là chọn hung khí số 2 và manh mối số 2.")
    await ctx.send(embed = embed)

@client.command()
@commands.has_role('deception')
async def helpmoderator(ctx):
    embed = discord.Embed(title = f"Help commands for moderator", colour = discord.Color.green())
    embed.add_field(name = "card", value="Dùng để phát bài cho player. VD: $card 2 2, có nghĩa là chia bài cho 2 player trong đó mỗi player có 2 lá hung khí và 2 lá manh mối")
    embed.add_field(name = "clue", value = "Dùng để hiển thị hint cho player. Lưu ý nó chỉ hiển thị có những lá hint gì, Quản trò vẫn phải đưa ra hint củ thể cho player biết bằng lệnh khác. Có 4 lá hiện trường và quản trò có quyền lựa chọn. VD: $clue 1 ,Có nghĩa là chọn lá hiện trường 1", inline= False)
    embed.add_field(name = "murder",value = "Lệnh của quản trò để random murder trong tất cả players", inline=False)
    embed.add_field(name = "witness",value = "Lệnh của quản trò để random witness trong tất cả players. Lưu ý phải roll Murder trước",inline=False)
    embed.add_field(name = "accomplice",value = "Lệnh của quản trò để random accomplce trong tất cả players, nếu player < 7 thì k dùng lệnh này",inline=False)
    await ctx.send(embed = embed)

@client.command()
@commands.has_role('deception')
async def moderatorselect(ctx,arg1,arg2,arg3,arg4,arg5,arg6):
    embed = discord.Embed(title = "Hint from Moderator", colour = discord.Color.red())
    embed.add_field(name = cause_of_death[0], value = cause_of_death[int(arg1)])
    embed.add_field(name = location_choice[0], value = location_choice[int(arg2)],inline= False)
    embed.add_field(name = hints[0][0], value = hints[0][int(arg3)],inline= False)
    embed.add_field(name = hints[1][0], value = hints[1][int(arg4)],inline= False)
    embed.add_field(name = hints[2][0], value = hints[2][int(arg5)],inline= False)
    embed.add_field(name = hints[3][0], value = hints[3][int(arg6)],inline= False)   
    await ctx.send(embed = embed)

client.run(TOKEN)
