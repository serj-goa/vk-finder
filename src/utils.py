from vk_api.utils import get_random_id

from src.config.config import session, user_session


def correct_user_info(user_data: dict, user_id: int, flags: dict, event) -> None:
    if user_data[user_id]['user_birth'] is None and flags['start_request']:
        if flags['send_msg_date']:
            user_data[user_id]['user_birth'] = event.text.strip()

    elif user_data[user_id]['user_gender'] is None and flags['start_request']:
        if flags['send_msg_gender']:
            user_data[user_id]['user_gender'] = event.text.strip().lower()

    elif user_data[user_id]['user_city'] is None and flags['start_request']:
        if flags['send_msg_city']:
            user_data[user_id]['user_city'] = event.text.strip().lower()


def find_persons(user_info: dict, user_id: int):
    response = user_session.method(
        'users.search',
        {
            'sex': user_info[user_id]['user_gender'] - 1,
            'has_photo': 1,
            'count': 1000,
            'v': 5.131,
        }
    )
    if response:
        return response.get('items')[:20]

    send_message(user_id, 'Ошибка')


def parse_user_info(data: dict, user_data: dict, user_id: int):
    user_data[user_id] = {
        'user_birth': data.get('bdate'),
        'user_gender': data.get('sex'),
        'user_city': data.get('city'),
    }


def send_message(user_id: int, message: str) -> None:
    session.method(
        'messages.send', 
        {
            'user_id': user_id, 
            'message': message, 
            'random_id': get_random_id(), 
        }
    )


def set_default_flags(flags: dict) -> None:
    for key in flags.keys():
        flags[key] = False


def show_clarifying_message(user_data: dict, user_id: str, flags: dict) -> None:
    if user_data[user_id]['user_birth'] is None and flags['start_request']:
        if not flags['send_msg_date']:
            send_message(user_id, message='Укажите дату рождения цифрами в формате месяц.день.год полностью')
            flags['send_msg_date'] = True

    elif user_data[user_id]['user_gender'] is None and flags['start_request']:
        if not flags['send_msg_gender']:
            send_message(user_id, message='Укажите пол одной буквой М или Ж')
            flags['send_msg_gender'] = True

    elif user_data[user_id]['user_city'] is None and flags['start_request']:
        if not flags['send_msg_city']:
            send_message(user_id, message='Укажите город')
            flags['send_msg_city'] = True
