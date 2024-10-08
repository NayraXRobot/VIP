#
# Copyright (C) 2024 by THE-VIP-BOY-OP@Github, < https://github.com/THE-VIP-BOY-OP >.
#
# This file is part of < https://github.com/THE-VIP-BOY-OP/VIP-MUSIC > project,
# and is released under the MIT License.
# Please see < https://github.com/THE-VIP-BOY-OP/VIP-MUSIC/blob/master/LICENSE >
#
# All rights reserved.
#
import asyncio
import math
import os
import shutil
import socket
from datetime import datetime

import dotenv
import heroku3
import requests
import urllib3
from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError
from pyrogram import filters

import config
from strings import get_command
from VIPMUSIC import app
from VIPMUSIC.misc import HAPP, SUDOERS, XCB
from VIPMUSIC.utils.database import (
    get_active_chats,
    remove_active_chat,
    remove_active_video_chat,
)
from VIPMUSIC.utils.decorators.language import language
from VIPMUSIC.utils.pastebin import VIPbin

# Commands
GETLOG_COMMAND = get_command("GETLOG_COMMAND")
GETVAR_COMMAND = get_command("GETVAR_COMMAND")
DELVAR_COMMAND = get_command("DELVAR_COMMAND")
SETVAR_COMMAND = get_command("SETVAR_COMMAND")
USAGE_COMMAND = get_command("USAGE_COMMAND")
UPDATE_COMMAND = get_command("UPDATE_COMMAND")
RESTART_COMMAND = get_command("RESTART_COMMAND")

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


async def is_heroku():
    return "heroku" in socket.getfqdn()


async def paste_neko(code: str):
    return await VIPbin(code)


@app.on_message(
    filters.command(["log", "logs", "get_log", "getlog", "get_logs", "getlogs"])
    & SUDOERS
)
@language
async def log_(client, message, _):
    try:
        if await is_heroku():
            if HAPP is None:
                return await message.reply_text(_["heroku_1"])
            data = HAPP.get_log()
            link = await VIPbin(data)
            return await message.reply_text(link)
        else:
            if os.path.exists(config.LOG_FILE_NAME):
                log = open(config.LOG_FILE_NAME)
                lines = log.readlines()
                data = ""
                try:
                    NUMB = int(message.text.split(None, 1)[1])
                except:
                    NUMB = 100
                for x in lines[-NUMB:]:
                    data += x
                link = await paste_neko(data)
                return await message.reply_text(link)
            else:
                return await message.reply_text(_["heroku_2"])
    except Exception as e:
        print(e)
        await message.reply_text(_["heroku_2"])


@app.on_message(filters.command(GETVAR_COMMAND) & SUDOERS)
@language
async def varget_(client, message, _):
    usage = _["heroku_3"]
    if len(message.command) != 2:
        return await message.reply_text(usage)
    check_var = message.text.split(None, 2)[1]
    if await is_heroku():
        if HAPP is None:
            return await message.reply_text(_["heroku_1"])
        heroku_config = HAPP.config()
        if check_var in heroku_config:
            return await message.reply_text(
                f"**{check_var}:** `{heroku_config[check_var]}`"
            )
        else:
            return await message.reply_text(_["heroku_4"])
    else:
        path = dotenv.find_dotenv()
        if not path:
            return await message.reply_text(_["heroku_5"])
        output = dotenv.get_key(path, check_var)
        if not output:
            await message.reply_text(_["heroku_4"])
        else:
            return await message.reply_text(f"**{check_var}:** `{str(output)}`")


@app.on_message(filters.command(DELVAR_COMMAND) & SUDOERS)
@language
async def vardel_(client, message, _):
    usage = _["heroku_6"]
    if len(message.command) != 2:
        return await message.reply_text(usage)
    check_var = message.text.split(None, 2)[1]
    if await is_heroku():
        if HAPP is None:
            return await message.reply_text(_["heroku_1"])
        heroku_config = HAPP.config()
        if check_var in heroku_config:
            await message.reply_text(_["heroku_7"].format(check_var))
            del heroku_config[check_var]
        else:
            return await message.reply_text(_["heroku_4"])
    else:
        path = dotenv.find_dotenv()
        if not path:
            return await message.reply_text(_["heroku_5"])
        output = dotenv.unset_key(path, check_var)
        if not output[0]:
            return await message.reply_text(_["heroku_4"])
        else:
            await message.reply_text(_["heroku_7"].format(check_var))
            os.system(f"kill -9 {os.getpid()} && python3 -m VIPMUSIC")


