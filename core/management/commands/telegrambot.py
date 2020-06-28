from django.core.management import BaseCommand
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import CallbackQueryHandler, MessageHandler, BaseFilter
from telegram.ext import Updater, CommandHandler
import logging
from bot import settings
from core.models import Service

updater = Updater(settings.bot, use_context=True)
dispatcher = updater.dispatcher

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


def start(update, context):
    update.message.reply_text(
        text="سلام🧑🏻‍⚕️👩🏻‍⚕️ \n به ربات کلینیک زیبایی نای ذی خوش آمدید",
        reply_markup=ReplyKeyboardMarkup([['آدرس', 'شماره تماس'], ['اینستاگرام', 'وب سایت'], ['خدمات']],
                                         one_time_keyboard=True)
    )


def create_question_layout(response, update):
    questions = response
    if len(questions):
        for q in questions:
            inline_keyboard = [[]]
            for option in q["options"]:
                inline_keyboard[0].append(
                    InlineKeyboardButton(option["title"], callback_data=str(q['_id']) + '_' + str(option['_id'])))
            inline_keyboard = InlineKeyboardMarkup(inline_keyboard)
            if update.message:
                update.message.reply_text(q["title"], reply_markup=inline_keyboard)
            else:
                update.callback_query.message.reply_text(q["title"], reply_markup=inline_keyboard)


def update_question(response, query):
    keyboard = [
        [InlineKeyboardButton("خدمت انتخاب شده شما: {}".format(response),
                              callback_data="ALREADY_ANSWERED")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text=query.message.text,
        reply_markup=reply_markup
    )


def inline_query(update, _):
    # user = User.objects.get(telegram_id=update.callback_query.message.chat.id)
    if 'service__' in update.callback_query.data:
        service_id = update.callback_query.data.split('__')[1]
        service = Service.objects.get(pk=service_id)
        update.callback_query.message.reply_text('👍🏿')

        # update.callback_query.answer()
        update_question(service.title, update.callback_query)
        # create_question_layout(service.title, update)


def address(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="بلوار آفریقا - خیابان شریفی - پ19 - ط2")
    context.bot.send_location(chat_id=update.effective_chat.id, latitude=35.759400, longitude=51.412237)


def instagram(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="https://instagram.com/nayziclinic")


def website(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="https://nayziclinic.com")


def contact_us(update, context):
    context.bot.send_contact(chat_id=update.effective_chat.id, first_name='کلینیک زیبایی نای ذی',
                             phone_number=+982191001919)


# def button(update, context):
#     keyboard = [[InlineKeyboardButton("Option 1", callback_data='1'),
#                  InlineKeyboardButton("Option 2", callback_data='2')],
#
#                 [InlineKeyboardButton("Option 3", callback_data='3')]]
#     reply_markup = InlineKeyboardMarkup(keyboard)
#     update.message.reply_text('Please choose:', reply_markup=reply_markup)


def service(update, _):
    # user = User.objects.get(telegram_id=update.message.chat.id)
    batch_size = 2
    services = Service.objects.all()

    chunks = [services[i:i + batch_size] for i in range(0, len(services), batch_size)]

    keyboard = []
    for services in chunks:
        row = []
        for service in services:
            row.append(InlineKeyboardButton(service.title, callback_data='service__' + str(service.id)))
        keyboard.append(row)

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(text='خدماتی که می خوای رو انتخاب کن:', reply_markup=reply_markup)
    # UserActivity.objects.log_user_select_popular_stories(user=user)


class AddressFilter(BaseFilter):
    def filter(self, message):
        return 'آدرس' == message.text


class InstagramFilter(BaseFilter):
    def filter(self, message):
        return 'اینستاگرام' == message.text


class ContactUsFilter(BaseFilter):
    def filter(self, message):
        return 'شماره تماس' == message.text


class WebsiteFilter(BaseFilter):
    def filter(self, message):
        return 'وب سایت' == message.text


class ServiceFilter(BaseFilter):
    def filter(self, message):
        return 'خدمات' == message.text


class Command(BaseCommand):
    def handle(self, *args, **options):
        start_handler = CommandHandler('start', start)
        dispatcher.add_handler(start_handler)

        dispatcher.add_handler(CallbackQueryHandler(inline_query))

        address_handler_text = MessageHandler(AddressFilter(), address)
        dispatcher.add_handler(address_handler_text)
        instagram_handler_text = MessageHandler(InstagramFilter(), instagram)
        dispatcher.add_handler(instagram_handler_text)
        contact_us_handler_text = MessageHandler(ContactUsFilter(), contact_us)
        dispatcher.add_handler(contact_us_handler_text)
        website_handler_text = MessageHandler(WebsiteFilter(), website)
        dispatcher.add_handler(website_handler_text)
        service_handler_text = MessageHandler(ServiceFilter(), service)
        dispatcher.add_handler(service_handler_text)

        updater.start_polling()
        updater.idle()
