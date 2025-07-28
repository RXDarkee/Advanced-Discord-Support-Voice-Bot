import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import traceback
import sys
import time
from datetime import datetime
import random
from typing import Dict, List


#  |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||

#  |||||||||| IF YOUR USING THIS BOT, PLEASE GIVE CREDIT TO THE DEVELOPER ||||||||||
#  \\\\\\\\\\ Please Remember To Join My Server For Updates And Support ///////////
#     \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\/////////////////////////////////////
#                 <<<<<<<< https://discord.gg/ZseggnJZzV >>>>>>>>>

#  ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||



# Loading environment variables
load_dotenv()

# Configuration Variables
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
DISCORD_SERVER_ID_STR = os.getenv("DISCORD_SERVER_ID")
WAIT_FOR_SUPPORT_CHANNEL_ID_STR = os.getenv("WAIT_FOR_SUPPORT_CHANNEL_ID")
ADMIN_ROLE_ID_STR = os.getenv("ADMIN_ROLE_ID")

# Validated Configuration
VALIDATED_DISCORD_SERVER_ID = None
VALIDATED_WAIT_FOR_SUPPORT_CHANNEL_ID = None
VALIDATED_ADMIN_ROLE_ID = None

# Message tracking
user_welcome_msgs: Dict[int, List[int]] = {}  # {user_id: [message_ids]}
staff_alert_msgs: Dict[int, List[int]] = {}   # {user_id: [message_ids]}

# Image URLs for embeds (replace with your own)
WELCOME_IMAGE = "https://cdn.discordapp.com/attachments/1338114250161524787/1368695350835282070/GIF1.gif?ex=6887e660&is=688694e0&hm=84735159f7c22dcfeb8592bef8298c092bc7c5d9cff88b0ae8c97cf685e777fb&"  # Welcome banner image
STAFF_ALERT_IMAGE = "https://cdn.discordapp.com/attachments/1338114250161524787/1368695350835282070/GIF1.gif?ex=6887e660&is=688694e0&hm=84735159f7c22dcfeb8592bef8298c092bc7c5d9cff88b0ae8c97cf685e777fb&"  # Staff alert image
BOT_AVATAR = "https://cdn.discordapp.com/attachments/1399310612877676578/1399311154400202762/VszAAM6.png?ex=68888991&is=68873811&hm=c2de95212ad1ea334d2b7d30972b286ab5bebb504639555efab989fb01318974&"  # Bot avatar/thumbnail

# Color palette for embeds
EMBED_COLORS = {
   "welcome": 0x00ff00,  # Green
    "alert": 0xff0000,    # Red
    "info": 0x3498db      # Blue
}

def validate_and_load_config():
    """Validate and load configuration from .env"""
    global VALIDATED_DISCORD_SERVER_ID, VALIDATED_WAIT_FOR_SUPPORT_CHANNEL_ID, VALIDATED_ADMIN_ROLE_ID

    print("\n--- Starting Configuration Validation ---")

    if not DISCORD_BOT_TOKEN:
        print("CRITICAL ERROR: DISCORD_BOT_TOKEN not set in .env!")
        return False

    # Server ID validation
    if not DISCORD_SERVER_ID_STR or not DISCORD_SERVER_ID_STR.isdigit():
        print("CRITICAL ERROR: Invalid DISCORD_SERVER_ID in .env!")
        return False
    VALIDATED_DISCORD_SERVER_ID = int(DISCORD_SERVER_ID_STR)

    # Voice Channel ID validation
    if not WAIT_FOR_SUPPORT_CHANNEL_ID_STR or not WAIT_FOR_SUPPORT_CHANNEL_ID_STR.isdigit():
        print("CRITICAL ERROR: Invalid WAIT_FOR_SUPPORT_CHANNEL_ID in .env!")
        return False
    VALIDATED_WAIT_FOR_SUPPORT_CHANNEL_ID = int(WAIT_FOR_SUPPORT_CHANNEL_ID_STR)

    # Admin Role ID validation
    if not ADMIN_ROLE_ID_STR or not ADMIN_ROLE_ID_STR.isdigit():
        print("CRITICAL ERROR: Invalid ADMIN_ROLE_ID in .env!")
        return False
    VALIDATED_ADMIN_ROLE_ID = int(ADMIN_ROLE_ID_STR)

    print("--- Configuration Validation Complete ---")
    return True

