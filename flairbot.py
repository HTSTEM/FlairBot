import discord, time, asyncio

prefix = "!"
client = discord.Client()
flairs = [ #(role_name, twower/command name)
    ('#TeamMeester','Meester'),
    ('#TeamMidnight','Midnight'),
    ('#TeamYessoan','Yessoan')
]

debug = True #set false for normal use

server_id = owner_id = None
if debug:
    server_id = '297811083308171264'
    owner_id = '240995021208289280'

else:
    server_id ='184755239952318464'
    owner_id = '140564059417346049'
    
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
    
    htc = client.get_server(server_id)
    bot = htc.get_member(client.user.id)  
    owner = htc.get_member(owner_id)        
    inHTC = (htc.get_member(message.author.id) != None)
    isOwner = (owner.id == message.author.id)

    if isOwner:
        if command == "permcheck":
            hasPerm = bot.server_permissions.manage_roles
            if not hasPerm:
                print("**Alert:** The bot does not have permission to manage roles.")
            else:
                print("The bot currently has permission to manage roles.")

        if command == "teamstats":
            await client.request_offline_members(htc)
            role_counts = {}
            for role, name in flairs:
                role_counts[name] = get_role_count(role,htc)
                
            print ("--- FLAIR STATS ---")
            for name, count in role_counts.items():
                print('{}: {}'.format(name,count))

            print ("--- END STATS ---")

    if (command == "help" and message.channel.name != "music" and
      (message.channel.is_private or message.server.id == server_id)):
        names = ['`!{}`'.format(name.lower()) for flair, name in flairs]
        if len(names) > 1:
            names[-1] = 'or {}'.format(names[-1])
        await client.send_message(message.channel,
            'To join a team, say {}. To leave your team, say `!remove`'.format(', '.join(names)))

    try:
        if (inHTC and not message.channel.name in ['serious','music'] and
          (message.channel.is_private or message.server.id == server_id)):
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
                        await client.remove_roles(user,role)
                        try:
                            user.roles.remove(role)
                        except:
                            pass
                
                sent_message = None
                if removed:
                    sent_message = await client.send_message(message.channel,"You have successfully been removed from your team.")
                else:
                    sent_message = await client.send_message(message.channel,"You're not on a team!")
                if not message.channel.is_private:
                    try:
                        await client.delete_message(message)
                    except:
                        pass
                    await asyncio.sleep(5)
                    await client.delete_message(sent_message)

            else:
                for role_name, name in flairs:
                    if command == name.lower():
                        for role in teams:
                            if role in user.roles:
                                await client.remove_roles(user,role)
                                try:
                                    user.roles.remove(role)
                                except:
                                    pass

                        team = discord.utils.get(teams,name=role_name)
                        await client.add_roles(user,team)
                        sent_message = await client.send_message(message.channel,"You have joined {}.".format(role_name))
                        if not message.channel.is_private:
                            try:
                                await client.delete_message(message)
                            except:
                                pass
                            await asyncio.sleep(5)
                            await client.delete_message(sent_message)

    except Exception as e:
        if debug:
            raise e
        else:
            print("[ERROR] A bot-crashing error occured somewhere in the code.")

def get_role_count(role_name,server):
    team = discord.utils.get(server.roles,name=role_name)
    count = len(
                list(
                    filter(
                        lambda x:team in x.roles,
                        server.members
                    )
                )
            )
    return count


client.run(open("bot-token.txt").read().split("\n")[0])
