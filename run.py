import discord
import re
import random
import os
import sys
import requests
import json

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)
appdir = os.path.dirname(os.path.abspath(__file__))

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    if not os.path.isdir(appdir+"/dictionary"):
        os.mkdir(appdir+"/dictionary")

@client.event
async def on_message(message):
    #自分を無視
    if message.author == client.user:
        return

    if message.content.startswith("!help"):
        if message.content == "!help early":
            command = ["!generate","!waifu","!trend"]
            await message.channel.send("実装予定コマンドはこれだけだよ。```"+"\n".join(command)+"```")
        #コマンド一覧
        command = ["!pw","!pwa","!weather"]
        #コマンド一覧を整形し定型文に合わせて返信
        await message.channel.send("実装済みコマンドはこれだけだよ。```"+"\n".join(command)+"```")

    #pw追加受け取り
    if message.content.startswith("!pwa"):
        #ユーザーネーム抽出、適合無ければ終了
        username = re.match(r'!pwa .+? ',message.content)
        if username == None or message.content == "!pwa":
            await message.channel.send("構文は!pwa <name> <powerword>でお願いね。")
            return
        else:
            username = username.group()[5:-1]
        #メンバー内で名前の一致する人を検索
        for m in message.guild.members:
            if m.display_name==username or m.name==username:
                await message.channel.send(m.display_name+"さんがパワーワードを言ったんだね！")
                #パワーワードの抽出とギルドIDメンバーID連結のテキストへの追記
                word = message.content[int(6+len(username)):].strip()
                with open(appdir+"/dictionary/"+str(message.channel.guild.id)+str(m.id)+".txt",mode="a") as dictionary:
                    dictionary.write(word+"\n")
                await message.channel.send(word+"を追記したよ！")
                return
        message.channel.send(username+"さんは見つからなかったよ。その人だれ？")
        return
    
    #ユーザー指定pwコマンド受け取り
    if message.content.startswith("!pw "):
        #ユーザーネーム抽出、適合無ければ終了
        username = re.match(r'!pw .+',message.content)
        if username == None or username == "help":
            await message.channel.send("構文は!pw <name>でお願いね。")
            return
        else:
            username = username.group()[4:].strip()

        #メンバー内で名前の一致する人を検索
        for m in message.guild.members:
            if m.display_name==username or m.name==username:
                #パワーワード集の存在チェック、なければ空で生成
                if not os.path.isfile(appdir+"/dictionary/"+str(message.guild.id)+str(m.id)+".txt"):
                    with open(appdir+"/dictionary/"+str(message.guild.id)+str(m.id)+".txt",mode="x") as dictionary:
                        await message.channel.send("パワーワードが登録されてないよー")
                        return
                #パワーワードの読み込みと乱数による選択
                with open(appdir+"/dictionary/"+str(message.guild.id)+str(m.id)+".txt",mode="r") as dictionary:
                    words = [s for s in dictionary.read().split("\n") if s!=""]
                    if len(words) <=1:
                        await message.channel.send(m.display_name+"「"+words[0]+"」")
                    else:
                        await message.channel.send(m.display_name+"「"+words[random.randrange(0,len(words)-1)]+"」")
                return
        
        #ユーザーが存在しない場合は返信して終了
        await message.channel.send(username+"さんは見つからなかったよ。その人だれ？")
        return

    #ユーザー指定なしpwコマンド受け取り
    if message.content == "!pw":
        #ギルドIDの一致するファイル全探索して一時リストに追加
        words = list()
        for f in os.listdir(appdir+"/dictionary"):
            if re.match(str(message.channel.guild.id),f) != None:
                with open(appdir+"/dictionary/"+f,mode="r") as dictionary:
                    words += [s for s in dictionary.read().split("\n") if s!=""]
        #PWリストが見つかれば乱数で選択して返信、見つからなければ返信
        if len(words) <= 0:
            await message.channel.send("このサーバーではまだPowerwordが登録されてないよ。!pwaで追加よろしく！")
            
        else:
            await message.channel.send(words[random.randrange(0,len(words))])
        return

    if message.content.startswith("!generate"):
        await message.channel.send("パワーワードを生成")
    if message.content.startswith("!waifu"):
        await message.channel.send("Waifuを生成")
    if message.content.startswith("!trend"):
        await message.channel.send("現在のTwitterトレンドを報告")
    if message.content.startswith("!weather"):
        #Embedと色を用意
        rc = lambda: random.randint(0, 255)
        embed = discord.Embed(color=discord.Colour.from_rgb(rc(),rc(),rc()))
        #地点のリストでgetして追記、札幌,仙台,東京,名古屋,大阪,広島,福岡
        for city in ["016010","040010","130010","230010","270000","340010","400010"]:
            res = requests.get("https://weather.tsukumijima.net/api/forecast/city/"+city)
            data = res.json()
            telop = list()
            telop.append("天気:"+data["forecasts"][0]["telop"])
            if data["forecasts"][0]["temperature"]["min"]["celsius"] != None or data["forecasts"][0]["temperature"]["max"]["celsius"] != None:
                telop.append("気温:"+data["forecasts"][0]["temperature"]["min"]["celsius"]+"-"+data["forecasts"][0]["temperature"]["max"]["celsius"]+"℃")
            else:
                telop.append("気温:"+"-"+"℃")
            telop.append("降水確率:"+data["forecasts"][0]["chanceOfRain"]["T00_06"][:-1]+"-"+data["forecasts"][0]["chanceOfRain"]["T06_12"][:-1]+"-"+data["forecasts"][0]["chanceOfRain"]["T12_18"][:-1]+"-"+data["forecasts"][0]["chanceOfRain"]["T18_24"]+"\n")
            embed.add_field(name=data["title"][4:-4],value=",".join(telop))
        await message.channel.send("今日の天気です。",embed=embed)
        return


#ファイルのトークンを探した後無ければ引数を読む、どちらもなければ終了
try:
    with open(appdir+"/token","r") as token:
        client.run(token.read())
except:
    try:
        client.run(sys.argv[1])
    except:
        with open(appdir+"/token","a") as token:
            token.write("")
        print("tokenがありません")
