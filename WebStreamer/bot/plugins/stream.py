import asyncio
import urllib.parse
from WebStreamer.bot import StreamBot
from WebStreamer.utils.database import Database
from WebStreamer.utils.human_readable import humanbytes
from WebStreamer.vars import Var
from pyrogram import filters, Client
from pyrogram.errors import FloodWait, UserNotParticipant
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
db = Database(Var.DATABASE_URL, Var.SESSION_NAME)


def get_media_file_size(m):
    media = m.video or m.audio or m.document
    if media and media.file_size:
        return media.file_size
    else:
        return None


def get_media_file_name(m):
    media = m.video or m.document or m.audio
    if media and media.file_name:
        return urllib.parse.quote_plus(media.file_name)
    else:
        return None


@StreamBot.on_message(filters.private & (filters.document | filters.video | filters.audio) & ~filters.edited, group=4)
async def private_receive_handler(c: Client, m: Message):
    if not await db.is_user_exist(m.from_user.id):
        await db.add_user(m.from_user.id)
        await c.send_message(
            Var.BIN_CHANNEL,
            f"#NEW_USER: \n\nNew User [{m.from_user.first_name}](tg://user?id={m.from_user.id}) Started !!"
        )
    if Var.UPDATES_CHANNEL != "None":
        try:
            user = await c.get_chat_member(Var.UPDATES_CHANNEL, m.chat.id)
            if user.status == "kicked":
                await c.send_message(
                    chat_id=m.chat.id,
                    text="**ππΎπ π°ππ΄ π±π°π½π½π΄π³../**",
                    parse_mode="markdown",
                    disable_web_page_preview=True
                )
                return
        except UserNotParticipant:
            await c.send_message(
                chat_id=m.chat.id,
                text="**πΉπΎπΈπ½ πΌπ ππΏπ³π°ππ΄π π²π·π°π½π½π΄π» ππΎ πππ΄ πΌπ΄..**\n\n**π³ππ΄ ππΎ πΎππ΄ππ»πΎπ°π³ πΎπ½π»π π²π·π°π½π½π΄π» πππ±ππ²ππΈπ±π΄ππ π²π°π½ πππ΄ ππ·πΈπ π±πΎπ..!**",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton("πΉπΎπΈπ½ ππΏπ³π°ππ΄π π²π·π°π½π½π΄π»", url=f"https://t.me/{Var.UPDATES_CHANNEL}")
                        ]
                    ]
                ),
                parse_mode="markdown"
            )
            return
        except Exception:
            await c.send_message(
                chat_id=m.chat.id,
                text="**π°π³π³ π΅πΎππ²π΄ πππ± ππΎ π°π½π π²π·π°π½π½π΄π»**",
                parse_mode="markdown",
                disable_web_page_preview=True)
            return
    try:
        log_msg = await m.forward(chat_id=Var.BIN_CHANNEL)
        file_name = get_media_file_name(m)
        file_size = humanbytes(get_media_file_size(m))
        stream_link = "https://{}/{}/{}".format(Var.FQDN, log_msg.message_id, file_name) if Var.ON_HEROKU or Var.NO_PORT else \
            "http://{}:{}/{}/{}".format(Var.FQDN,
                                    Var.PORT,
                                    log_msg.message_id,
                                    file_name)

        msg_text = "<b>ππΎππ π»πΈπ½πΊ πΈπ πΆπ΄π½π΄ππ°ππ΄π³...β‘\n\nπ§ π΅πΈπ»π΄ π½π°πΌπ΄ :- \n{}\n {}\n\nπ π³πΎππ½π»πΎπ°π³ π»πΈπ½πΊ :- {}\n\nβ»οΈ ππ·πΈπ π»πΈπ½πΊ πΈπ πΏπ΄ππΌπ°π½π΄π½π π°π½π³ ππΈπ»π» π½πΎπ π΄ππΏπΈππ΄ β»οΈ\n\n@OpusTechz</b>"
        await log_msg.reply_text(text=f"ππ΄πππ΄πππ΄π³ π±π [{m.from_user.first_name}](tg://user?id={m.from_user.id})\n**πππ΄π πΈπ³ :-** `{m.from_user.id}`\n**π³πΎππ½π»πΎπ°π³ π»πΈπ½πΊ :- ** {stream_link}\n\n@OpusTechz", disable_web_page_preview=True, parse_mode="Markdown", quote=True)
        await m.reply_text(
            text=msg_text.format(file_name, file_size, stream_link),
            parse_mode="HTML", 
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("β‘ π³πΎππ½π»πΎπ°π³ π½πΎπ β‘", url=stream_link)]]),
            quote=True
        )
    except FloodWait as e:
        print(f"Sleeping for {str(e.x)}s")
        await asyncio.sleep(e.x)
        await c.send_message(chat_id=Var.BIN_CHANNEL, text=f"Gα΄α΄ FΚα΄α΄α΄Wα΄Ιͺα΄ α΄? {str(e.x)}s from [{m.from_user.first_name}](tg://user?id={m.from_user.id})\n\n**ππππ πΈπ³ :** `{str(m.from_user.id)}`", disable_web_page_preview=True, parse_mode="Markdown")