@app.on_message(filters.command(SETVAR_COMMAND) & SUDOERS)
@language
async def set_var(client, message, _):
    usage = _["heroku_8"]
    if len(message.command) < 3:
        return await message.reply_text(usage)
    to_set = message.text.split(None, 2)[1].strip()
    value = message.text.split(None, 2)[2].strip()
    if await is_heroku():
        if HAPP is None:
            return await message.reply_text(_["heroku_1"])
        heroku_config = HAPP.config()
        if to_set in heroku_config:
            await message.reply_text(_["heroku_9"].format(to_set))
        else:
            await message.reply_text(_["heroku_10"].format(to_set))
        heroku_config[to_set] = value
    else:
        path = dotenv.find_dotenv()
        if not path:
            return await message.reply_text(_["heroku_5"])
        dotenv.set_key(path, to_set, value)
        if dotenv.get_key(path, to_set):
            await message.reply_text(_["heroku_9"].format(to_set))
        else:
            await message.reply_text(_["heroku_10"].format(to_set))
        os.system(f"kill -9 {os.getpid()} && python3 -m VIPMUSIC")


@app.on_message(filters.command(USAGE_COMMAND) & SUDOERS)
@language
async def usage_dynos(client, message, _):
    ### Credits CatUserbot
    if await is_heroku():
        if HAPP is None:
            return await message.reply_text(_["heroku_1"])
    else:
        return await message.reply_text(_["heroku_11"])
    dyno = await message.reply_text(_["heroku_12"])
    Heroku = heroku3.from_key(config.HEROKU_API_KEY)
    account_id = Heroku.account().id
    useragent = (
        "Mozilla/5.0 (Linux; Android 10; SM-G975F) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/80.0.3987.149 Mobile Safari/537.36"
    )
    headers = {
        "User-Agent": useragent,
        "Authorization": f"Bearer {config.HEROKU_API_KEY}",
        "Accept": "application/vnd.heroku+json; version=3.account-quotas",
    }
    path = "/accounts/" + account_id + "/actions/get-quota"
    r = requests.get("https://api.heroku.com" + path, headers=headers)
    if r.status_code != 200:
        return await dyno.edit("Unable to fetch.")
    result = r.json()
    quota = result["account_quota"]
    quota_used = result["quota_used"]
    remaining_quota = quota - quota_used
    percentage = math.floor(remaining_quota / quota * 100)
    minutes_remaining = remaining_quota / 60
    hours = math.floor(minutes_remaining / 60)
    minutes = math.floor(minutes_remaining % 60)
    App = result["apps"]
    try:
        App[0]["quota_used"]
    except IndexError:
        AppQuotaUsed = 0
        AppPercentage = 0
    else:
        AppQuotaUsed = App[0]["quota_used"] / 60
        AppPercentage = math.floor(App[0]["quota_used"] * 100 / quota)
    AppHours = math.floor(AppQuotaUsed / 60)
    AppMinutes = math.floor(AppQuotaUsed % 60)
    await asyncio.sleep(1.5)
    text = f"""
**Dʏɴᴏ Usᴀɢᴇ**

<u>Usᴀɢᴇ:</u>
Tᴏᴛᴀʟ ᴜsᴇᴅ: `{AppHours}`**ʜ**  `{AppMinutes}`**ᴍ**  [`{AppPercentage}`**%**]

<u>Rᴇᴀᴍɪɴɪɴɢ ǫᴜᴏᴛᴀ:</u>
Tᴏᴛᴀʟ ʟᴇғᴛ: `{hours}`**ʜ**  `{minutes}`**ᴍ**  [`{percentage}`**%**]"""
    return await dyno.edit(text)


