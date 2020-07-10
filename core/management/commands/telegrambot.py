from django.core.management import BaseCommand
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CallbackQueryHandler, MessageHandler, BaseFilter, Filters
from telegram.ext import Updater, CommandHandler
import logging
from bot import settings
from core.models import Service, User, UserActivity, UserService, UserServiceImage

updater = Updater(settings.bot, use_context=True)
dispatcher = updater.dispatcher

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

KEYBOARD_MARKUPS = {
    'MENU': [['آدرس', 'شماره تماس'], ['اینستاگرام', 'وب سایت'], ['خدمات']],
    'COMPLETED': [['تمام شد']],
    'NEXT': [['بعدی']],
}


def user_handler(telegram_id, telegram_username, action):
    user = User.objects.get_or_create(telegram_id=telegram_id, username=telegram_username)
    if user[1] is False:
        u_a = UserActivity.objects.filter(user__username=user[0].username)
        u_a.update(action=action)

    UserActivity.objects.create(user=user[0], action=action)


def start(update, context):
    update.message.reply_text(
        text="سلام🧑🏻‍⚕️👩🏻‍⚕️ \n به ربات کلینیک زیبایی نای ذی خوش آمدید",
        reply_markup=ReplyKeyboardMarkup(KEYBOARD_MARKUPS['MENU'],
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


def get_contact_user(update, context):
    user = User.objects.filter(telegram_id=update.message.chat.id)
    u = User.objects.get(telegram_id=update.message.chat.id)
    if u.name is None:
        def get_name_user():
            user.update(
                name=update.message.chat.first_name if not None else '' + update.message.chat.last_name if not None else '')
            update.message.reply_text(text="کارشناسان ما بزودی با شما تماس خواهند گرفت",
                                      reply_markup=ReplyKeyboardMarkup(KEYBOARD_MARKUPS['MENU'],
                                                                       one_time_keyboard=True))

        def get_city_user(update, context):
            user.update(city=update.message.text)
            context.bot.send_message(chat_id=update.effective_chat.id, text="شهر شما ثبت شد")
            get_name_user()

        def get_age_user(update, context):
            user.update(age=update.message.text)
            context.bot.send_message(chat_id=update.effective_chat.id, text="سن شما ثبت شد")
            context.bot.send_message(chat_id=update.effective_chat.id, text="لطفا شهر خود را ارسال کنید")
            dispatcher.add_handler(MessageHandler(Filters.text, get_city_user))

        def get_mobile_number(update, context):
            user.update(mobile=update.message.text)
            context.bot.send_message(chat_id=update.effective_chat.id, text="شماره شما ثبت شد")
            context.bot.send_message(chat_id=update.effective_chat.id, text="لطفا سن خود را ارسال کنید")
            dispatcher.add_handler(MessageHandler(Filters.regex('^[1-9][0-9]{1}$'), get_age_user))

        context.bot.send_message(chat_id=update.effective_chat.id, text="لطفا شماره خود را با 09 ارسال کنید")
        dispatcher.add_handler(MessageHandler(Filters.regex('^09[0-9]{9}$'), get_mobile_number))
    else:
        update.message.reply_text(text="کارشناسان ما بزودی با شما تماس خواهند گرفت",
                                  reply_markup=ReplyKeyboardMarkup(KEYBOARD_MARKUPS['MENU'],
                                                                   one_time_keyboard=True))


def user_request_service(update, context, user, service, service_sticker_count):
    def reply_photo_to_stickers(update, context):
        if update.message.photo:
            user_service = UserService.objects.get(user=user, services=service)

            new_file = context.bot.get_file(update.message.photo[-1].file_id)
            i = new_file.download('medias/user_service_image/' + str(update.effective_chat.id) + '.jpg')
            img = UserServiceImage.objects.create(image=i.split('medias/')[1])
            user_service.images.add(img)

            user_service = UserService.objects.get(user=user, services=service)
            user_service_image_count = len(user_service.images.all())
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="عکس شما دریافت شد. لطفا روی دکمه بزنید",
                                     reply_markup=ReplyKeyboardMarkup(KEYBOARD_MARKUPS[
                                                                          'COMPLETED' if user_service_image_count == service_sticker_count else 'NEXT'],
                                                                      one_time_keyboard=True)
                                     )

    def send_stickers():
        update_question(service.title, update.callback_query)
        # create_question_layout(service.title, update)

        for i in service.images.all():
            context.bot.send_sticker(chat_id=update.effective_chat.id, sticker=i.image)
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="عکس هایی تو این زاویه که فرستادیم برات از خودت بگیر و همینجا بفرس برامون \n وقتی فرستادی روی بعدی/تمام شد بزن")

    if UserService.objects.filter(user=user, services=service).exists() is True:
        user_service = UserService.objects.get(user=user, services=service)
        user_service_image_count = len(user_service.images.all())
        if user_service_image_count < service_sticker_count:
            send_stickers()
            dispatcher.add_handler(MessageHandler(Filters.photo, reply_photo_to_stickers))
        else:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="شما قبلا درخواست داده اید. لطفا با پشتیبانی تماس حاصل فرمایید.")
            contact_us(update, context)
    else:
        user_service = UserService.objects.create(user=user, services=service)
        send_stickers()
        dispatcher.add_handler(MessageHandler(Filters.photo, reply_photo_to_stickers))


def inline_query(update, context):
    user = User.objects.get(telegram_id=update.callback_query.message.chat.id)
    if 'service__' in update.callback_query.data:
        service_id = update.callback_query.data.split('__')[1]
        service = Service.objects.get(pk=service_id)
        # update.callback_query.message.reply_text()
        service_sticker_count = len(service.images.all())

        user_request_service(update, context, user, service, service_sticker_count)

        # update.callback_query.answer()


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


def end_send_image(update, context):
    context.bot.send_message(text='در خواست سرویس شما با موفقیت ثبت شد.', chat_id=update.message.chat_id,
                             reply_markup=ReplyKeyboardRemove())
    get_contact_user(update, context)


def next_send_image(update, context):
    update.message.reply_text(
        text="لطفا عکس بعدی را ارسال کنید",
        reply_markup=ReplyKeyboardMarkup(KEYBOARD_MARKUPS['NEXT'],
                                         one_time_keyboard=True)
    )


def service(update, _):
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


class EndSendImageFilter(BaseFilter):
    def filter(self, message):
        return 'تمام شد' == message.text


class NextSendImageFilter(BaseFilter):
    def filter(self, message):
        return 'بعدی' == message.text


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

        end_send_image_handler_text = MessageHandler(EndSendImageFilter(), end_send_image)
        dispatcher.add_handler(end_send_image_handler_text)
        next_send_image_handler_text = MessageHandler(NextSendImageFilter(), next_send_image)
        dispatcher.add_handler(next_send_image_handler_text)

        updater.start_polling()
        updater.idle()
