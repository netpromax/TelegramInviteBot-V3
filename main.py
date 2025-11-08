import telegram
import random
import time
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram import constants # لاستخدام constants.ParseMode

# 🛑 1. ضـع تـوكن البـوت الـذي حـصـلـت عـلـيـه مـن @BotFather (بـيـن عـلامـات الـتـنـصـيـص)
TOKEN = "8270551515:AAEKbkQRterrwBEkoawJd9Oesh1UIrbrQdY"

# 🛑 2. ضـع مـعـرّف مـجـمـوعـتـك الـسـالـب هـنـا (يـجـب أن يـبـدأ بـعـلامـة -)
GROUP_ID = -1003203601185

# قاعدة بيانات بسيطة لتخزين الإجابة الصحيحة لكل مستخدم
user_answers = {} 

# تم تعريف الدوال كـ async
async def start(update, context):
    """الرد على أمر /start بطلب حل المعادلة."""
    user_id = update.message.from_user.id
    
    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)
    correct_answer = num1 + num2
    
    user_answers[user_id] = correct_answer
    
    equation_message = (
        "🔒 Solve to get invites:\n"
        f"**{num1} + {num2} = ?**\n"
        "Send your answer as a number."
    )
    # استخدام await
    await update.message.reply_text(equation_message, parse_mode=constants.ParseMode.MARKDOWN)

# تم تعريف الدوال كـ async
async def handle_message(update, context):
    """معالجة رسالة المستخدم للتحقق من الإجابة."""
    user_id = update.message.from_user.id
    user_text = update.message.text.strip()
    
    if user_id in user_answers:
        try:
            user_answer = int(user_text)
        except ValueError:
            await update.message.reply_text("❌ Please reply with the **number** of the answer only.", parse_mode=constants.ParseMode.MARKDOWN)
            return 
        
        if user_answer == user_answers[user_id]:
            await update.message.reply_text("✅ **Correct**—fetching the temporary link...", 
                                      parse_mode=constants.ParseMode.MARKDOWN)
            
            del user_answers[user_id] 
            
            # استدعاء دالة async
            await create_invite_link(update, context)
            
        else:
            await update.message.reply_text("❌ Incorrect answer. Please use **/start** again to get a new equation.", parse_mode=constants.ParseMode.MARKDOWN)
            del user_answers[user_id] 
    
# تم تعريف الدوال كـ async
async def create_invite_link(update, context):
    """استخدام Telegram API لتوليد رابط دعوة مؤقت (10 ثوان)."""
    
    expire_time = int(time.time()) + 10 
    
    try:
        # استخدام await
        invite_link_object = await context.bot.create_chat_invite_link(
            chat_id=GROUP_ID,
            expire_date=expire_time,
            member_limit=1
        )
        
        link = invite_link_object.invite_link
        
        response_message = (
            "✉️ Your link **(valid for 10s only!)**:\n"
            f"👉 **{link}**\n\n"
            "Use **/start** again if the link expires."
        )
        # استخدام await
        await update.message.reply_text(response_message, 
                                  parse_mode=constants.ParseMode.MARKDOWN, 
                                  disable_web_page_preview=True)

    except telegram.error.TelegramError as e:
        # 🛑 تم تصحيح تنسيق الماركداون هنا لتجنب خطأ "Can't parse entities" 
        await update.message.reply_text(f"🚫 Error: The bot must be an Admin in the group with Invite Users permission. Error details: {e}")


def main():
    """تشغيل البوت باستخدام الواجهة الجديدة (Application)."""
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    application.run_polling()


if __name__ == '__main__':
    main()