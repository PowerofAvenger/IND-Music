


from asyncio import QueueEmpty

from pyrogram import Client, filters
from pyrogram.types import Message

from IndMusic.function.admins import set
from IndMusic.helpers.decorators import authorized_users_only, errors
from IndMusic.services.callsmusic import callsmusic
from IndMusic.services.queues import queues
from IndMusic.config import que


@Client.on_message(
    filters.command(["channelpause", "cpause"]) & filters.group & ~filters.edited
)
@errors
@authorized_users_only
async def pause(_, message: Message):
    try:
        conchat = await _.get_chat(message.chat.id)
        conid = conchat.linked_chat.id
        chid = conid
    except:
        await message.reply("Is chat even linked")
        return
    chat_id = chid
    (
        await message.reply_text("▶️ Paused!")
    ) if (
        callsmusic.pause(chat_id)
    ) else (
        await message.reply_text("❗ Nothing is playing!")
    )


@Client.on_message(
    filters.command(["channelresume", "cresume"]) & filters.group & ~filters.edited
)
@errors
@authorized_users_only
async def resume(_, message: Message):
    try:
        conchat = await _.get_chat(message.chat.id)
        conid = conchat.linked_chat.id
        chid = conid
    except:
        await message.reply("Is chat even linked")
        return
    chat_id = chid
    (
       await message.reply_text("⏸ Resumed!")
    ) if (
        callsmusic.resume(chat_id)
    ) else (
        await message.reply_text("❗ Nothing is paused!")
    )
        
    

@Client.on_message(
    filters.command(["channelend", "cend"]) & filters.group & ~filters.edited
)
@errors
@authorized_users_only
async def stop(_, message: Message):
    try:
        conchat = await _.get_chat(message.chat.id)
        conid = conchat.linked_chat.id
        chid = conid
    except:
        await message.reply("Is chat even linked")
        return
    chat_id = chid
    if chat_id not in callsmusic.active_chats:
        await message.reply_text("❗ Nothing is streaming!")
    else:
        try:
            queues.clear(chat_id)
        except QueueEmpty:
            pass

        await callsmusic.stop(chat_id)
        await message.reply_text("❌ Stopped streaming!")


@Client.on_message(
    filters.command(["channelskip", "cskip"]) & filters.group & ~filters.edited
)
@errors
@authorized_users_only
async def skip(_, message: Message):
    global que
    try:
        conchat = await _.get_chat(message.chat.id)
        conid = conchat.linked_chat.id
        chid = conid
    except:
        await message.reply("Is chat even linked")
        return
    chat_id = chid
    if chat_id not in callsmusic.active_chats:
        await message.reply_text("❗ Nothing is playing to skip!")
    else:
        queues.task_done(chat_id)

        if queues.is_empty(chat_id):
            await callsmusic.stop(chat_id)
        else:
            await callsmusic.set_stream(chat_id, queues.get(chat_id)["file"])

    qeue = que.get(chat_id)
    if qeue:
        skip = qeue.pop(0)
    if not qeue:
        return
    await message.reply_text(f"- Skipped **{skip[0]}**\n- Now Playing **{qeue[0][0]}**")
    
    
@Client.on_message(
    filters.command(["channelmute", "cmute"]) & filters.group & ~filters.edited
)
@errors
@authorized_users_only
async def mute(_, message: Message):
    global que
    try:
        conchat = await _.get_chat(message.chat.id)
        conid = conchat.linked_chat.id
        chid = conid
    except:
        await message.reply("Is chat even linked")
        return 
    chat_id = chid
    result = await callsmusic.mute(chat_id)
    (
        await message.reply_text("✅ Muted")
    ) if (
        result == 0
    ) else (
        await message.reply_text("❌ Already muted")
    ) if (
        result == 1
    ) else (
        await message.reply_text("❌ Not in call")
    )
        
        
@Client.on_message(
    filters.command(["channelunmute", "cunmute"]) & filters.group & ~filters.edited
)
@errors
@authorized_users_only
async def unmute(_, message: Message):
    global que
    try:
        conchat = await _.get_chat(message.chat.id)
        conid = conchat.linked_chat.id
        chid = conid
    except:
        await message.reply("Is chat even linked")
        return 
    chat_id = chid
    result = await callsmusic.unmute(chat_id)
    (
        await message.reply_text("✅ Unmuted")
    ) if (
        result == 0
    ) else (
        await message.reply_text("❌ Not muted")
    ) if (
        result == 1
    ) else (
        await message.reply_text("❌ Not in call")
    )


@Client.on_message(filters.command("channeladmincache"))
@errors
async def admincache(client, message: Message):
    try:
        conchat = await client.get_chat(message.chat.id)
        conid = conchat.linked_chat.id
        chid = conid
    except:
        await message.reply("Is chat even linked")
        return
    set(
        chid,
        [
            member.user
            for member in await conchat.linked_chat.get_members(filter="administrators")
        ],
    )
    await message.reply_text("❇️ Admin cache refreshed!")
