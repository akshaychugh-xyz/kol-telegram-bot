from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext, MessageHandler, filters, ConversationHandler
import sqlite3
import logging

TOKEN = '7500505731:AAEzQeCQK8iqFYW7V1wXTIavfrhtyUrZh4A'
GROUP_CHAT_ID = '-1002222871824'  # Replace with actual group chat ID

# Define conversation states
EMAIL = range(1)

# Database helper functions
def get_db_connection():
    return sqlite3.connect('your_database.db')

def check_email(email):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT referral_code FROM users WHERE email=?", (email,))
        return cursor.fetchone() is not None

def check_deposit(email):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT deposited FROM users WHERE email=? AND deposited=1", (email,))
        result = cursor.fetchone()
        logging.info(f"Deposit check for {email}: {'Verified' if result else 'Not verified'}")
        return result is not None

async def start(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Welcome! Please enter your email ID:")
    return EMAIL

async def verify_email(update: Update, context: CallbackContext) -> int:
    email = update.message.text
    if check_email(email):
        context.user_data['email'] = email
        await update.message.reply_text("Email verified! Now checking your deposit status...")
        # Immediately check deposit status
        return await check_deposit_status(update, context)
    else:
        await update.message.reply_text("Email not found or not affiliated with a referral code. Please try again.")
        return EMAIL

async def check_deposit_status(update: Update, context: CallbackContext) -> int:
    email = context.user_data['email']
    logging.info(f"Checking deposit status for email: {email}")
    if check_deposit(email):
        await update.message.reply_text("Deposit verified! Generating your invitation link...")
        await send_invite_link(update, context)
        return ConversationHandler.END
    else:
        await update.message.reply_text("You have not deposited $100. Please complete the deposit and try again.")
        return ConversationHandler.END

async def send_invite_link(update: Update, context: CallbackContext) -> None:
    try:
        logging.info(f"Attempting to access chat with ID: {GROUP_CHAT_ID}")
        chat = await context.bot.get_chat(GROUP_CHAT_ID)
        logging.info(f"Successfully accessed chat: {chat.title}")
        invite_link = await chat.create_invite_link(member_limit=1)
        await update.message.reply_text(f"Here is your one-time link to join the group: {invite_link.invite_link}")
    except Exception as e:
        await update.message.reply_text("An error occurred while generating the invite link. Please try again later.")
        logging.error(f"Error creating invite link: {e}")
        if isinstance(e, telegram.error.BadRequest):
            logging.error(f"BadRequest details: {e.message}")

async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Operation cancelled. Type /start to begin again.")
    return ConversationHandler.END

async def verify_group_access(application: Application) -> None:
    try:
        chat = await application.bot.get_chat(GROUP_CHAT_ID)
        logging.info(f"Successfully accessed group: {chat.title}")
        await chat.send_message("Bot is operational and has access to this group.")
    except Exception as e:
        logging.error(f"Failed to access group chat: {e}")
        if isinstance(e, telegram.error.BadRequest):
            logging.error(f"BadRequest details: {e.message}")

def main() -> None:
    application = Application.builder().token(TOKEN).build()

    # Add this line to verify group access on startup
    application.job_queue.run_once(verify_group_access, when=1)

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, verify_email)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(conv_handler)

    application.run_polling()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()