# Initialize bot with intents
intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.voice_states = True
intents.dm_messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

async def send_welcome_embed(member: discord.Member, guild: discord.Guild, channel: discord.VoiceChannel):
    """Send a welcome embed to the user who joined the support channel"""
    embed = discord.Embed(
        title="🎉 Welcome to Support! 🎉",
        description=f"Thanks for joining the **Support Waiting Room** in **{guild.name}**!",
        color=EMBED_COLORS["welcome"],
        timestamp=datetime.utcnow()
    )
    
    embed.set_thumbnail(url=BOT_AVATAR)
    embed.set_image(url=WELCOME_IMAGE)
    
    embed.add_field(
        name="What happens next?",
        value="Our staff has been notified and will be with you shortly. Please wait patiently in the voice channel.",
        inline=False
    )
    
    embed.add_field(
        name="Quick Links",
        value=f"[Jump to Voice Channel](https://discord.com/channels/{guild.id}/{channel.id})",
        inline=False
    )
    
    embed.set_footer(
        text=f"{guild.name} Support System",
        icon_url=guild.icon.url if guild.icon else None
    )
    

    # Made By Rasan Fernando Mh Motivation = Tharu***, My Lv. Thanks To Her I Made This Bot

    try:
        msg = await member.send(embed=embed)
        # Track the message
        if member.id not in user_welcome_msgs:
            user_welcome_msgs[member.id] = []
        user_welcome_msgs[member.id].append(msg.id)
        return True
    except discord.Forbidden:
        print(f"Couldn't DM user {member.id} - DMs disabled")
        return False
    except Exception as e:
        print(f"Error sending welcome embed: {str(e)}")
        return False

async def send_staff_alert(member: discord.Member, guild: discord.Guild, channel: discord.VoiceChannel, staff_member: discord.Member):
    """Send a staff alert embed to admin team members"""
    embed = discord.Embed(
        title="🚨 Support Needed! 🚨",
        description=f"**{member.name}** is waiting in the support channel!",
        color=EMBED_COLORS["alert"],
        timestamp=datetime.utcnow()
    )
    
    embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
    embed.set_image(url=STAFF_ALERT_IMAGE)
    
    embed.add_field(
        name="User Details",
        value=f"• Name: {member.mention}\n• ID: `{member.id}`\n• Joined: {member.joined_at.strftime('%b %d, %Y') if member.joined_at else 'Unknown'}",
        inline=True
    )
    
    embed.add_field(
        name="Channel",
        value=f"{channel.mention}\n[Jump to Channel](https://discord.com/channels/{guild.id}/{channel.id})",
        inline=True
    )
    
    embed.add_field(
        name="Account Created",
        value=member.created_at.strftime('%b %d, %Y') if member.created_at else 'Unknown',
        inline=False
    )
    
    embed.set_footer(
        text=f"{guild.name} Support System • {datetime.now().strftime('%H:%M %p')}",
        icon_url=guild.icon.url if guild.icon else None
    )
    
    try:
        msg = await staff_member.send(embed=embed)
        # Track the message
        if member.id not in staff_alert_msgs:
            staff_alert_msgs[member.id] = []
        staff_alert_msgs[member.id].append(msg.id)
        return True
    except discord.Forbidden:
        print(f"Couldn't DM staff {staff_member.id} - DMs disabled")
        return False
    except Exception as e:
        print(f"Error sending staff alert: {str(e)}")
        return False

async def delete_user_messages(user_id: int):
    """Delete all tracked messages for a user"""
    try:
        # Delete welcome message to user
        if user_id in user_welcome_msgs:
            user = await bot.fetch_user(user_id)
            for msg_id in user_welcome_msgs[user_id]:
                try:
                    msg = await user.fetch_message(msg_id)
                    await msg.delete()
                except (discord.NotFound, discord.Forbidden):
                    continue
            del user_welcome_msgs[user_id]

        # Delete staff alert messages about this user
        if user_id in staff_alert_msgs:
            guild = bot.get_guild(VALIDATED_DISCORD_SERVER_ID)
            if guild:
                admin_role = guild.get_role(VALIDATED_ADMIN_ROLE_ID)
                if admin_role:
                    staff_members = [m for m in guild.members if admin_role in m.roles]
                    for msg_id in staff_alert_msgs[user_id]:
                        for staff in staff_members:
                            try:
                                msg = await staff.fetch_message(msg_id)
                                await msg.delete()
                                break  # Found and deleted, move to next message
                            except (discord.NotFound, discord.Forbidden):
                                continue
            del staff_alert_msgs[user_id]
    except Exception as e:
        print(f"Error deleting messages for user {user_id}: {str(e)}")

