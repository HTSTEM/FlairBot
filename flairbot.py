import discord

prefix = "!"
client = discord.Client()
flairs = { #(role_name, twower/command name)
    'meester': '#TeamMeester',
    'midnight': '#TeamMidnight',
    'yessoan': '#TeamYessoan'
}

debug = True #set false for normal use

guild_id = owner_id = None
if debug:
    guild_id = 297811083308171264
    owner_id = 240995021208289280

else:
    guild_id =184755239952318464
    owner_id = 140564059417346049
    
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_message(message):
    if (not message.content.startswith(prefix)) or message.content.startswith(prefix+prefix):
        return
    
    command = message.content.split(' ')[0][len(prefix):].lower()
    
    htc = client.get_guild(guild_id)
    bot = htc.get_member(client.user.id)  
    owner = htc.get_member(owner_id)        
    inHTC = (htc.get_member(message.author.id) != None)
    isOwner = (owner.id == message.author.id)

    if isOwner:
        if command == "permcheck":
            hasPerm = bot.guild_permissions.manage_roles
            if not hasPerm:
                print("**Alert:** The bot does not have permission to manage roles.")
            else:
                print("The bot currently has permission to manage roles.")

        if command == "teamstats":
            if htc.large: await client.request_offline_members(htc)
            role_counts = {}
            for name, role in flairs.items():
                role_counts[name] = get_role_count(role,htc)
                
            print ("--- FLAIR STATS ---")
            for name, count in role_counts.items():
                print('{}: {}'.format(name.title(),count))

            print ("--- END STATS ---")

    if (command == "help" and message.channel.name != "music" and
      (isinstance(message.channel, discord.abc.PrivateChannel) or message.guild.id == guild_id)):
        names = ['`!{}`'.format(name.lower()) for name in flairs.keys()]
        if len(names) > 1:
            names[-1] = 'or {}'.format(names[-1])
        await message.channel.send(
            'To join a team, say {}. To leave your team, say `!remove`'.format(', '.join(names))
        )

    try:
        if (inHTC and not message.channel.name in ['serious','music'] and
          (isinstance(message.channel, discord.abc.PrivateChannel) or message.guild.id == guild_id)):
            user = htc.get_member(message.author.id)
            roles = htc.roles
            teams =[]

            for role in roles:
                if role.name.startswith("#Team"):
                    teams.append(role)

            if command == "remove":
                removed = False
                for role in teams:
                    if role in user.roles:
                        removed = True
                        await user.remove_roles(role)

                
                sent_message = None
                if removed:  d = "You have successfully been removed from your team."
                else: d = "You're not on a team!"

                if isinstance(message.channel, discord.abc.PrivateChannel):
                    await message.channel.send(d)
                else:
                    await message.channel.send(d, delete_after=5)

                    try: await message.delete()
                    except discord.Forbidden: pass

            else:
                if command in flairs:
                    for role in teams:
                        if role in user.roles:
                            await user.remove_roles(role)


                    team = discord.utils.get(teams,name=flairs[command])
                    await user.add_roles(team)

                    if isinstance(message.channel, discord.abc.PrivateChannel):
                        await message.channel.send("You have joined {}.".format(team.name))
                    else:
                        await message.channel.send(
                            "You have joined {}.".format(team.name),
                            delete_after=5
                        )
                        try: await message.delete()
                        except: pass


    except Exception as e:
        if debug:
            raise e
        else:
            print("[ERROR] A bot-crashing error occured somewhere in the code.")

def get_role_count(role_name, guild):
    team = discord.utils.get(guild.roles,name=role_name)
    count = len(
                list(
                    filter(
                        lambda x:team in x.roles,
                        guild.members
                    )
                )
            )
    return count


client.run(open("bot-token.txt").read().split("\n")[0])
