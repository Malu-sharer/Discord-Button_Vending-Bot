# -*- coding: utf-8 -*-
from functools import partial
from discord_components import DiscordComponents, ComponentsBot, Select, SelectOption, Button, ButtonStyle, ActionRow
import discord, sqlite3, datetime, randomstring, os, setting, random
from discord_components.ext.filters import user_filter
import asyncio, requests, json
from setting import admin_id, domain, bot_name, license_master_id
from datetime import timedelta
from discord_webhook import DiscordEmbed, DiscordWebhook
from discord_buttons_plugin import ButtonType

client = discord.Client()
charginguser = []
buyinguser = []

def now():
    return str(datetime.datetime.now()).split(".")[0]

def get_roleid(serverid):
    con = sqlite3.connect("../DB/" + str(serverid) + ".db")
    cur = con.cursor()
    cur.execute("SELECT roleid FROM serverinfo;")
    data = cur.fetchone()[0]
    con.close()
    if (str(data).isdigit()):
        return int(data)
    else:
        return data

def get_logwebhk(serverid):
    con = sqlite3.connect("../DB/" + str(serverid) + ".db")
    cur = con.cursor()
    cur.execute("SELECT logwebhk FROM serverinfo;")
    data = cur.fetchone()[0]
    con.close()
    return data

def get_buylogwebhk(serverid):
    con = sqlite3.connect("../DB/" + str(serverid) + ".db")
    cur = con.cursor()
    cur.execute("SELECT buylogwebhk FROM serverinfo;")
    data = cur.fetchone()[0]
    con.close()
    return data

def add_time(now_days, add_days):
    ExpireTime = datetime.datetime.strptime(now_days, '%Y-%m-%d %H:%M')
    ExpireTime_STR = (ExpireTime + timedelta(days=add_days)).strftime('%Y-%m-%d %H:%M')
    return ExpireTime_STR

def is_expired(time):
    ServerTime = datetime.datetime.now()
    ExpireTime = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M')
    if ((ExpireTime - ServerTime).total_seconds() > 0):
        return False
    else:
        return True

def get_logwebhk(serverid):
    con = sqlite3.connect("../DB/" + str(serverid) + ".db")
    cur = con.cursor()
    cur.execute("SELECT logwebhk FROM serverinfo;")
    data = cur.fetchone()[0]
    con.close()
    return data

def make_expiretime(days):
    ServerTime = datetime.datetime.now()
    ExpireTime = ServerTime + timedelta(days=days)
    ExpireTime_STR = (ServerTime + timedelta(days=days)).strftime('%Y-%m-%d %H:%M')
    return ExpireTime_STR

def nowstr():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

@client.event
async def on_ready():
    print(f"[!] 로그인 시간 : {now()}\n[!] 봇 이름 : {client.user.name}\n[!] 봇 아이디 : {client.user.id}\n[!] 참가 중인 서버 : {len(client.guilds)}개")
    DiscordComponents(client)
    while True:
        guilds = len(client.guilds)
        activity = discord.Game(name=f"{guilds}개의 서버에서 사용중")
        await client.change_presence(status=discord.Status.online, activity = activity)
        await asyncio.sleep(10)