@bot.event
async def on_ready():
    """Bot startup handler"""
    print(f'\nBot logged in as {bot.user.name} ({bot.user.id})')
    print(f'Discord.py version: {discord.__version__}')
    
    # Validate we can access all required resources
    target_guild = bot.get_guild(VALIDATED_DISCORD_SERVER_ID)
    if not target_guild:
        print(f"CRITICAL ERROR: Bot is not in server {VALIDATED_DISCORD_SERVER_ID}")
        await bot.close()
        return
    
    wait_channel = target_guild.get_channel(VALIDATED_WAIT_FOR_SUPPORT_CHANNEL_ID)
    if not wait_channel or not isinstance(wait_channel, discord.VoiceChannel):
        print(f"CRITICAL ERROR: Invalid wait channel {VALIDATED_WAIT_FOR_SUPPORT_CHANNEL_ID}")
        await bot.close()
        return
    
    admin_role = target_guild.get_role(VALIDATED_ADMIN_ROLE_ID)
    if not admin_role:
        print(f"CRITICAL ERROR: Invalid admin role {VALIDATED_ADMIN_ROLE_ID}")
        await bot.close()
        return
    
    print("--- All systems operational ---")
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching,
        name=f"{wait_channel.name}"
    ))

@bot.event
async def on_voice_state_update(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
    """Handle voice channel joins and leaves"""
    # Skip if not a human user
    if member.bot:
        return
    
    # Check if joining our target channel
    if (not before.channel and after.channel and 
        after.channel.id == VALIDATED_WAIT_FOR_SUPPORT_CHANNEL_ID and
        member.guild.id == VALIDATED_DISCORD_SERVER_ID):
        
        print(f"User {member.name} joined support channel")
        
        # Get required objects
        guild = bot.get_guild(VALIDATED_DISCORD_SERVER_ID)
        channel = guild.get_channel(VALIDATED_WAIT_FOR_SUPPORT_CHANNEL_ID)
        admin_role = guild.get_role(VALIDATED_ADMIN_ROLE_ID)
        
        # Send welcome message to user
        await send_welcome_embed(member, guild, channel)
        
        # Notify staff
        notified_staff = 0
        failed_staff = 0
        
        try:
            # Try to fetch fresh member list first
            staff_members = [m async for m in guild.fetch_members(limit=None) 
                            if not m.bot and admin_role in m.roles and m.id != member.id]
        except discord.Forbidden:
            # Fallback to cached members if we can't fetch
            staff_members = [m for m in guild.members 
                           if not m.bot and admin_role in m.roles and m.id != member.id]
        
        for staff in staff_members:
            success = await send_staff_alert(member, guild, channel, staff)
            if success:
                notified_staff += 1
            else:
                failed_staff += 1
        
        print(f"Notified {notified_staff} staff members ({failed_staff} failed)")
    
    # Check if leaving our target channel
    elif (before.channel and before.channel.id == VALIDATED_WAIT_FOR_SUPPORT_CHANNEL_ID and
          (not after.channel or after.channel.id != VALIDATED_WAIT_FOR_SUPPORT_CHANNEL_ID) and
          member.guild.id == VALIDATED_DISCORD_SERVER_ID):
        
        print(f"User {member.name} left support channel")
        await delete_user_messages(member.id)

@bot.event
async def on_error(event, *args, **kwargs):
    """Global error handler"""
    print(f'\nError in event {event}:')
    traceback.print_exc()

# Main execution
if __name__ == '__main__':
    print("Starting Support Bot...")
    
    if not validate_and_load_config():
        print("\nInvalid configuration - check your .env file")
        sys.exit(1)
    
    try:
        bot.run(DISCORD_BOT_TOKEN)
    except discord.LoginFailure:
        print("\nFailed to login - check your bot token")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nBot shutting down...")
    except Exception as e:
        print(f"\nFatal error: {str(e)}")
        sys.exit(1)