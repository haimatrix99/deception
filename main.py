import random
import discord
from discord.ext import commands
from discord.utils import get
from settings import *

client = commands.Bot(command_prefix='$', help_command= None )

channels = {
    'card': 870245357425143838,
    'hint': 870245359593607199,
    'mod': 870718208590639164,
    'chung': 870307111698067536,
    'player': 870734874628210739,
}
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
    name_murder.clear()
    await ctx.send("Reset game")

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command.')


@client.command()
@commands.has_role('deception')
async def startgame(ctx, num_player):
    channel = client.get_channel(channels['chung'])
    global NUMBERS, players
    players = int(num_player)
    NUMBERS = list(range(1,int(num_player) + 1))
    shuffle(NUMBERS)
    if int(num_player) > 0 and int(num_player) < 5:
        await channel.send(f"Game bắt đầu với {num_player} người chơi trong đó có: 1 Hung thủ và {int(num_player)-1} Điều tra viên")
    elif int(num_player) >=5 and int(num_player) <= 7:
        await channel.send(f"Game bắt đầu với {num_player} người chơi trong đó có: 1 Hung thủ, 1 Nhân chứng và {int(num_player)-2} Điều tra viên")
    elif int(num_player) > 7 and int(num_player) <=12:
        await channel.send(f"Game bắt đầu với {num_player} người chơi trong đó có: 1 Hung thủ, 1 Đồng phạm, 1 Nhân chứng và {int(num_player)-3} Điều tra viên")
    else:
        await channel.send("Vui lòng chọn lại số players.")

@client.command()
@commands.has_role('deception')
async def card(ctx, num_card = "4"):
    channel = client.get_channel(channels['card'])
    total_mean, total_clue = show_card(players, int(num_card))
    for i in range(1, players + 1):
        embed = discord.Embed(title = f"Player {i}", colour = discord.Color.red())
        embed.add_field(name = "Hung khí", value= "   -   ".join(s for s in total_mean[i-1]), inline= False)
        embed.add_field(name = "Manh mối", value= "   -   ".join(s for s in total_clue[i-1]), inline= False)
        await channel.send(embed = embed)

@client.command()
@commands.has_role('deception')
async def clue(ctx, locate):
    channel = client.get_channel(channels['hint'])
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
    await channel.send(embed = embed)

@client.command()
@commands.has_role('deception')
async def murder(ctx):  
    global num_murder
    channel = client.get_channel(channels['mod'])
    if num_murder == 0:
        num_murder = random.choice(NUMBERS)
        await channel.send(f"Hung thủ là Player {num_murder}")
    else:
        await channel.send("Đã chọn được hung thủ")
    
@client.command()
@commands.has_role('deception')
async def witness(ctx):  
    global num_witness
    channel = client.get_channel(channels['mod'])
    if num_witness == 0 and 5 <= players <= 7 :
        while True:
            num_witness = random.choice(NUMBERS)
            if num_witness != num_murder:
                break
        await channel.send(f"Nhân chứng là Player {num_witness}")
    elif num_witness == 0 and players < 5: 
        await channel.send("Không thể thêm nhân chứng")
    elif num_witness != 0:
        await channel.send("Đã chọn được nhân chứng")

@client.command()
@commands.has_role('deception')
async def accomplice(ctx): 
    global num_accomplice
    channel = client.get_channel(channels['mod'])
    if num_accomplice == 0 and 7 < players <= 12:
        while True:
            num_accomplice = random.choice(NUMBERS)
            if num_accomplice != num_murder and num_accomplice != num_witness:
                break
        await channel.send(f"Đồng phạm là Player {num_accomplice}")
    elif num_accomplice == 0 and players < 7:
        await channel.send("Không thể thêm đồng phạm")
    elif num_accomplice != 0:
        await channel.send("Đã chọn được đồng phạm")

@client.command()
@commands.has_role('Deception player')
async def getnumber(ctx):
    channel = client.get_channel(channels['player'])
    if len(NUMBERS) == 0:
        await ctx.send("Đủ người chơi rồi không vào đƯợc nữa")
    elif len(NUMBERS) != 0 and num_murder != 0 or num_witness != 0 or num_accomplice!= 0:
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
            await channel.send(f'{ctx.author.name} sẽ là Player số {num_player}')
        else:
            await ctx.send("Bạn đã nhận số của mình rồi :3")

@client.command()
async def select(ctx, arg1, arg2):
    if ctx.author.id == name_murder[-1]:
        global answer1, answer2
        answer1, answer2 = arg1, arg2
        channel = client.get_channel(870718208590639164)
        await channel.send(f"Hung khí hung thủ chọn là thẻ số {answer1}\nManh mối liên quan đến hung thủ là thẻ số {answer2}")
    else: await ctx.send("Bạn không phải là hung thủ nên không thể chọn hung khí và manh mối.")

