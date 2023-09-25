from telegram import InlineKeyboardButton, InlineKeyboardMarkup

START_KEYBOARD = InlineKeyboardMarkup(
    [
        [
            #InlineKeyboardButton('Предыдущее блюдо', callback_data='previous_dish'),
            InlineKeyboardButton('Другое блюдо', callback_data='another_dish'),
            InlineKeyboardButton('Ингредиенты блюда', callback_data='dish_ingredients')
        ],
        [


        ]
    ]
)

SUBSCRIPTION = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton('Оформить подписку', callback_data='subscribe'),
        ]
    ]
)