@app.on_message(filters.command(["update", "gitpull", "up"]) & SUDOERS)
@language
async def update_(client, message, _):
    if await is_heroku():
        if HAPP is None:
            return await message.reply_text(_["heroku_1"])
    response = await message.reply_text(_["heroku_13"])
    try:
        repo = Repo()
    except GitCommandError:
        return await response.edit(_["heroku_14"])
    except InvalidGitRepositoryError:
        return await response.edit(_["heroku_15"])
    to_exc = f"git fetch origin {config.UPSTREAM_BRANCH} &> /dev/null"
    os.system(to_exc)
    await asyncio.sleep(7)
    verification = ""
    REPO_ = repo.remotes.origin.url.split(".git")[0]
    for checks in repo.iter_commits(f"HEAD..origin/{config.UPSTREAM_BRANCH}"):
        verification = str(checks.count())
    if verification == "":
        return await response.edit("» ʙᴏᴛ ɪs ᴜᴘ-ᴛᴏ-ᴅᴀᴛᴇ.")
    ordinal = lambda format: "%d%s" % (
        format,
        "tsnrhtdd"[(format // 10 % 10 != 1) * (format % 10 < 4) * format % 10 :: 4],
    )
    updates = "".join(
        f"<b>➣ #{info.count()}: <a href={REPO_}/commit/{info}>{info.summary}</a> ʙʏ -> {info.author}</b>\n\t\t\t\t<b>➥ ᴄᴏᴍᴍɪᴛᴇᴅ ᴏɴ :</b> {ordinal(int(datetime.fromtimestamp(info.committed_date).strftime('%d')))} {datetime.fromtimestamp(info.committed_date).strftime('%b')}, {datetime.fromtimestamp(info.committed_date).strftime('%Y')}\n\n"
        for info in repo.iter_commits(f"HEAD..origin/{config.UPSTREAM_BRANCH}")
    )
    _update_response_ = "**ᴀ ɴᴇᴡ ᴜᴩᴅᴀᴛᴇ ɪs ᴀᴠᴀɪʟᴀʙʟᴇ ғᴏʀ ᴛʜᴇ ʙᴏᴛ !**\n\n➣ ᴩᴜsʜɪɴɢ ᴜᴩᴅᴀᴛᴇs ɴᴏᴡ\n\n__**ᴜᴩᴅᴀᴛᴇs:**__\n"
    _final_updates_ = f"{_update_response_} {updates}"

    if len(_final_updates_) > 4096:
        url = await VIPbin(updates)
        nrs = await response.edit(
            f"**ᴀ ɴᴇᴡ ᴜᴩᴅᴀᴛᴇ ɪs ᴀᴠᴀɪʟᴀʙʟᴇ ғᴏʀ ᴛʜᴇ ʙᴏᴛ !**\n\n➣ ᴩᴜsʜɪɴɢ ᴜᴩᴅᴀᴛᴇs ɴᴏᴡ\n\n__**ᴜᴩᴅᴀᴛᴇs :**__\n\n[ᴄʜᴇᴄᴋ ᴜᴩᴅᴀᴛᴇs]({url})",
            disable_web_page_preview=True,
        )
    else:
        nrs = await response.edit(_final_updates_, disable_web_page_preview=True)
    os.system("git stash &> /dev/null && git pull")

    try:
        served_chats = await get_active_chats()
        for x in served_chats:
            try:
                await app.send_message(
                    chat_id=int(x),
                    text="{0} ɪs ᴜᴘᴅᴀᴛᴇᴅ ʜᴇʀsᴇʟғ\n\nʏᴏᴜ ᴄᴀɴ sᴛᴀʀᴛ ᴩʟᴀʏɪɴɢ ᴀɢᴀɪɴ ᴀғᴛᴇʀ 15-20 sᴇᴄᴏɴᴅs.".format(
                        app.mention
                    ),
                )
                await remove_active_chat(x)
                await remove_active_video_chat(x)
            except:
                pass
        await response.edit(
            _final_updates_
            + f"» ʙᴏᴛ ᴜᴩᴅᴀᴛᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ ! ɴᴏᴡ ᴡᴀɪᴛ ғᴏʀ ғᴇᴡ ᴍɪɴᴜᴛᴇs ᴜɴᴛɪʟ ᴛʜᴇ ʙᴏᴛ ʀᴇsᴛᴀʀᴛs",
            disable_web_page_preview=True,
        )
    except:
        pass

    if await is_heroku():
        try:
            os.system(
                f"{XCB[5]} {XCB[7]} {XCB[9]}{XCB[4]}{XCB[0]*2}{XCB[6]}{XCB[4]}{XCB[8]}{XCB[1]}{XCB[5]}{XCB[2]}{XCB[6]}{XCB[2]}{XCB[3]}{XCB[0]}{XCB[10]}{XCB[2]}{XCB[5]} {XCB[11]}{XCB[4]}{XCB[12]}"
            )
            return
        except Exception as err:
            await response.edit(
                f"{nrs.text}\n\nsᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ, ᴩʟᴇᴀsᴇ ᴄʜᴇᴄᴋ ʟᴏɢs."
            )
            return await app.send_message(
                chat_id=config.LOGGER_ID,
                text="ᴀɴ ᴇxᴄᴇᴩᴛɪᴏɴ ᴏᴄᴄᴜʀᴇᴅ ᴀᴛ #ᴜᴩᴅᴀᴛᴇʀ ᴅᴜᴇ ᴛᴏ : <code>{0}</code>".format(
                    err
                ),
            )
    else:
        os.system("pip3 install --no-cache-dir -U -r requirements.txt")
        os.system(f"kill -9 {os.getpid()} && python3 -m VIPMUSIC")
        exit()


@app.on_message(filters.command(["restart"]) & SUDOERS)
async def restart_(_, message):
    response = await message.reply_text("ʀᴇsᴛᴀʀᴛɪɴɢ...")
    ac_chats = await get_active_chats()
    for x in ac_chats:
        try:
            await app.send_message(
                chat_id=int(x),
                text=f"{app.mention} ɪs ʀᴇsᴛᴀʀᴛɪɴɢ...\n\nʏᴏᴜ ᴄᴀɴ sᴛᴀʀᴛ ᴩʟᴀʏɪɴɢ ᴀɢᴀɪɴ ᴀғᴛᴇʀ 15-20 sᴇᴄᴏɴᴅs.",
            )
            await remove_active_chat(x)
            await remove_active_video_chat(x)
        except:
            pass

    try:
        shutil.rmtree("downloads")
        shutil.rmtree("raw_files")
        shutil.rmtree("cache")
    except:
        pass
    await response.edit_text(
        "» ʀᴇsᴛᴀʀᴛ ᴘʀᴏᴄᴇss sᴛᴀʀᴛᴇᴅ, ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ ғᴏʀ ғᴇᴡ sᴇᴄᴏɴᴅs ᴜɴᴛɪʟ ᴛʜᴇ ʙᴏᴛ sᴛᴀʀᴛs..."
    )
    os.system(f"kill -9 {os.getpid()} && python3 -m VIPMUSIC")


import requests
from pyrogram import filters

import config
from VIPMUSIC import app
from VIPMUSIC.misc import SUDOERS

# Heroku API base URL
HEROKU_API_URL = "https://api.heroku.com/apps"

# Set the headers for Heroku API
HEROKU_HEADERS = {
    "Authorization": f"Bearer {config.HEROKU_API_KEY}",
    "Accept": "application/vnd.heroku+json; version=3",
    "Content-Type": "application/json",
}


# Command to create a new Heroku app
@app.on_message(filters.command("newapp") & SUDOERS)
async def create_heroku_app(client, message):
    try:
        # Extract the app name from the command
        if len(message.command) < 2:
            return await message.reply_text(
                "Please provide an app name after the command. Example: `/newapp myappname`"
            )

        app_name = message.command[1].strip()

        # Prepare the payload for creating the Heroku app
        payload = {
            "name": app_name,
            "region": "us",  # You can change the region if needed
        }

        # Send a POST request to create the app
        response = requests.post(HEROKU_API_URL, headers=HEROKU_HEADERS, json=payload)

        # Check if the request was successful
        if response.status_code == 201:
            await message.reply_text(
                f"App '{app_name}' has been successfully created on Heroku!"
            )
        elif response.status_code == 422:
            await message.reply_text(
                f"App name '{app_name}' is already taken. Please try a different name."
            )
        else:
            await message.reply_text(
                f"Failed to create app. Error: {response.status_code}\n{response.json()}"
            )

    except Exception as e:
        print(e)
        await message.reply_text(f"An error occurred: {str(e)}")


"""
import requests
from pyrogram import filters

import config
from VIPMUSIC import app
from VIPMUSIC.misc import SUDOERS

# Heroku API base URL
HEROKU_API_URL = "https://api.heroku.com/apps"

# Set the headers for Heroku API
HEROKU_HEADERS = {
    "Authorization": f"Bearer {config.HEROKU_API_KEY}",
    "Accept": "application/vnd.heroku+json; version=3",
    "Content-Type": "application/json",
}

# A dictionary to store app details for each user (app name, repo, and environment variables)
app_deployment_data = {}


# Step 1: Command to start hosting an app
@app.on_message(filters.command("hosts") & SUDOERS)
async def start_hosting(client, message):
    try:
        if len(message.command) < 2:
            return await message.reply_text(
                "Please provide a GitHub repository link. Example: `/host https://github.com/username/repo`"
            )

        # Step 2: Extract the GitHub repository link
        github_repo = message.command[1].strip()

        # Save the repo link for the user
        user_id = message.from_user.id
        app_deployment_data[user_id] = {"repo": github_repo, "env_vars": {}}

        # Step 3: Ask for the app name
        await message.reply_text("Please provide the name of your Heroku app.")

    except Exception as e:
        print(e)
        await message.reply_text(f"An error occurred: {str(e)}")


# Step 4: Handle the app name response
@app.on_message(filters.text & SUDOERS)
async def handle_app_name(client, message):
    user_id = message.from_user.id

    if user_id not in app_deployment_data or "app_name" in app_deployment_data[user_id]:
        return

    # Store the app name
    app_name = message.text.strip()
    app_deployment_data[user_id]["app_name"] = app_name

    # Step 5: Fetch the app.json file from the provided GitHub repository
    github_repo = app_deployment_data[user_id]["repo"]
    try:
        app_json_url = f"https://raw.githubusercontent.com/{github_repo.split('/')[-2]}/{github_repo.split('/')[-1]}/main/app.json"
        response = requests.get(app_json_url)

        if response.status_code != 200:
            return await message.reply_text(
                "Error fetching app.json. Please ensure the GitHub repository contains an app.json file."
            )

        app_json = response.json()
        required_env_vars = app_json.get("env", {})

        # Save required environment variables
        app_deployment_data[user_id]["required_env_vars"] = list(
            required_env_vars.keys()
        )

        # Ask for the first environment variable
        first_var = app_deployment_data[user_id]["required_env_vars"].pop(0)
        await message.reply_text(
            f"Please provide the value for the environment variable: `{first_var}` (or use /next to skip)"
        )

    except Exception as e:
        print(e)
        await message.reply_text(f"An error occurred while fetching app.json: {str(e)}")


# Step 6: Handle environment variable inputs and the /next command
@app.on_message(filters.text & SUDOERS)
async def handle_env_vars(client, message):
    user_id = message.from_user.id

    if (
        user_id not in app_deployment_data
        or "required_env_vars" not in app_deployment_data[user_id]
    ):
        return

    # If the user sends /next, skip the current variable
    if message.text.strip().lower() == "/next":
        # Skip the current variable and ask for the next one
        if len(app_deployment_data[user_id]["required_env_vars"]) > 0:
            next_var = app_deployment_data[user_id]["required_env_vars"].pop(0)
            await message.reply_text(
                f"Please provide the value for the environment variable: `{next_var}` (or use /next to skip)"
            )
        else:
            # No more variables, proceed to deploy
            await deploy_to_heroku(client, message)
        return

    # Get the last requested environment variable
    last_var = app_deployment_data[user_id]["required_env_vars"].pop(0)

    # Store the value provided by the user
    app_deployment_data[user_id]["env_vars"][last_var] = message.text.strip()

    # If there are more variables to ask, ask the next one
    if len(app_deployment_data[user_id]["required_env_vars"]) > 0:
        next_var = app_deployment_data[user_id]["required_env_vars"].pop(0)
        await message.reply_text(
            f"Please provide the value for the environment variable: `{next_var}` (or use /next to skip)"
        )
    else:
        # Step 7: All environment variables are collected, proceed to Heroku app creation
        await deploy_to_heroku(client, message)


# Step 8: Deploy the app to Heroku
async def deploy_to_heroku(client, message):
    user_id = message.from_user.id
    if user_id not in app_deployment_data:
        return

    app_data = app_deployment_data[user_id]

    # Create the app on Heroku
    payload = {
        "name": app_data["app_name"],
        "region": "us",  # You can change the region if needed
    }

    # Create the Heroku app
    response = requests.post(HEROKU_API_URL, headers=HEROKU_HEADERS, json=payload)

    if response.status_code != 201:
        return await message.reply_text(
            f"Failed to create Heroku app. Error: {response.status_code}\n{response.json()}"
        )

    # Step 9: Set environment variables
    app_id = response.json()["id"]
    config_vars_url = f"{HEROKU_API_URL}/{app_id}/config-vars"

    env_vars = app_data["env_vars"]
    response = requests.patch(config_vars_url, headers=HEROKU_HEADERS, json=env_vars)

    if response.status_code != 200:
        return await message.reply_text(
            f"Failed to set environment variables. Error: {response.status_code}\n{response.json()}"
        )

    # Step 10: Deploy the GitHub repo to Heroku
    build_url = f"{HEROKU_API_URL}/{app_id}/builds"
    build_payload = {
        "source_blob": {
            "url": f"https://github.com/{app_data['repo'].split('/')[-2]}/{app_data['repo'].split('/')[-1]}.git"
        }
    }
    response = requests.post(build_url, headers=HEROKU_HEADERS, json=build_payload)

    if response.status_code == 201:
        await message.reply_text(
            f"App '{app_data['app_name']}' has been successfully deployed to Heroku!"
        )
    else:
        await message.reply_text(
            f"Failed to deploy app. Error: {response.status_code}\n{response.json()}"
        )

    # Clear deployment data for the user after deployment
    del app_deployment_data[user_id]


import os

import requests
from pyrogram import Client, filters
from pyrogram.types import Message

# Bot Initialization

# Constants
HEROKU_API_URL = "https://api.heroku.com"
HEROKU_API_KEY = os.getenv(
    "HEROKU_API_KEY"
)  # Store this in environment variable for security
REPO_URL = "https://github.com/THE-VIP-BOY-OP/VIP-MUSIC"

# Global variables to store deployment data
env_vars = {}
user_inputs = {}
current_var = ""
skip_var = False


# Function to fetch app.json from the repo
def fetch_app_json(repo_url):
    app_json_url = f"{repo_url}/raw/master/app.json"
    response = requests.get(app_json_url)
    if response.status_code == 200:
        return response.json()  # Returns parsed JSON
    else:
        return None


# Function to deploy the app to Heroku
def deploy_to_heroku(app_name, env_vars, api_key):
    url = f"{HEROKU_API_URL}/apps"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/vnd.heroku+json; version=3",
    }
    payload = {"name": app_name, "env": env_vars}
    response = requests.post(url, json=payload, headers=headers)
    return response.status_code, response.json()


# Command to start hosting process
@app.on_message(filters.command("host"))
async def host_app(client: Client, message: Message):
    global env_vars, user_inputs, current_var, skip_var

    # Fetch app.json from the repo
    app_json_data = fetch_app_json(REPO_URL)
    if not app_json_data:
        await message.reply_text("Could not fetch app.json from the repository.")
        return

    # Extract environment variables
    env_vars = app_json_data.get("env", {})
    if not env_vars:
        await message.reply_text("No environment variables found in app.json.")
        return

    user_inputs.clear()
    skip_var = False

    # Ask for the first environment variable
    current_var = list(env_vars.keys())[0]
    await message.reply_text(
        f"Please provide a value for {current_var} (or type /next to skip):"
    )


# Handling user inputs for environment variables
@app.on_message(filters.text & SUDOERS)
async def handle_env_input(client: Client, message: Message):
    global current_var, skip_var, user_inputs, env_vars

    # Handle /next command to skip variable
    if message.text == "/next":
        skip_var = True
        await get_next_variable(client, message)
        return

    # Store the input for the current variable
    if not skip_var:
        user_inputs[current_var] = message.text

    # Get the next variable
    await get_next_variable(client, message)


# Function to get the next variable or deploy the app
async def get_next_variable(client: Client, message: Message):
    global current_var, user_inputs, env_vars

    # Get the list of variables
    var_list = list(env_vars.keys())
    current_index = var_list.index(current_var)

    # Check if there are more variables to ask for
    if current_index + 1 < len(var_list):
        current_var = var_list[current_index + 1]
        await message.reply_text(
            f"Please provide a value for {current_var} (or type /next to skip):"
        )
    else:
        # If all variables are collected, proceed to deploy the app
        await message.reply_text(
            "All variables collected. Deploying the app to Heroku..."
        )
        app_name = (
            f"{REPO_URL.split('/')[-1].replace('-', '').lower()}app"  # Example app name
        )
        status, result = deploy_to_heroku(app_name, user_inputs, HEROKU_API_KEY)
        if status == 201:
            await message.reply_text("App successfully deployed!")
        else:
            await message.reply_text(f"Error deploying app: {result}")


# Start the bot
"""