@client.command()
@commands.has_role('Deception player')
async def vote(ctx, player, mean, clue):
    global kick
    kick = False
    member = ctx.author
    role = get(ctx.guild.roles, name = "Deception player")
    if mean == answer1 and clue == answer2 and player == str(num_murder):
        await ctx.send(f"{ctx.author.name} đã chọn Player {player} là hung thủ với hung khí số {mean} và manh mối số {clue}\nKết quả cuối cùng là chính xác, Congrats!.")
        kick = False
    else:
        await ctx.send(f"{ctx.author.name} đã chọn Player {player} là hung thủ với hung khí số {mean} và manh mối số {clue}\nKết quả là sai. Player {ctx.author.name} đã mất danh dự của mình không thể vote lần nữa những vẫn có quyền thảo luận.")
        await member.remove_roles(role, atomic=False)
        list_player_id.remove(ctx.author.id)
        kick = True

@client.command()
@commands.has_role('deception')
async def ms(ctx,arg1,arg2,arg3,arg4,arg5,arg6):
    embed = discord.Embed(title = "Hint from Moderator", colour = discord.Color.red())
    embed.add_field(name = cause_of_death[0], value = cause_of_death[int(arg1)])
    embed.add_field(name = location_choice[0], value = location_choice[int(arg2)],inline= False)
    embed.add_field(name = hints[0][0], value = hints[0][int(arg3)],inline= False)
    embed.add_field(name = hints[1][0], value = hints[1][int(arg4)],inline= False)
    embed.add_field(name = hints[2][0], value = hints[2][int(arg5)],inline= False)
    embed.add_field(name = hints[3][0], value = hints[3][int(arg6)],inline= False)   
    await ctx.send(embed = embed)

@client.command()
async def help(ctx):
    embed = discord.Embed(title = f"Help commands for player", colour = discord.Color.green())
    embed.add_field(name = "getnumber", value = "Lệnh này cho player dùng để nhận số, khi nhận xong thì player sẽ nhận được message role của mình, Nếu là hung thủ thì sẽ xem bài và dùng lệnh để chọn hung khí và manh mối.")
    embed.add_field(name = "vote", value= "Lệnh này để có thể vote ai là Hung thủ, nếu vote đúng thì sẽ Endgame chờ hung thủ lật kèo. còn sai thì sẽ k được vote lần nữa. VD: $vote 2 2 2 @Deception Player, Lưu ý phải tag role @Deception Player, cái này được tính như danh dự. Phải tag mới được tính. còn 2 2 2 kia sẽ là Player 2 là hung thủ với hung khí số 2 và manh mối số 2", inline= False)
    embed.add_field(name = "select", value = "Lệnh dành cho ai làm hung thủ để chọn hung khí và manh mối. VD: $select 2 2 là chọn hung khí số 2 và manh mối số 2.")
    await ctx.send(embed = embed)

@client.command()
@commands.has_role('deception')
async def hm(ctx):
    embed = discord.Embed(title = f"Help commands for moderator", colour = discord.Color.green())
    embed.add_field(name = "startgame", value = "Dùng để bắt đầu game với số player. VD: $startgame 5, bắt đầu game với 5 player.")
    embed.add_field(name = "card", value="Dùng để phát bài cho player. VD: $card 2, có nghĩa là chia bài trong đó mỗi player có 2 lá hung khí và 2 lá manh mối, 3 đối với game dễ, 4 là bình thường, 5 là game khó.")
    embed.add_field(name = "clue", value = "Dùng để hiển thị hint cho player. Lưu ý nó chỉ hiển thị có những lá hint gì, Quản trò vẫn phải đưa ra hint củ thể cho player biết bằng lệnh khác. Có 4 lá hiện trường và quản trò có quyền lựa chọn. VD: $clue 1 ,Có nghĩa là chọn lá hiện trường 1", inline= False)
    embed.add_field(name = "murder",value = "Lệnh của quản trò để random murder trong tất cả players", inline=False)
    embed.add_field(name = "witness",value = "Lệnh của quản trò để random witness trong tất cả players. Lưu ý phải roll Murder trước",inline=False)
    embed.add_field(name = "accomplice",value = "Lệnh của quản trò để random accomplce trong tất cả players, nếu player < 7 thì k dùng lệnh này",inline=False)
    embed.add_field(name = "ms", value = "Lệnh dùng để chọn vị trí các viên đạn trong các hint đưa ở trên. VD: $ms 2 2 2 2 2 2, có nghĩa là đặt 6 viên đạn ở hàng 2 của 6 thẻ.")
    embed.add_field(name = "reset", value = "Lệnh dùng khi chơi xong 1 game.")
    await ctx.send(embed = embed)

@client.command()
async def play(message):
    member = message.author
    role = get(message.guild.roles, name = "Deception player")
    if member.id not in list_player_id and kick == False:
        list_player_id.append(member.id)
        await member.add_roles(role, atomic=False)
        await message.send(f"{member.name} đã tham gia vào game!")
    elif role in member.roles and member.id in list_player_id:
        await message.send("Bạn đã ở trong game rồi!")
    elif kick:
        await message.send("Game chưa kết thúc.")
        
client.run(TOKEN)


