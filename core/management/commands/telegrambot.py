from random import randint

from django.core.management import BaseCommand
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import CallbackQueryHandler, MessageHandler, BaseFilter, Filters
from telegram.ext import Updater, CommandHandler
import logging
from bot import settings
from core.models import Service, User, UserActivity

updater = Updater(settings.bot, use_context=True)
dispatcher = updater.dispatcher

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


def user_handler(telegram_id, telegram_username, action):
    user = User.objects.get_or_create(telegram_id=telegram_id, username=telegram_username)
    if user[1] is False:
        u_a = UserActivity.objects.filter(user__username=user[0].username)
        u_a.update(action=action)

    UserActivity.objects.create(user=user[0], action=action)


def start(update, context):
    update.message.reply_text(
        text="سلام🧑🏻‍⚕️👩🏻‍⚕️ \n به ربات کلینیک زیبایی نای ذی خوش آمدید",
        reply_markup=ReplyKeyboardMarkup([['آدرس', 'شماره تماس'], ['اینستاگرام', 'وب سایت'], ['خدمات']],
                                         one_time_keyboard=True)
    )

    user_handler(update.message.chat.id, update.message.chat.username, action='start')


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


def inline_query(update, context):
    # user = User.objects.get(telegram_id=update.callback_query.message.chat.id)
    if 'service__' in update.callback_query.data:
        service_id = update.callback_query.data.split('__')[1]
        service = Service.objects.get(pk=service_id)
        # update.callback_query.message.reply_text()
        service_sticker_count = len(service.images.all())

        # update.callback_query.answer()
        update_question(service.title, update.callback_query)
        # create_question_layout(service.title, update)

        for i in service.images.all():
            context.bot.send_sticker(chat_id=update.effective_chat.id, sticker=i.image)

        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="عکس هایی تو این زاویه که فرستادیم برات از خودت بگیر و همینجا بفرس برامون")


def address(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="بلوار آفریقا - خیابان شریفی - پ19 - ط2")
    context.bot.send_location(chat_id=update.effective_chat.id, latitude=35.759400, longitude=51.412237)
    user_handler(update.message.chat.id, update.message.chat.username, action='get_contact_us')


def instagram(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="https://instagram.com/nayziclinic")
    user_handler(update.message.chat.id, update.message.chat.username, action='get_contact_us')


def website(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="https://nayziclinic.com")
    user_handler(update.message.chat.id, update.message.chat.username, action='get_contact_us')


def contact_us(update, context):
    context.bot.send_contact(chat_id=update.effective_chat.id, first_name='کلینیک زیبایی نای ذی',
                             phone_number=+982191001919)
    user_handler(update.message.chat.id, update.message.chat.username, action='get_contact_us')


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


def reply_photo_to_stickers(update, context):
    if update.message.photo:
        new_file = context.bot.get_file(update.message.photo[-1].file_id)
        rand = randint(0, 99999999)

        new_file.download('user_reply_to_stickers_' + str(update.effective_chat.id) + '_' + str(rand) + '.jpg')
        context.bot.send_message(chat_id=update.effective_chat.id, text="https://nayziclinic.com")


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

        dispatcher.add_handler(MessageHandler(Filters.photo, reply_photo_to_stickers))

        updater.start_polling()
        updater.idle()