@StreamBot.on_message(filters.channel & (filters.document | filters.video) & ~filters.edited, group=-1)
async def channel_receive_handler(bot, broadcast):
    if int(broadcast.chat.id) in Var.BANNED_CHANNELS:
        await bot.leave_chat(broadcast.chat.id)
        return
    try:
        log_msg = await broadcast.forward(chat_id=Var.BIN_CHANNEL)
        stream_link = "https://{}/{}".format(Var.FQDN, log_msg.message_id) if Var.ON_HEROKU or Var.NO_PORT else \
            "http://{}:{}/{}".format(Var.FQDN,
                                    Var.PORT,
                                    log_msg.message_id)
        await log_msg.reply_text(
            text=f"**π²π·π°π½π½π΄π» π½π°πΌπ΄ :** `{broadcast.chat.title}`\n**π²π·π°π½π½π΄π» πΈπ³ :** `{broadcast.chat.id}`\n**π΅πΈπ»π΄ πππ» :** https://t.me/{(await bot.get_me()).username}?start=OpusTechz_{str(log_msg.message_id)}",
            # text=f"**π²π·π°π½π½π΄π» π½π°πΌπ΄ :** `{broadcast.chat.title}`\n**π²π·π°π½π½π΄π» πΈπ³ :** `{broadcast.chat.id}`\n**π΅πΈπ»π΄ πππ» :** https://t.me/OPFileToLinkBot?start=OpusTechz_{str(log_msg.message_id)}",
            quote=True,
            parse_mode="Markdown"
        )
        await bot.edit_message_reply_markup(
            chat_id=broadcast.chat.id,
            message_id=broadcast.message_id,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("π³πΎππ½π»πΎπ°π³ π»πΈπ½πΊ", url=f"https://t.me/{(await bot.get_me()).username}?start=OpusTechz_{str(log_msg.message_id)}")]])
            # [[InlineKeyboardButton("π³πΎππ½π»πΎπ°π³ π»πΈπ½πΊ", url=f"https://t.me/OPFileToLinkBot?start=OpusTechz_{str(log_msg.message_id)}")]])
        )
    except FloodWait as w:
        print(f"Sleeping for {str(w.x)}s")
        await asyncio.sleep(w.x)
        await bot.send_message(chat_id=Var.BIN_CHANNEL,
                             text=f"Gα΄α΄ FΚα΄α΄α΄Wα΄Ιͺα΄ α΄? {str(w.x)}s from {broadcast.chat.title}\n\n**CΚα΄Ι΄Ι΄α΄Κ ID:** `{str(broadcast.chat.id)}`",
                             disable_web_page_preview=True, parse_mode="Markdown")
    except Exception as e:
        await bot.send_message(chat_id=Var.BIN_CHANNEL, text=f"**#α΄ΚΚα΄Κ_α΄Κα΄α΄α΄Κα΄α΄α΄:** `{e}`", disable_web_page_preview=True, parse_mode="Markdown")
        print(f"Cα΄Ι΄'α΄ Eα΄Ιͺα΄ BΚα΄α΄α΄α΄α΄sα΄ Mα΄ssα΄Ι’α΄!\nEΚΚα΄Κ: {e}")



#@OpusTechz
