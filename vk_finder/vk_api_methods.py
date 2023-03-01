from vk_api.exceptions import ApiError
from vk_api.utils import get_random_id

from vk_finder.config.config import session, user_session
from vk_finder.vk_api_keyboard import create_keyboard


def find_contacts(user_info: dict, user_id: int, status: None) -> list:
    """
    Receives through the API, list of contacts suitable for transmitted parameters 
    in accordance with the requirements for the 'users.search' method.
    sex: 1 - woman, 2 - man
    status: 1 - not married, 6 - in active search
    """
    response = user_session.method(
        'users.search',
        {
            'sex': 1 if user_info[user_id]['user_gender'] == 2 else 2,
            'status': status,
            'has_photo': 1,
            'city': user_info[user_id]['user_city_id'],
            'birth_year': user_info[user_id]['user_birth'],
            'age_from': user_info[user_id].get('age_from', None),
            'age_to': user_info[user_id].get('age_to', None),
            'count': 1000,
            'v': 5.131,
        }
    )

    if response:
        return response.get('items')

    send_message(user_id, 'Ошибка')
    return []


def get_cities_from_db(query: str) -> dict:
    """
    Receives through the API the data of cities suitable for the transmitted template, 
    in accordance with the requirements for the method 'Database.getcities'.
    """
    return user_session.method(
        'database.getCities',
        {
            'q': query,
            'v': 5.131,
        }
    )


def get_contact_photo(contact_id: int) -> dict | None:
    """
    Receives top three contact photos of the contact profile.
    Popularity is determined by the number of likes and comments.
    """
    try:
        response = user_session.method(
            'photos.get', 
            {
                'owner_id': contact_id,
                'album_id': 'profile',
                'extended': '1',
                'v': 5.131,
            }
        )

        if response.get('count') and response.get('count') >= 3:

            top_photos = sorted(
                response.get('items'), 
                key=lambda x: x['likes']['count'] + x['comments']['count'], 
                reverse=True
            )[:3]

            photos = ''
            id_ = top_photos[0]['owner_id']

            for photo in top_photos:
                photos += f"photo{id_}_{photo['id']},"

            photo_data = {'user_id': id_, 'attachments': photos}

            return photo_data

        return None

    except ApiError as error:
        print(f'Contact id {contact_id} get_photos error.\n{error}')
        return None


def get_current_user_data(user_id: int) -> dict:
    """
    Receives from the API user data provided for by the 'users.get' method.
    ('id', 'bdate', 'sex', 'first_name', 'last_name', 'can_access_closed', 'is_closed')
    """
    return session.method(
        'users.get', 
        {
            'user_ids': user_id, 
            'fields': 'sex, bdate, city,',
        }
    )[0]


def send_message(user_id: int, message: str, attachments: str = None, keyboard_args=None) -> None:
    """
    Sends through the API message specified in its ID
    in accordance with the requirements for the method 'Messages.Send', 
    and there is also the possibility of transferring the keyboard to the chatbot.
    """
    if keyboard_args is not None:
        keyboard = create_keyboard(keyboard_args)

    session.method(
        'messages.send', 
        {
            'user_id': user_id, 
            'message': message, 
            'random_id': get_random_id(),
            'attachment': attachments,
            'keyboard':  keyboard.get_keyboard() if keyboard_args is not None else keyboard_args,
        }
    )