@client.event
async def on_message(message):
        if message.content.startswith('!생성 '):
            if message.author.id in license_master_id:
                if not isinstance(message.channel, discord.channel.DMChannel):
                    try:
                        amount = int(message.content.split(" ")[1])
                    except:
                        await message.channel.send("올바른 생성 갯수를 입력해주세요.")
                        return
                    if 1 <= amount <= 30:
                        try:
                            license_length = int(message.content.split(" ")[2])
                        except:
                            await message.channel.send("올바른 생성 기간을 입력해주세요.")
                            return
                        codes = []
                        for _ in range(amount):
                            code = "mjmall-" + randomstring.pick(20)
                            codes.append(code)
                            con = sqlite3.connect("../DB/" + "license.db")
                            cur = con.cursor()
                            cur.execute("INSERT INTO license Values(?, ?, ?, ?, ?);", (code, license_length, 0, "None", 0))
                            con.commit()
                            con.close()
                        await message.channel.send("\n".join(codes))

        if message.content.startswith('!등록 '):
            if message.author.guild_permissions.administrator or message.author.id == int(admin_id):
                license_key = message.content.split(" ")[1]
                con = sqlite3.connect("../DB/" + "license.db")
                cur = con.cursor()
                cur.execute("SELECT * FROM license WHERE code == ?;", (license_key,))
                search_result = cur.fetchone()
                con.close()
                if (search_result != None):
                    if (search_result[2] == 0):
                        if not (os.path.isfile("../DB/" + str(message.guild.id) + ".db")):
                            con = sqlite3.connect("../DB/" + str(message.guild.id) + ".db")
                            cur = con.cursor()
                            cur.execute("CREATE TABLE serverinfo (id TEXT, expiredate TEXT, cultureid TEXT, culturepw TEXT, pw TEXT, roleid TEXT, logwebhk TEXT, buylogwebhk TEXT, culture_fee TEXT, bank TEXT, normaloff INTEGER, vipoff INTEGER, vvipoff INTEGER, reselloff INTEGER, color TEXT, chargeban INTEGER, vipautosetting INTEGER, vvipautosetting INTEGER, buyusernamehide TEXT, viproleid INTEGER, vviproleid INTEGER, pushbulletapppassword TEXT, webhookprofile TEXT, webhookname TEXT, announcement TEXT);")
                            con.commit()
                            first_pw = randomstring.pick(10)
                            cur.execute("INSERT INTO serverinfo VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", (message.guild.id, make_expiretime(int(sqlite3.connect("../DB/" + "license.db").cursor().execute("SELECT * FROM license WHERE code == ?;", (license_key,)).fetchone()[1])), "", "", first_pw, 0, "", "", 0, "", 0, 0, 0, 0, "파랑", 3, 5, 10, "익명님, `{product_name}` 제품 `{amount}`개 구매 감사합니다!", 0, 0, "", "https://cdn.discordapp.com/attachments/921272040374300682/926834856497905744/Capture_2021-12-27_13.31.23.jpg", "구매로그", "공지사항"))
                            con.commit()
                            cur.execute("CREATE TABLE users (id INTEGER, money INTEGER, bought INTEGER, warnings INTEGER, rank TEXT, buycount INTEGER);")
                            con.commit()
                            cur.execute("CREATE TABLE products (name INTEGER, money INTEGER, stock TEXT, roleid INTEGER);")
                            con.commit()
                            cur.execute("CREATE TABLE buy_logs (amount INTEGER, id TEXT, datetime INTEGER);")
                            con.commit()
                            con.close()
                            con = sqlite3.connect("../DB/" + "license.db")
                            cur = con.cursor()
                            cur.execute("UPDATE license SET isused = ?, useddate = ?, usedby = ? WHERE code == ?;", (1, nowstr(), message.guild.id, license_key))
                            con.commit()
                            con.close()
                            con = sqlite3.connect("../DB/" + "license.db")
                            cur = con.cursor()
                            cur.execute("SELECT * FROM license WHERE code == ?;", (license_key,))
                            await message.author.send(embed=discord.Embed(title="서버 등록 성공", description="서버가 성공적으로 등록되었습니다.\n라이센스 기간: `30`일\n만료일: `" + make_expiretime(int(sqlite3.connect("../DB/" + "license.db").cursor().execute("SELECT * FROM license WHERE code == ?;", (license_key,)).fetchone()[1])) + f"`\n웹 패널: {domain}\n아이디: `" +str(message.guild.id) + "`\n비밀번호: `" + first_pw + "`", color=0x4461ff),
                            components = [
                                ActionRow(
                                    Button(style=ButtonType().Link,label = "웹패널",url=domain),
                                )
                            ]
                        )
                            await message.channel.send(embed=discord.Embed(title="서버 등록 성공", description="서버가 성공적으로 등록되었습니다.", color=0x4461ff))
                            con.close()
                            
                        else:
                            await message.channel.send(embed=discord.Embed(title="서버 등록 실패", description="이미 등록된 서버이므로 등록할 수 없습니다.\n기간 추가를 원하신다면 !라이센스 명령어를 이용해주세요.", color=0x4461ff))
                    else:
                        await message.channel.send(embed=discord.Embed(title="서버 등록 실패", description="이미 사용된 라이센스입니다.\n관리자에게 문의해주세요.", color=0x4461ff))
                else:
                    await message.channel.send(embed=discord.Embed(title="서버 등록 실패", description="존재하지 않는 라이센스입니다.", color=0x4461ff))
        
        if message.content.startswith("!서버 이전 "):
            if message.author.guild_permissions.administrator or message.author.id == int(admin_id):
                if not (os.path.isfile("../DB/" + str(message.guild.id) + ".db")):
                    try:
                        server_id = message.content.split(" ")[2].split(" ")[0]
                        webpanel_pw = message.content.split(" ")[3]
                    except:
                        await message.channel.send(embed=discord.Embed(title="서버 이전 실패", description="서버 아이디와 웹패널 비밀번호를 확인해주세요.", color=0x4461ff))
                    if (os.path.isfile("../DB/" + server_id + ".db")):
                        con = sqlite3.connect("../DB/" + server_id + ".db")
                        cur = con.cursor()
                        cur.execute("SELECT * FROM serverinfo;", ())
                        server_info = cur.fetchone()
                        con.close()
                        if server_info[4] == webpanel_pw:
                            con = sqlite3.connect("../DB/" + server_id + ".db")
                            cur = con.cursor()
                            cur.execute("UPDATE serverinfo SET id = ?;", (str(message.guild.id),))
                            con.commit()
                            con.close()
                            os.rename("../DB/" + server_id + ".db", "../DB/" + str(message.guild.id) + ".db")
                            await message.author.send(embed=discord.Embed(title="서버 이전 성공", description="만료일: `" + server_info[1] + f"`\n웹 패널: {domain}\n아이디: `" +str(message.guild.id) + "`\n비밀번호: `" + server_info[4] + "`", color=0x4461ff))
                            await message.channel.send(embed=discord.Embed(title="서버 이전 성공", description="서버가 성공적으로 이전되었습니다", color=0x4461ff))
                            
                        else:
                            await message.channel.send(embed=discord.Embed(title="서버 이전 실패", description="웹패널 비밀번호를 확인해주세요.", color=0x4461ff))
                    else:
                        await message.channel.send(embed=discord.Embed(title="서버 이전 실패", description="올바른 서버 아이디를 입력해주세요.", color=0x4461ff))
                else:
                    await message.channel.send(embed=discord.Embed(title="서버 이전 실패", description="이미 서버가 등록되어있습니다.", color=0x4461ff))

        if message.content == '!버튼':
            if message.author.guild_permissions.administrator or message.author.id == int(admin_id):
                if (os.path.isfile("../DB/" + str(message.guild.id) + ".db")):
                    try:
                        await message.delete()
                    except:
                        pass
                    con = sqlite3.connect("../DB/" + str(message.guild.id) + ".db")
                    cur = con.cursor()
                    cur.execute("SELECT * FROM serverinfo;", ())
                    server_info = cur.fetchone()
                    con.close()
                    color = server_info[14]
                    if color == "파랑":
                        embed = discord.Embed(title='버튼 자판기 안내', description='원하시는 버튼 메뉴를 선택 해주십시요.\n```이용 전 안내사항(필독 요망)\n1. 계좌이체시 입금내역을 고객센터에 보내주세요!\n2. 문화상품권 충전은 자동 충전 입니다```', color=0x4461ff)
                        embed.set_thumbnail(url="사진링크넣기")
                        await message.channel.send(
                            embed=embed,
                            components = [
                                ActionRow(
                                    Button(style=ButtonStyle.blue,label = "제품 보기",custom_id="제품"),
                                    Button(style=ButtonStyle.blue,label = "충전 하기",custom_id="충전"),
                                    Button(style=ButtonStyle.blue,label = "정보 확인",custom_id="정보"),
                                    Button(style=ButtonStyle.blue,label = "구매 하기",custom_id="구매"),
                                    Button(style=ButtonStyle.blue, label="공지사항", custom_id="공지"),                              )
                            ]
                        )
                    if color == "빨강":
                        embed = discord.Embed(title='버튼 자판기 안내', description='원하시는 버튼 메뉴를 선택 해주십시요.\n```이용 전 안내사항(필독 요망)\n1. 계좌이체시 입금내역을 고객센터에 보내주세요!\n2. 문화상품권 충전은 자동 충전 입니다```', color=0xff4848)
                        embed.set_thumbnail(url="사진링크넣기")
                        await message.channel.send(
                            embed=embed,
                            components = [
                                ActionRow(
                                    Button(style=ButtonStyle.red,label = "제품 보기",custom_id="제품"),
                                    Button(style=ButtonStyle.red,label = "충전 하기",custom_id="충전"),
                                    Button(style=ButtonStyle.red,label = "정보 확인",custom_id="정보"),
                                    Button(style=ButtonStyle.red,label = "구매 하기",custom_id="구매"),
                                    Button(style=ButtonStyle.red, label="공지사항", custom_id="공지"),
                                )
                            ]
                        )
                    if color == "초록":
                        embed = discord.Embed(title='버튼 자판기 안내', description='원하시는 버튼 메뉴를 선택 해주십시요.\n```이용 전 안내사항(필독 요망)\n1. 계좌이체시 입금내역을 고객센터에 보내주세요!\n2. 문화상품권 충전은 자동 충전 입니다```', color=0x00ff27)
                        embed.set_thumbnail(url="사진링크넣기")
                        await message.channel.send(
                            embed=embed,
                            components = [
                                ActionRow(
                                    Button(style=ButtonStyle.green,label = "제품 보기",custom_id="제품"),
                                    Button(style=ButtonStyle.green,label = "충전 하기",custom_id="충전"),
                                    Button(style=ButtonStyle.green,label = "정보 확인",custom_id="정보"),
                                    Button(style=ButtonStyle.green,label = "구매 하기",custom_id="구매"),
                                    Button(style=ButtonStyle.green, label="공지사항", custom_id="공지"),
                                )
                            ]
                        )
                    if color == "회색":
                        embed = discord.Embed(title='버튼 자판기 안내', description='원하시는 버튼 메뉴를 선택 해주십시요.\n```이용 전 안내사항(필독 요망)\n1. 계좌이체시 입금내역을 고객센터에 보내주세요!\n2. 문화상품권 충전은 자동 충전 입니다```', color=0x444444)
                        embed.set_thumbnail(url="사진링크넣기")
                        await message.channel.send(
                            embed=embed,
                            components = [
                                ActionRow(
                                    Button(style=ButtonStyle.gray,label = "제품 보기",custom_id="제품"),
                                    Button(style=ButtonStyle.gray,label = "충전 하기",custom_id="충전"),
                                    Button(style=ButtonStyle.gray,label = "정보 확인",custom_id="정보"),
                                    Button(style=ButtonStyle.gray,label = "구매 하기",custom_id="구매"),
                                    Button(style=ButtonStyle.gray, label="공지사항", custom_id="공지"), #된거죠? 네
                                )
                            ]
                        )
                    

        if message.content == '!라이센스':
            if message.author.guild_permissions.administrator or message.author.id == int(admin_id):
                if (os.path.isfile("../DB/" + str(message.guild.id) + ".db")):
                    embed = discord.Embed(title='라이센스 안내', description='원하시는 버튼을 클릭해주세요.', color=0x4461ff)
                    embed.set_thumbnail(url="사진링크넣기")
                    await message.channel.send(
                        embed=embed,
                        components = [
                            ActionRow(
                                Button(style=ButtonStyle.blue,label = "연장",custom_id="연장"),
                                Button(style=ButtonStyle.blue,label = "웹패널",custom_id="웹패널"),
                            )
                        ]
                    )
                    
        if message.content == "!수익":
            if message.author.guild_permissions.administrator or message.author.id == int(admin_id):
                if (os.path.isfile("../DB/" + str(message.guild.id) + ".db")):
                    a_day = 0
                    a_week = 0
                    a_month = 0
                    a_year = 0
                    total = 0
                    con = sqlite3.connect("../DB/" + str(message.guild.id) + ".db")
                    cur = con.cursor()
                    cur.execute("SELECT * FROM buy_logs;")
                    buy_logs = cur.fetchall()
                    con.close()
                    if buy_logs != None:
                        for buy_log in buy_logs:
                            def years_to_days(years):
                                return years * 365

                            def months_to_days(months):
                                return months * 30

                            def datetime_diff(now_datetime, ago_datetime):
                                now_date = now_datetime.split(" ")[0].split("-")
                                ago_date = ago_datetime.split(" ")[0].split("-")
                                if int(now_date[0]) >= int(ago_date[0]):
                                    if int(now_date[1]) == int(ago_date[1]):
                                        return 1
                                    else:
                                        now_days = years_to_days(int(now_date[0])) + months_to_days(int(now_date[1])) + int(now_date[2])
                                        ago_days = years_to_days(int(ago_date[0])) + months_to_days(int(ago_date[1])) + int(ago_date[2])
                                    return now_days - ago_days
                                else:
                                    raise

                            diff = datetime_diff(now(), str(buy_log[2]))
                            total += int(buy_log[0])
                            if diff == 1:
                                a_day += int(buy_log[0])
                            elif 1 < diff <= 7:
                                a_week += int(buy_log[0])
                            elif 7 < diff <= 30:
                                a_month += int(buy_log[0])
                            elif 30 < diff <= 365:
                                a_year += int(buy_log[0]) # rr
                        await message.channel.send(embed=discord.Embed(description=f"누적 수익 : `{a_day}원`", color=0x2f3136))
                        open(f"{message.guild.id}.txt", "w").write(str(buy_logs))
                        await message.channel.send(file=discord.File(f"{message.guild.id}.txt"))
                        os.remove(f"{message.guild.id}.txt")
                    else:
                        await message.channel.send(embed=discord.Embed(description=f"구매 기록이 없습니다.", color=0x2f3136))
        if message.content.startswith("!수동충전 "):
            if message.author.guild_permissions.administrator or message.author.id == int(admin_id):
                try:
                    userId = message.mentions[0].id
                except:
                    userId = int(message.content.split(" ")[1])
                try:
                    amount = message.content.split(" ")[2]
                except:
                    return await message.channel.send(embed=discord.Embed(title="수동 충전 실패", description="`!수동충전 @유저멘션 충전금액` 으로 사용해주세요!", color=0x4461ff))
                con = sqlite3.connect("../DB/" + str(message.guild.id) + ".db")
                cur = con.cursor()
                cur.execute("SELECT * FROM users WHERE id == ?;", (userId,))
                user_info = cur.fetchone()
                if not user_info:
                    cur.execute("INSERT INTO users VALUES(?, ?, ?, ?, ?, ?);", (userId, 0, 0, 0, "일반", 0))
                    con.commit()
                    con.close()
                current_money = int(user_info[1])
                now_money = current_money + int(amount)
                cur.execute("UPDATE users SET money = ? WHERE id == ?;", (now_money, userId))
                con.commit()
                await message.channel.send(embed=discord.Embed(title="수동 충전 성공", description=f"관리자: {message.author}\n기존 금액: `{current_money}`\n충전한 금액: `{amount}`\n충전 후 금액: `{now_money}`원", color=0x4461ff))
                
        if message.content == "!구매 메시지":
            if message.author.guild_permissions.administrator or message.author.id == int(admin_id):
                if not isinstance(message.channel, discord.channel.DMChannel):
                    if (os.path.isfile("../DB/" + str(message.guild.id) + ".db")):
                        await message.channel.send("제품 이름을 입력해주세요")
                        def check(msg):
                            return (not isinstance(msg.channel, discord.channel.DMChannel) and (message.author.id == msg.author.id))
                        try:
                            product_name = await client.wait_for("message", timeout=60, check=check)
                        except asyncio.TimeoutError:
                            try:
                                await message.channel.send("시간 초과")
                            except:
                                pass
                            return None
                        await message.channel.send("제품 설명을 입력해주세요")
                        try:
                            product_content = await client.wait_for("message", timeout=60, check=check)
                        except asyncio.TimeoutError:
                            try:
                                await message.channel.send("시간 초과")
                            except:
                                pass
                            return None
                        await message.channel.send("버튼 내용을 입력해주세요")
                        try:
                            button_content = await client.wait_for("message", timeout=60, check=check)
                        except asyncio.TimeoutError:
                            try:
                                await message.channel.send("시간 초과")
                            except:
                                pass
                            return None
                        await message.channel.send(embed=discord.Embed(title=product_name.content, description=product_content.content, color=0x00d6ff),
                        components = [
                            ActionRow(
                                Button(style=ButtonStyle.gray,label=button_content.content,custom_id="구매")
                            )
                        ])

        if message.content == "!도움말":
            if message.author.guild_permissions.administrator or message.author.id == int(admin_id):
                await message.channel.send(embed=discord.Embed(title="도움말", description=f"서버 등록 : !등록 (구매한 라이센스)\n연장 : !라이센스 입력 후 연장 버튼 클릭\n웹패널 확인 : !라이센스 입력 후 웹패널 버튼 클릭\n수동 충전 : !수동충전 (@맨션) (금액)\n서버 이전 : !서버 이전 (서버 아이디) (웹패널 비밀번호)", color=0x4461ff))

