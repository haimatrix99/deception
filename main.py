import random
import discord
from discord.ext import commands
from discord.utils import get
from settings import *

client = commands.Bot(command_prefix='$', help_command=None)

channels = {
    'info': 870245357425143838,
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
    global num_murder, num_accomplice, num_witness
    objShuffleCards.resetDeck()
    objShuffleCards.shuffle_clue()
    objShuffleCards.shuffle_mean()
    objShuffleCards.shuffle_hint()
    list_id.clear()
    name_murder.clear()
    NUMBERS.clear()
    players = 0
    num_murder = 0
    num_accomplice = 0
    num_witness = 0
    kick = False
    isselect == False
    ispick = False
    isfound = False
    await ctx.send("Reset game mới")


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command.')


@client.command()
async def play(message):
    member = message.author
    role = get(message.guild.roles, name="Deception player")
    if member.id not in list_player_id and kick == False:
        list_player_id.append(member.id)
        await member.add_roles(role, atomic=False)
        await message.send(f"{member.name} đã tham gia vào game!")
    elif role in member.roles and member.id in list_player_id:
        await message.send("Bạn đã ở trong game rồi!")
    elif kick:
        await message.send("Game chưa kết thúc.")
    print(list_player_id)


@client.command()
@commands.has_role('deception')
async def startgame(ctx, num_player):
    channel = client.get_channel(channels['chung'])
    global NUMBERS, players
    players = int(num_player)
    NUMBERS = list(range(1, int(num_player) + 1))
    shuffle(NUMBERS)
    if int(num_player) > 0 and int(num_player) < 5:
        await channel.send(f"Game bắt đầu với {num_player} người chơi trong đó có: 1 Hung thủ và {int(num_player)-1} Điều tra viên")
    elif int(num_player) >= 5 and int(num_player) <= 7:
        await channel.send(f"Game bắt đầu với {num_player} người chơi trong đó có: 1 Hung thủ, 1 Nhân chứng và {int(num_player)-2} Điều tra viên")
    elif int(num_player) > 7 and int(num_player) <= 12:
        await channel.send(f"Game bắt đầu với {num_player} người chơi trong đó có: 1 Hung thủ, 1 Đồng phạm, 1 Nhân chứng và {int(num_player)-3} Điều tra viên")
    else:
        await channel.send("Vui lòng chọn lại số players.")


@client.command()
@commands.has_role('deception')
async def card(ctx, num_card="4"):
    channel = client.get_channel(channels['info'])
    total_mean, total_clue = show_card(players, int(num_card))
    for i in range(1, players + 1):
        embed = discord.Embed(title=f"Player {i}", colour=discord.Color.red())
        embed.add_field(name="Hung khí", value="   -   ".join(s for s in total_mean[i - 1]), inline=False)
        embed.add_field(name="Manh mối", value="   -   ".join(s for s in total_clue[i - 1]), inline=False)
        await channel.send(embed=embed)


@client.command()
@commands.has_role('deception')
async def clue(ctx, locate):
    channel = client.get_channel(channels['info'])
    global cause_of_death
    cause_of_death = show_death()
    global location_choice
    location_choice = show_location(locate)
    global hints
    hints = show_hint()
    embed = discord.Embed(title=f"Hint", colour=discord.Color.blue())
    embed.add_field(name=cause_of_death[0], value="\n".join(cause_of_death[s] for s in range(1, len(cause_of_death))), inline=True)
    embed.add_field(name=location_choice[0], value="\n".join(location_choice[s] for s in range(1, len(location_choice))), inline=True)
    for i in range(4):
        embed.add_field(name=hints[i][0], value="\n".join(hints[i][s] for s in range(1, len(hints[i]))), inline=True)
    await channel.send(embed=embed)


@client.command()
@commands.has_role('deception')
async def murder(ctx):
    global num_murder
    if players == 0:
        await ctx.send("Game chưa setup xong")
    channel = client.get_channel(channels['mod'])
    if num_murder == 0:
        num_murder = random.choice(NUMBERS)
        await channel.send(f"Hung thủ là Player {num_murder}")
    elif num_murder != 0 and players != 0:
        await channel.send("Đã chọn được hung thủ")


@client.command()
@commands.has_role('deception')
async def witness(ctx):
    global num_witness
    if players == 0:
        await ctx.send("Game chưa setup xong")
    channel = client.get_channel(channels['mod'])
    if num_witness == 0 and 5 <= players <= 7:
        while True:
            num_witness = random.choice(NUMBERS)
            if num_witness != num_murder:
                break
        await channel.send(f"Nhân chứng là Player {num_witness}")
    elif num_witness == 0 and players < 5 and players != 0:
        await channel.send("Không thể thêm nhân chứng")
    elif num_witness != 0 and players != 0:
        await channel.send("Đã chọn được nhân chứng")


@client.command()
@commands.has_role('deception')
async def accomplice(ctx):
    global num_accomplice
    if players == 0:
        await ctx.send("Game chưa setup xong")
    channel = client.get_channel(channels['mod'])
    if num_accomplice == 0 and 7 < players <= 12:
        while True:
            num_accomplice = random.choice(NUMBERS)
            if num_accomplice != num_murder and num_accomplice != num_witness:
                break
        await channel.send(f"Đồng phạm là Player {num_accomplice}")
    elif num_accomplice == 0 and players < 7 and players != 0:
        await channel.send("Không thể thêm đồng phạm")
    elif num_accomplice != 0 and players != 0:
        await channel.send("Đã chọn được đồng phạm")


@client.command()
@commands.has_role('Deception player')
async def getnumber(ctx):
    channel = client.get_channel(channels['player'])
    if len(NUMBERS) == 0:
        await ctx.send("Đủ người chơi rồi không vào được nữa hoặc có thể là game chưa bắt đầu")
    elif len(NUMBERS) != 0 and num_murder != 0 or num_witness != 0 or num_accomplice != 0:
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
    elif len(NUMBERS) != 0 and num_witness == 0 and num_murder == 0 and num_accomplice == 0:
        await ctx.send("Quản trò chưa setup xong các thẻ bài!")


@client.command()
async def select(ctx, arg1, arg2):
    global isselect
    isselect == False
    if ctx.author.id == name_murder[-1] and isselect == False:
        global answer1, answer2
        answer1, answer2 = arg1, arg2
        channel = client.get_channel(870718208590639164)
        isselect = True
        await channel.send(f"Hung khí hung thủ chọn là thẻ số {answer1}\nManh mối liên quan đến hung thủ là thẻ số {answer2}")
    elif ctx.author.id == name_murder[-1] and isselect:
        await ctx.send("Bạn đã chọn xong hung khí và manh mối rồi!")
    else:
        await ctx.send("Bạn không phải là hung thủ nên không thể chọn hung khí và manh mối.")


@client.command()
@commands.has_role('Deception player')
async def vote(ctx, player, mean, clue):
    global kick, isfound
    kick = False
    member = ctx.author
    role = get(ctx.guild.roles, name="Deception player")
    if mean == answer1 and clue == answer2 and player == str(num_murder):
        await ctx.send(f"{ctx.author.name} đã chọn Player {player} là hung thủ với hung khí số {mean} và manh mối số {clue}\nKết quả cuối cùng là chính xác, Congrats!.")
        kick = False
        isfound = True

    else:
        await ctx.send(f"{ctx.author.name} đã chọn Player {player} là hung thủ với hung khí số {mean} và manh mối số {clue}\nKết quả là sai. Player {ctx.author.name} đã mất danh dự của mình không thể vote lần nữa những vẫn có quyền thảo luận.")
        await member.remove_roles(role, atomic=False)
        list_player_id.remove(ctx.author.id)
        kick = True


@client.command()
@commands.has_role('deception')
async def sm(ctx, arg1, arg2, arg3, arg4, arg5, arg6):
    channel = client.get_channel(channels['info'])
    embed = discord.Embed(title="Hint from Moderator", colour=discord.Color.red())
    embed.add_field(name=cause_of_death[0], value=cause_of_death[int(arg1)])
    embed.add_field(name=location_choice[0], value=location_choice[int(arg2)], inline=False)
    embed.add_field(name=hints[0][0], value=hints[0][int(arg3)], inline=False)
    embed.add_field(name=hints[1][0], value=hints[1][int(arg4)], inline=False)
    embed.add_field(name=hints[2][0], value=hints[2][int(arg5)], inline=False)
    embed.add_field(name=hints[3][0], value=hints[3][int(arg6)], inline=False)
    await channel.send(embed=embed)


@client.command()
async def help(ctx):
    embed = discord.Embed(title=f"Help commands for player", colour=discord.Color.green())
    embed.add_field(name="play", value="Lệnh này dùng để add role Depcetion player cũng như là danh dự để vote.")
    embed.add_field(name="quit", value="Lệnh này dùng để remove role Depcetion player.")
    embed.add_field(name="getnumber", value="Lệnh này cho player dùng để nhận số, khi nhận xong thì player sẽ nhận được message role của mình, Nếu là hung thủ thì sẽ xem bài và dùng lệnh để chọn hung khí và manh mối.")
    embed.add_field(name="vote", value="Lệnh này để có thể vote ai là Hung thủ, nếu vote đúng thì sẽ Endgame chờ hung thủ lật kèo. còn sai thì sẽ k được vote lần nữa. VD: $vote 2 2 2,còn 2 2 2 kia sẽ là Player 2 là hung thủ với hung khí số 2 và manh mối số 2")
    embed.add_field(name="select", value="Lệnh dành cho ai làm hung thủ để chọn hung khí và manh mối. VD: $select 2 2 là chọn hung khí số 2 và manh mối số 2. Hung thủ sẽ command ở phần trong DM với Bot luôn")
    embed.add_field(name="findwitness", value="Nếu hung thủ bị bắt thì hung thủ có quyền dùng lệnh này để tìm ra nhân chứng và lật kèo. Nếu chọn đung thì hung thủ thắng, nếu sai thì thua. VD: $findwitness 4, tức là Hung thủ chọn 4 làm nhân chứng nếu đúng thì 4 là nhân chứng thì hung thủ thắng còn không thì hung thủ thua.")
    await ctx.send(embed=embed)


@client.command()
@commands.has_role('deception')
async def hm(ctx):
    embed = discord.Embed(title=f"Help commands for moderator", colour=discord.Color.green())
    embed.add_field(name="startgame", value="Dùng để bắt đầu game với số player. VD: $startgame 5, bắt đầu game với 5 player.")
    embed.add_field(name="card", value="Dùng để phát bài cho player. VD: $card 2, có nghĩa là chia bài trong đó mỗi player có 2 lá hung khí và 2 lá manh mối. Mặc đinh là 4 nếu muốn game dễ thì 3 , 5 là game khó.")
    embed.add_field(name="clue", value="Dùng để hiển thị hint cho player. Lưu ý nó chỉ hiển thị có những lá hint gì, Quản trò vẫn phải đưa ra hint củ thể cho player biết bằng lệnh khác. Có 4 lá hiện trường và quản trò có quyền lựa chọn. VD: $clue 1 ,Có nghĩa là chọn lá hiện trường 1")
    embed.add_field(name="murder", value="Lệnh của quản trò để random murder trong tất cả players")
    embed.add_field(name="witness", value="Lệnh của quản trò để random witness trong tất cả players.")
    embed.add_field(name="accomplice", value="Lệnh của quản trò để random accomplice trong tất cả players.")
    embed.add_field(name="locate", value="Lệnh dùng để check các địa điểm gây án")
    embed.add_field(name="sm", value="Lệnh dùng để chọn vị trí các viên đạn trong các hint đưa ở trên. VD: $sm 2 2 2 2 2 2, có nghĩa là đặt 6 viên đạn ở hàng 2 của 6 thẻ.")
    embed.add_field(name="reset", value="Lệnh dùng khi chơi xong 1 game.")
    await ctx.send(embed=embed)


@client.command()
@commands.has_role("deception")
async def locate(ctx):
    channel = client.get_channel(channels['info'])
    embed = discord.Embed(title=f"Locations", colour=discord.Color.red())
    locates = locations()
    for i in range(4):
        embed.add_field(name=f"Location of Crime-{i+1}", value="\n".join(_ for _ in locates[i]))
    await channel.send(embed=embed)


@client.command()
async def quit(ctx):
    member = ctx.author
    role = get(ctx.guild.roles, name="Deception player")
    if role in member.roles and member.id in list_player_id:
        list_player_id.remove(member.id)
        await member.remove_roles(role, atomic=False)
        await ctx.send(f"{member.name} đã thoát game.")
    elif role in member.roles and member.id not in list_player_id:
        await member.remove_roles(role, atomic=False)
        await ctx.send(f"{member.name} đã thoát game.")
    else:
        await ctx.send("Bạn chưa tham gia vào game.")
    print(list_player_id)


@client.command()
async def findwitness(ctx, witness):
    global isfound, ispick, num_witness
    num_witness = 0
    ispick = False
    isfound = False
    if isfound and num_witness != 0 and ctx.author.id == name_murder[-1] and ispick == False:
        ispick = True
        if int(witness) == num_witness:
            await ctx.send(f"Player {num_murder} là hung thủ sau khi bị bắt đã chọn đúng Player {witness} là nhân chứng của vụ án. Hung thủ đã lật kèo được vụ án. Hung thủ chiến thắng.")
        else:
            await ctx.send(f"Player {num_murder} là hung thủ sau khi bị bắt đã chọn Player {witness} là nhân chứng của vụ án, nhưng Player {witness} không phải là nhân chứng. Phe điều tra viên đã chiến thắng.")
    elif ispick == True:
        await ctx.send("Hung thủ đã chọn rồi, không được chọn lại")
    elif ctx.author.id != name_murder[-1]:
        await ctx.send("Bạn không phải là hung thủ để chọn ra nhân chứng")
    elif num_witness == 0 and ctx.author == name_murder[-1]:
        await ctx.send("Vụ án này không có nhân chứng")
    elif isfound == False:
        await ctx.send("Hung thủ chưa bị bắt")


client.run(TOKEN)