@client.event
async def on_button_click(interaction):
    if not isinstance(interaction.channel, discord.channel.DMChannel):
        if (os.path.isfile("../DB/" + str(interaction.guild.id) + ".db")):
            con = sqlite3.connect("../DB/" + str(interaction.guild.id) + ".db")
            cur = con.cursor()
            cur.execute("SELECT * FROM serverinfo;")
            cmdchs = cur.fetchone()
            con.close()
            try:
                tempvar = is_expired(cmdchs[1])
            except:
                os.rename("../DB/" + str(interaction.guild.id) + ".db", "../DB/" + str(interaction.guild.id) + f".db_old{datetime.datetime.now()}")
            if not(is_expired(cmdchs[1])):
                if interaction.responded:
                    return
                try:
                    con = sqlite3.connect("../DB/" + str(interaction.guild.id) + ".db")
                    cur = con.cursor()
                    cur.execute("SELECT * FROM users WHERE id == ?;", (interaction.user.id,))
                    user_info = cur.fetchone()
                    if (user_info == None):
                        cur.execute("INSERT INTO users VALUES(?, ?, ?, ?, ?, ?);", (interaction.user.id, 0, 0, 0, "일반", 0))
                        con.commit()
                        con.close()
                except:
                    pass
                con = sqlite3.connect("../DB/" + str(interaction.guild.id) + ".db")
                cur = con.cursor()
                cur.execute("SELECT * FROM users WHERE id == ?;", (interaction.user.id,))
                user_info = cur.fetchone()
                cur.execute("SELECT * FROM serverinfo;")
                server_info = cur.fetchone()
                con.close()
                color = server_info[14]
                if color == "파랑":
                    color = 0x4461ff
                if color == "빨강":
                    color = 0xff4848
                if color == "초록":
                    color = 0x00ff27
                if color == "회색":
                    color = 0x444444
                webhook_profile_url = server_info[22]
                webhook_name = server_info[23]
                if interaction.custom_id == "제품":
                    con = sqlite3.connect(f"../DB/{interaction.guild.id}.db")
                    cur = con.cursor()
                    cur.execute("SELECT * FROM products;")
                    products = cur.fetchall()
                    con.close()
                    list_embed = discord.Embed(title="제품 목록", color=color)
                    for product in products:
                        if product[2] == "":
                            list_embed.add_field(name=product[0], value="가격: `" + str(product[1]) + "`원\n재고: `0`개", inline=False)
                        else:
                            list_embed.add_field(name=product[0], value="가격: `" + str(product[1]) + "`원\n재고: `" + str(len(product[2].split("\n"))) + "`개", inline=False)
                    await interaction.respond(embed=list_embed)
                   
                if interaction.custom_id == "충전":
                    if color == 0x4461ff:
                        embed = discord.Embed(title='충전수단 선택', description='원하시는 충전수단을 클릭해주세요.', color=color)
                        await interaction.respond(
                            embed=embed,
                            components = [
                                ActionRow(
                                    Button(style=ButtonStyle.blue,label = "문화상품권",custom_id="문상충전"),
                                    Button(style=ButtonStyle.blue,label = "계좌이체",custom_id="계좌충전"),
                                )
                            ]
                        )
                    if color == 0xff4848:
                        embed = discord.Embed(title='충전수단 선택', description='원하시는 충전수단을 클릭해주세요.', color=color)
                        await interaction.respond(
                            embed=embed,
                            components = [
                                ActionRow(
                                    Button(style=ButtonStyle.red,label = "문화상품권",custom_id="문상충전"),
                                    Button(style=ButtonStyle.red,label = "계좌이체",custom_id="계좌충전"),
                                )
                            ]
                        )
                    if color == 0x00ff27:
                        embed = discord.Embed(title='충전수단 선택', description='원하시는 충전수단을 클릭해주세요.', color=color)
                        await interaction.respond(
                            embed=embed,
                            components = [
                                ActionRow(
                                    Button(style=ButtonStyle.green,label = "문화상품권",custom_id="문상충전"),
                                    Button(style=ButtonStyle.green,label = "계좌이체",custom_id="계좌충전"),
                                )
                            ]
                        )
                    if color == 0x444444:
                        embed = discord.Embed(title='충전수단 선택', description='원하시는 충전수단을 클릭해주세요.', color=color)
                        await interaction.respond(
                            embed=embed,
                            components = [
                                ActionRow(
                                    Button(style=ButtonStyle.grey,label = "문화상품권",custom_id="문상충전"),
                                    Button(style=ButtonStyle.grey,label = "계좌이체",custom_id="계좌충전"),
                                )
                            ]
                        )
                    
                if interaction.custom_id == "문상충전":
                    global charginguser
                    con = sqlite3.connect("../DB/" + str(interaction.guild.id) + ".db")
                    cur = con.cursor()
                    cur.execute("SELECT * FROM users WHERE id == ?;", (interaction.user.id,))
                    user_info = cur.fetchone()
                    con.close()
                    con = sqlite3.connect("../DB/" + str(interaction.guild.id) + ".db")
                    cur = con.cursor()
                    cur.execute("SELECT * FROM serverinfo;")
                    server_info = cur.fetchone()
                    con.close()
                    if (server_info[2] != "" and server_info[3] != ""):
                        if not int(user_info[3]) >= int(server_info[15]):
                            if not interaction.user.id in charginguser:
                                charginguser.append(interaction.user.id)
                                try:
                                    await interaction.user.send(embed=discord.Embed(title="문화상품권 충전", description=f"문화상품권 핀번호를 `-`를 포함해서 입력해주세요.\n문화상품권 충전 수수료: {server_info[8]}%", color=color))
                                    await interaction.respond(embed=discord.Embed(title="전송 성공", description="DM을 확인해주세요.", color=color))
                                except:
                                    await interaction.respond(embed=discord.Embed(title="문화상품권 충전 실패", description="DM을 차단하셨거나 메시지 전송 권한이 없습니다.", color=color))
                                    chargingusers = []
                                    for user in charginguser:
                                        if user != interaction.user.id:
                                            chargingusers.append(user)
                                    charginguser = chargingusers
                                    return None

                                def check(msg):
                                    return (isinstance(msg.channel, discord.channel.DMChannel) and (len(msg.content) == 21 or len(msg.content) == 19) and (interaction.user.id == msg.author.id))
                                try:
                                    msg = await client.wait_for("message", timeout=60, check=check)
                                except asyncio.TimeoutError:
                                    try:
                                        chargingusers = []
                                        for user in charginguser:
                                            if user != interaction.user.id:
                                                chargingusers.append(user) # 된듯하네요 확인햅로게용
                                        charginguser = chargingusers
                                        await interaction.user.send(embed=discord.Embed(title="문화상품권 충전 실패", description="시간 초과되었습니다.", color=color))
                                    except:
                                        pass
                                    return None
                                
                                try:
                                    jsondata = {"id" : server_info[2], "pw" : server_info[3], "pin" : msg.content}
                                    res = requests.post("http://127.0.0.1:5000/api", json=jsondata)
                                except Exception as e:
                                    try:
                                        await interaction.user.send(embed=discord.Embed(title="문화상품권 충전 실패", description="일시적인 서버 오류입니다.\n잠시 후 다시 시도해주세요.", color=color))
                                        chargingusers = []
                                        for user in charginguser:
                                            if user != interaction.user.id:
                                                chargingusers.append(user)
                                        charginguser = chargingusers
                                        print(e)
                                    except:
                                        pass
                                    return None
                                res = res.json()
                                if res["result"] == True:
                                    con = sqlite3.connect("../DB/" + str(interaction.guild.id) + ".db")
                                    cur = con.cursor()
                                    cur.execute("SELECT * FROM serverinfo WHERE id == ?;",(interaction.guild.id,))
                                    guild_info = cur.fetchone()
                                    culture_fee = int(guild_info[8])
                                    culture_amount = int(res["amount"])
                                    culture_amount_after_fee = culture_amount - int(culture_amount*(culture_fee/100))
                                    cur = con.cursor()
                                    cur.execute("SELECT * FROM users WHERE id == ?;", (msg.author.id,))
                                    user_info = cur.fetchone()
                                    current_money = int(user_info[1])
                                    now_money = current_money + culture_amount_after_fee
                                    cur.execute("UPDATE users SET money = ? WHERE id == ?;", (now_money, msg.author.id))
                                    con.commit()
                                    con.close()
                                    try:
                                        chargingusers = []
                                        for user in charginguser:
                                            if user != interaction.user.id:
                                                chargingusers.append(user)
                                        charginguser = chargingusers
                                        await interaction.user.send(embed=discord.Embed(title="문화상품권 충전 성공", description=f"핀코드: `{msg.content}`\n금액: `{culture_amount}`원\n충전한 금액: `{culture_amount_after_fee}` (수수료 {culture_fee}%)\n충전 후 금액: `{now_money}`원", color=color))
                                        con = sqlite3.connect("../DB/" + str(interaction.guild.id) + ".db")
                                        cur = con.cursor()
                                        cur.execute("UPDATE users SET warnings = ? WHERE id == ?;", (0, msg.author.id))
                                        con.commit()
                                        con.close()
                                        try:
                                            webhook = DiscordWebhook(username=webhook_name, avatar_url=webhook_profile_url, url=get_logwebhk(interaction.guild.id))
                                            eb = DiscordEmbed(title='문화상품권 충전 성공', description=f'[웹 패널로 이동하기]({domain})', color=color)
                                            eb.add_embed_field(name='디스코드 닉네임', value=f"{msg.author}", inline=False)
                                            eb.add_embed_field(name='핀 코드', value=f"{msg.content}", inline=False)
                                            eb.add_embed_field(name='상품권 금액', value=f"`{culture_amount}`원", inline=False)
                                            eb.add_embed_field(name='충전한 금액', value=f"`{culture_amount_after_fee}`원 (수수료 {culture_fee}%)", inline=False)
                                            webhook.add_embed(eb)
                                            webhook.execute()
                                        except:
                                            pass
                                    except:
                                        pass
                                    
                                else:
                                    con = sqlite3.connect("../DB/" + str(interaction.guild.id) + ".db")
                                    cur = con.cursor()
                                    cur.execute("UPDATE users SET warnings = ? WHERE id == ?;", (user_info[3] + 1, msg.author.id))
                                    con.commit()
                                    con.close()
                                    chargingusers = []
                                    for user in charginguser:
                                        if user != interaction.user.id:
                                            chargingusers.append(user)
                                    charginguser = chargingusers
                                    await interaction.user.send(embed=discord.Embed(title="문화상품권 충전 실패", description="실패 사유 : " + res["reason"], color=color))
                                    try:
                                        webhook = DiscordWebhook(username=webhook_name, avatar_url=webhook_profile_url, url=get_logwebhk(interaction.guild.id))
                                        eb = DiscordEmbed(title='문화상품권 충전 실패', description=f'[웹 패널로 이동하기]({domain})', color=color)
                                        eb.add_embed_field(name='디스코드 닉네임', value=str(msg.author), inline=False)
                                        eb.add_embed_field(name='핀 코드', value=str(msg.content), inline=False)
                                        eb.add_embed_field(name='실패 사유', value=res["reason"], inline=False)
                                        webhook.add_embed(eb)
                                        webhook.execute()
                                    except Exception as e:
                                        pass
                            else:
                                await interaction.respond(embed=discord.Embed(title="문화상품권 충전 실패", description="이미 충전이 진행중입니다.", color=color))
                        else:
                            await interaction.respond(embed=discord.Embed(title="문화상품권 충전 실패", description=f"{server_info[15]}회 연속 충전실패로 충전이 정지되었습니다.\n샵 관리자에게 문의해주세요.", color=color))
                    else:
                        await interaction.respond(embed=discord.Embed(title="문화상품권 충전 실패", description="충전 기능이 비활성화되어 있습니다.\n샵 관리자에게 문의해주세요.", color=color))
                if interaction.custom_id == "계좌충전":
                    con = sqlite3.connect("../DB/" + str(interaction.guild.id) + ".db")
                    cur = con.cursor()
                    cur.execute("SELECT * FROM serverinfo")
                    serverinfo = cur.fetchone()
                    con.close()
                    try:
                        bankdata = json.loads(serverinfo[9])
                        assert len(bankdata['banknum']) > 1
                    except Exception as e:
                        await interaction.respond(embed=discord.Embed(title="계좌정보 불러오기 실패", description="서버에 계좌정보가 등록되어있지 않습니다.\n샵 관리자에게 문의해주세요.", color=color))
                        return
                    try:
                        if not interaction.user.id in charginguser:
                            charginguser.append(interaction.user.id)
                            nam = await interaction.user.send(embed=discord.Embed(description=f"입금자명을 입력해주세요.", color=color))
                            await interaction.respond(embed=discord.Embed(title="전송 성공", description="DM을 확인해주세요.", color=color))
                            def check(name):
                                return (isinstance(name.channel, discord.channel.DMChannel) and (interaction.user.id == name.author.id))
                            try:
                                name = await client.wait_for("message", timeout=60, check=check)
                                await nam.delete()
                                name = name.content
                            except asyncio.TimeoutError:
                                try:
                                    await interaction.user.send(embed=discord.Embed(title="계좌 충전 실패", description="시간 초과되었습니다.", color=color))
                                    chargingusers = []
                                    for user in charginguser:
                                        if user != interaction.user.id:
                                            chargingusers.append(user)
                                    charginguser = chargingusers
                                    return None
                                except:
                                    pass
                                return None
                            mone = await interaction.user.send(embed=discord.Embed(description=f"입금할 액수을 입력해주세요.", color=color))
                            def check(money):
                                return (isinstance(money.channel, discord.channel.DMChannel) and (interaction.user.id == money.author.id))
                            try:
                                money = await client.wait_for("message", timeout=60, check=check)
                                await mone.delete()
                                money = money.content
                            except asyncio.TimeoutError:
                                try:
                                    await interaction.user.send(embed=discord.Embed(title="계좌 충전 실패", description="시간 초과되었습니다.", color=color))
                                    chargingusers = []
                                    for user in charginguser:
                                        if user != interaction.user.id:
                                            chargingusers.append(user)
                                    charginguser = chargingusers
                                    return None
                                except:
                                    pass
                                return None
                            if money.isdigit():
                                await interaction.user.send(embed=discord.Embed(title="계좌 충전", description=f"입금 계좌 : `{bankdata.get('bankname')} {bankdata.get('banknum')} {bankdata.get('bankowner')}`\n입금자명 : `{name}`\n입금 금액 : `{money}`원", color=color))
                                await interaction.user.send(f"{bankdata.get('bankname')} {bankdata.get('banknum')} {bankdata.get('bankowner')}")
                            else:
                                await interaction.user.send(embed=discord.Embed(title="계좌 충전 실패", description=f"올바른 액수를 입력해주세요.", color=color))
                        else:
                            await interaction.user.send(embed=discord.Embed(title="계좌 충전 실패", description=f"이미 충전을 신청 하셨습니다.", color=color))
                    except Exception as e:
                        print(e)
                        return await interaction.respond(embed=discord.Embed(title="계좌 충전 실패", description="DM을 차단하셨거나 메시지 전송 권한이 없습니다.", color=color))
                    try:
                        if money.isdigit():
                            if serverinfo[21] != "":
                                async def waiting():
                                    try:
                                        jsondata = {
                                            "api_key" : "API키젠", "bankpin" : server_info[21], "shop": interaction.guild.id, "userinfo" : name, "userid" : interaction.user.id, "token" : "token", "type" : True, "amount": int(money)
                                        }
                                        loop = asyncio.get_event_loop()
                                        bound = partial(
                                        requests.post, "http://127.0.0.1:1234/bank", json=jsondata)
                                        ms_result = await loop.run_in_executor(None, bound)
                                        print(ms_result)
                                        if ms_result.status_code != 200:
                                            raise TypeError
                                        ms_result = ms_result.json()
                                        print(ms_result)
                                    except:
                                        await interaction.user.send(embed=discord.Embed(title="계좌 충전 실패", description="실패 사유 : 일시적인 서버 오류입니다.", color=color))

                                    if ms_result["result"] == False:
                                        reason = ms_result["reason"]
                                        await interaction.user.send(embed=discord.Embed(title="계좌 충전 실패", description="실패 사유 : " + reason, color=color))
                                        webhook = DiscordWebhook(username=webhook_name, avatar_url=webhook_profile_url, url=get_logwebhk(interaction.guild.id))
                                        eb = DiscordEmbed(title='계좌 충전 실패', description=f'[웹 패널로 이동하기]({domain})', color=color)
                                        eb.add_embed_field(name='디스코드 닉네임', value=str(msg.author), inline=False)
                                        eb.add_embed_field(name='실패 사유', value=reason, inline=False)
                                        webhook.add_embed(eb)
                                        webhook.execute()
                                        return

                                    if ms_result["result"] == True:
                                        userId = interaction.user.id
                                        amount = int(ms_result["count"])
                                        con = sqlite3.connect("../DB/" + str(interaction.guild.id) + ".db")
                                        cur = con.cursor()
                                        cur.execute("SELECT * FROM users WHERE id == ?;", (userId,))
                                        user_info = cur.fetchone()
                                        current_money = int(user_info[1])
                                        now_money = current_money + int(amount)
                                        cur.execute("UPDATE users SET money = ? WHERE id == ?;", (now_money, userId))
                                        con.commit()
                                        con.close()
                                        await interaction.user.send(embed=discord.Embed(title="계좌 충전 성공", description=f"충전되었습니다. {amount}원", color=color))
                                        webhook = DiscordWebhook(username=webhook_name, avatar_url=webhook_profile_url, url=get_logwebhk(interaction.guild.id))
                                        eb = DiscordEmbed(title='계좌 충전 성공', description=f'[웹 패널로 이동하기]({domain})', color=color)
                                        eb.add_embed_field(name='디스코드 닉네임', value=str(msg.author), inline=False)
                                        eb.add_embed_field(name='입금 금액', value=res["amount"], inline=False)
                                        webhook.add_embed(eb)
                                        webhook.execute()

                                futures = [asyncio.ensure_future(waiting())]

                                await asyncio.gather(*futures)
                            else:
                                try:
                                    webhook = DiscordWebhook(username=webhook_name, avatar_url=webhook_profile_url, url=get_logwebhk(interaction.guild.id))
                                    eb = DiscordEmbed(title='계좌이체 충전 요청', description=f'[웹 패널로 이동하기]({domain})', color=color)
                                    eb.add_embed_field(name='디스코드 닉네임', value=f"<@{interaction.user.id}>({interaction.user})", inline=False)
                                    eb.add_embed_field(name='입금자명', value=f"{name}", inline=False)
                                    eb.add_embed_field(name='입금 확인후 충전방법', value=f"!수동충전 <@{interaction.user.id}> {money}", inline=False)
                                    webhook.add_embed(eb)
                                    webhook.execute()
                                except:
                                    pass
                    except:
                        pass
                    
                if interaction.custom_id == "구매":
                    global buyinguser
                    con = sqlite3.connect("../DB/" + str(interaction.guild.id) + ".db")
                    cur = con.cursor()
                    cur.execute("SELECT * FROM products;")
                    products = cur.fetchall()
                    options = []
                    if not interaction.user.id in buyinguser:
                        try:
                            buyinguser.append(interaction.user.id)
                            for product in products:
                                if user_info[4] == "일반":
                                    rank = server_info[10]
                                if user_info[4] == "VIP":
                                    rank = server_info[11]
                                if user_info[4] == "VVIP":
                                    rank = server_info[12]
                                if user_info[4] == "리셀러":
                                    rank = server_info[13]
                                if product[2] == "":
                                    options.append(SelectOption(description=str(product[1] - product[1] * rank/100).split(".")[0]+"원ㅣ재고 0개",label=product[0], value=product[0]))
                                else:
                                    options.append(SelectOption(description=str(product[1] - product[1] * rank/100).split(".")[0]+"원ㅣ재고 "+str(len(product[2].split('\n')))+"개",label=product[0], value=product[0]))
                            gg = await interaction.user.send(embed=discord.Embed(title='제품 선택', description='구매할 제품을 선택해주세요.', color=color)
                                ,
                                components = [
                                    [Select(placeholder="구매하기", options=options)]
                                ]
                            )
                            await interaction.respond(embed=discord.Embed(title="전송 성공", description="DM을 확인해주세요.", color=color))
                        except:
                            buyingusers = []
                            for user in buyinguser:
                                if user != interaction.user.id:
                                    buyingusers.append(user)
                            buyinguser = buyingusers
                            await interaction.respond(embed=discord.Embed(title="전송 실패", description="DM을 막았거나 제품이 없습니다.", color=color))
                            return
                        try:
                            event = await client.wait_for("select_option", timeout=30, check=None)
                            product_name = event.values[0]
                            await gg.delete()
                        except asyncio.TimeoutError:
                            buyingusers = []
                            for user in buyinguser:
                                if user != interaction.user.id:
                                    buyingusers.append(user)
                            buyinguser = buyingusers
                            await gg.delete()
                            await interaction.user.send(embed=discord.Embed(title='구매 실패', description='시간 초과', color=color))
                            return
                        cur.execute("SELECT * FROM products WHERE name = ?;", (str(product_name),))
                        product_info = cur.fetchone()
                        if (product_info != None):
                            if (str(product_info[2]) != ""):
                                info_msg = await interaction.user.send(embed=discord.Embed(title="수량 선택", description="구매하실 수량을 숫자만 입력해주세요.", color=color))
                                def check(msg):
                                    return (msg.author.id == interaction.user.id)
                                try:
                                    msg = await client.wait_for("message", timeout=20, check=check)
                                except asyncio.TimeoutError:
                                    try:
                                        await info_msg.delete()
                                    except:
                                        pass
                                    buyingusers = []
                                    for user in buyinguser:
                                        if user != interaction.user.id:
                                            buyingusers.append(user)
                                    buyinguser = buyingusers
                                    await interaction.user.send(embed=discord.Embed(title="시간 초과", description="처음부터 다시 시도해주세요.", color=color))
                                    return None

                                try:
                                    await info_msg.delete()
                                except:
                                    pass
                                try:
                                    await msg.delete()
                                except:
                                    pass
                                
                                if not msg.content.isdigit() or int(msg.content) == 0:
                                    buyingusers = []
                                    for user in buyinguser:
                                        if user != interaction.user.id:
                                            buyingusers.append(user)
                                    buyinguser = buyingusers
                                    await interaction.user.send(embed=discord.Embed(title="구매 실패", description="수량은 숫자로만 입력해주세요.", color=color))
                                    return None

                                buy_amount = int(msg.content)

                                if (len(product_info[2].split("\n")) >= buy_amount):
                                    if user_info[4] == "일반":
                                        rank = server_info[10]
                                    if user_info[4] == "VIP":
                                        rank = server_info[11]
                                    if user_info[4] == "VVIP":
                                        rank = server_info[12]
                                    if user_info[4] == "리셀러":
                                        rank = server_info[13]
                                    off_amount = product_info[1] * buy_amount * rank/100
                                    buy_money = int(str(product_info[1] * buy_amount - off_amount).split(".")[0])
                                    if (int(user_info[1]) >= product_info[1] * buy_amount - off_amount):
                                        try_msg = await interaction.user.send(embed=discord.Embed(title="구매 진행 중입니다..", color=color))
                                        stocks = product_info[2].split("\n")
                                        bought_stock = []
                                        for n in range(buy_amount):
                                            picked = random.choice(stocks)
                                            bought_stock.append(picked)
                                            stocks.remove(picked)
                                        now_stock = "\n".join(stocks)
                                        now_money = int(user_info[1]) - buy_money
                                        now_bought = int(user_info[2]) + buy_money
                                        con = sqlite3.connect("../DB/" + str(interaction.guild.id) + ".db")
                                        cur = con.cursor()
                                        cur.execute("UPDATE users SET money = ?, bought = ? WHERE id == ?;", (now_money, now_bought, interaction.user.id))
                                        con.commit()
                                        cur.execute("UPDATE products SET stock = ? WHERE name == ?;", (now_stock, product_name))
                                        con.commit()
                                        con.close()
                                        bought_stock = "\n".join(bought_stock)
                                        con = sqlite3.connect("../DB/docs.db")
                                        cur = con.cursor()
                                        docs_name = randomstring.pick(30)
                                        cur.execute("INSERT INTO docs VALUES(?, ?);", (docs_name, bought_stock))
                                        con.commit()
                                        con.close()
                                        docs_url = f"{domain}/rawviewer/" + docs_name
                                        try:
                                            try:
                                                webhook = DiscordWebhook(username=webhook_name, avatar_url=webhook_profile_url, url=get_logwebhk(interaction.guild.id))
                                                eb = DiscordEmbed(title='제품 구매 로그', description=f'[웹 패널로 이동하기]({domain})', color=color)
                                                eb.add_embed_field(name='디스코드 닉네임', value=str(interaction.user), inline=False)
                                                eb.add_embed_field(name='구매 제품', value=str(product_name), inline=False)
                                                eb.add_embed_field(name='구매 개수', value=str(buy_amount), inline=False)
                                                eb.add_embed_field(name='구매 코드', value='[구매한 코드 보기](' + docs_url + ')', inline=False)
                                                webhook.add_embed(eb)
                                                webhook.execute()
                                            except:
                                                pass

                                            try:
                                                webhook = DiscordWebhook(username=webhook_name, avatar_url=webhook_profile_url, url=get_buylogwebhk(interaction.guild.id))
                                                log_text = server_info[18].replace("{user}", "<@" + str(interaction.user.id) + ">")
                                                log_text = log_text.replace("{product_name}", product_name)
                                                log_text = log_text.replace("{amount}", str(buy_amount))
                                                webhook.add_embed(DiscordEmbed(description=log_text, color=color))
                                                webhook.execute()
                                            except:
                                                pass
                                            try:
                                                buyer_role = interaction.guild.get_role(get_roleid(interaction.guild.id))
                                                await interaction.user.add_roles(buyer_role)
                                            except:
                                                pass
                                            await try_msg.delete()
                                            buyingusers = []
                                            for user in buyinguser:
                                                if user != interaction.user.id:
                                                    buyingusers.append(user)
                                                    buyinguser = buyingusers
                                            buyinguser = buyingusers
                                            await interaction.user.send(embed=discord.Embed(title="구매 성공", description=f"제품 이름 : `{product_name}`\n구매 개수 : `{buy_amount}`개\n차감 금액 : `{buy_money}`원", color=color))
                                            open(f"{interaction.user.id}.txt", "w").write(bought_stock.replace("\n", ""))
                                            await interaction.user.send(embed=discord.Embed(title='아래 파란글씨를 클릭하여 구매한상품을 확인가능합니다', description='[구매한 코드 보기](' + docs_url + ')', color=color))
                                            await interaction.user.send(file=discord.File(f"{interaction.user.id}.txt"))
                                            os.remove(f"{interaction.user.id}.txt")
                                            con = sqlite3.connect("../DB/" + str(interaction.guild.id) + ".db")
                                            cur = con.cursor()
                                            cur.execute("UPDATE users SET buycount = ? WHERE id == ?;", (user_info[5] + 1, msg.author.id))
                                            con.commit()
                                            con.close()
                                            try:
                                                if now_bought >= server_info[16]:
                                                    con = sqlite3.connect("../DB/" + str(interaction.guild.id) + ".db")
                                                    cur = con.cursor()
                                                    cur.execute("UPDATE users SET rank = ? WHERE id == ?;", ("VIP", msg.author.id))
                                                    con.commit()
                                                    con.close()
                                                    vip_role = interaction.guild.get_role(server_info[19])
                                                    await interaction.user.add_roles(vip_role)
                                                if now_bought >= server_info[17]:
                                                    con = sqlite3.connect("../DB/" + str(interaction.guild.id) + ".db")
                                                    cur = con.cursor()
                                                    cur.execute("UPDATE users SET rank = ? WHERE id == ?;", ("VVIP", msg.author.id))
                                                    con.commit()
                                                    con.close()
                                                    vvip_role = interaction.guild.get_role(server_info[20])
                                                    await interaction.user.add_roles(vvip_role)
                                                role = interaction.guild.get_role(product_info[3])
                                                await interaction.user.add_roles(role)
                                            except:
                                                pass
                                            con = sqlite3.connect("../DB/" + str(interaction.guild.id) + ".db")
                                            cur = con.cursor()
                                            cur.execute("INSERT INTO buy_logs Values(?, ?, ?);", (buy_money, interaction.user.id, now()))
                                            con.commit()
                                            con.close()
                                            
                                        except:
                                            try:
                                                await try_msg.delete()
                                            except:
                                                buyingusers = []
                                                for user in buyinguser:
                                                    if user != interaction.user.id:
                                                        buyingusers.append(user)
                                                buyinguser = buyingusers
                                                await interaction.user.send(embed=discord.Embed(title="제품 구매 실패", description="제품 구매 중 알 수 없는 오류가 발생했습니다.\n샵 관리자에게 문의해주세요.", color=color))
                                    else:
                                        buyingusers = []
                                        for user in buyinguser:
                                            if user != interaction.user.id:
                                                buyingusers.append(user)
                                        buyinguser = buyingusers
                                        await interaction.user.send(embed=discord.Embed(title="제품 구매 실패", description="잔액이 부족합니다.", color=color))
                                else:
                                    buyingusers = []
                                    for user in buyinguser:
                                        if user != interaction.user.id:
                                            buyingusers.append(user)
                                    buyinguser = buyingusers
                                    await interaction.user.send(embed=discord.Embed(title="제품 구매 실패", description="재고가 부족합니다.", color=color))
                            else:
                                buyingusers = []
                                for user in buyinguser:
                                    if user != interaction.user.id:
                                        buyingusers.append(user)
                                        buyinguser = buyingusers
                                buyinguser = buyingusers
                                await interaction.user.send(embed=discord.Embed(title="제품 구매 실패", description="재고가 부족합니다.", color=color))
                    else:
                        await interaction.respond(embed=discord.Embed(title="구매 실패", description="이미 구매가 진행중입니다.", color=color))

                if interaction.custom_id == "정보":
                    con = sqlite3.connect("../DB/" + str(interaction.guild.id) + ".db")
                    cur = con.cursor()
                    cur.execute("SELECT * FROM users WHERE id == ?;", (interaction.author.id,))
                    user_info = cur.fetchone()
                    con.close()
                    if user_info[4] == "일반":
                        rank = server_info[10]
                    if user_info[4] == "VIP":
                        rank = server_info[11]
                    if user_info[4] == "VVIP":
                        rank = server_info[12]
                    if user_info[4] == "리셀러":
                        rank = server_info[13]
                    await interaction.respond(embed=discord.Embed(title=str(interaction.user.name) + "님의 정보", description="보유 금액: `" + str(user_info[1]) + "`원\n누적 금액: `" + str(user_info[2]) + f"`원\n등급 : `{user_info[4]}`\n할인율 : `{rank}`%\n구매 수 : `{user_info[5]}`회\n경고 수 : `{user_info[3]}`회", color=color))
                    
                if interaction.custom_id == "공지":
                    con = sqlite3.connect("../DB/" + str(interaction.guild.id) + ".db")
                    cur = con.cursor()
                    cur.execute("SELECT * FROM serverinfo")
                    server_info = cur.fetchone()
                    con.close()
                    emm = discord.Embed(
                        title="서버 공지사항",
                        description=server_info[24],
                        color=color
                    )
                    await interaction.respond(embed=emm)
                if interaction.custom_id == "연장":
                    if interaction.user.guild_permissions.administrator or interaction.author.id == int(admin_id):
                        await interaction.user.send(embed=discord.Embed(description="라이센스를 입력해주세요.", color=color))
                        await interaction.respond(embed=discord.Embed(description="DM을 확인해주세요.", color=color))
                        def check(license_key):
                            return (license_key.author.id == interaction.user.id and isinstance(license_key.channel, discord.channel.DMChannel))
                        license_key = await client.wait_for("message", timeout=30, check=check)
                        license_key = license_key.content
                        con = sqlite3.connect("../DB/" + "license.db")
                        cur = con.cursor()
                        cur.execute("SELECT * FROM license WHERE code == ?;", (license_key,))
                        search_result = cur.fetchone()
                        con.close()
                        if (search_result != None):
                            if (search_result[2] == 0):
                                con = sqlite3.connect("../DB/" + "license.db")
                                cur = con.cursor()
                                cur.execute("UPDATE license SET isused = ?, useddate = ?, usedby = ? WHERE code == ?;", (1, nowstr(), str(interaction.guild.id), license_key))
                                con.commit()
                                cur = con.cursor()
                                cur.execute("SELECT * FROM license WHERE code == ?;",(license_key,))
                                key_info = cur.fetchone()
                                con.close()
                                con = sqlite3.connect("../DB/" + str(interaction.guild.id) + ".db")
                                cur = con.cursor()
                                cur.execute("SELECT * FROM serverinfo;")
                                server_info = cur.fetchone()
                                if (is_expired(server_info[1])):
                                    new_expiretime = make_expiretime(key_info[1])
                                else:
                                    new_expiretime = add_time(server_info[1], key_info[1])
                                cur.execute("UPDATE serverinfo SET expiredate = ?;", (new_expiretime,))
                                con.commit()
                                con.close()
                                await interaction.user.send(embed=discord.Embed(description=f"`{key_info[1]}`일이 연장되었습니다.", color=color))
                                print(f"[연장]ㅣGUILD ID : {interaction.guild.id}ㅣUSER ID : {interaction.author.id}ㅣUSER NAME : {interaction.author}ㅣNEW EXPIRETIME : {new_expiretime}ㅣPREVIOUS EXPIRETIME : {server_info[1]}ㅣTIME : {now()}")
                            else:
                                await interaction.user.send(embed=discord.Embed(description="이미 사용된 라이센스입니다.", color=color))
                        else:
                            await interaction.user.send(embed=discord.Embed(description="존재하지 않는 라이센스입니다.", color=color))

                if interaction.custom_id == "웹패널":
                    if interaction.user.guild_permissions.administrator or interaction.author.id == int(admin_id):
                        con = sqlite3.connect("../DB/" + str(interaction.guild.id) + ".db")
                        cur = con.cursor()
                        cur.execute("SELECT * FROM serverinfo;")
                        server_info = cur.fetchone()
                        await interaction.respond(embed=discord.Embed(title="웹패널 정보", description="만료일: `" + server_info[1] + f"`\n웹 패널: {domain}\n아이디: `" +str(interaction.guild.id) + "`\n비밀번호: `" + server_info[4] + "`", color=color))

client.run(setting.token)
