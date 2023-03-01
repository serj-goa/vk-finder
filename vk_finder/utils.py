from vk_api.longpoll import VkLongPoll, VkEventType

from vk_finder.config.config import session
from vk_finder.database.requests import check_is_favorite, save_data, select_contact_count, \
                                select_is_favorite_contacts, select_is_view_contacts, select_contact_info, \
                                select_contact_photos
from vk_finder.vk_api_methods import find_contacts, get_current_user_data, get_cities_from_db, \
                                get_contact_photo, send_message


def add_contact_to_db(contact_id: int, fields: dict = None, photo: dict = None, is_sender: bool = False, sender_id: int =None) -> None:
    """
    Adding contacts to the database.
    """
    if fields is None:
        fields: dict = get_current_user_data(user_id=contact_id)

    exists_db_contact: int = select_contact_count(contact_id)

    if not exists_db_contact:
        save_data(
            model_name='contacts', 
            fields={
                'vk_id': contact_id,
                'firstname': fields['first_name'],
                'lastname': fields['last_name']
            }
        )
        
        if is_sender:
            photo = get_contact_photo(contact_id)

        if photo:
            contact_photos: list = parse_photo_data(contact_data=photo)

            for foto_id in contact_photos:
                save_data(
                    model_name='photos', 
                    fields={
                        'vk_id': contact_id,
                        'vk_photo_id': foto_id
                    }
                )

        if not is_sender:
            save_data(
                model_name='bot_search_results', 
                fields={
                    'who_looking_vk_id': sender_id,
                    'who_found_vk_id': contact_id,
                }
            )


def clean_contacts(all_contacts: list, viewed_contacts: list) -> list:
    """
    Clears the list of contacts with closed profiles 
    and contacts with already viewed profiles.
    """
    if not all_contacts:
        return all_contacts

    contacts = []

    for contact in all_contacts:
        if not contact['is_closed'] and contact['id'] not in viewed_contacts:
            contacts.append(contact)

    return contacts


def get_info_by_user(user_data: dict, user_id: int) -> None:
    """
    Getting by vk_id, the missing information about the contact, 
    to search for a suitable pair.
    """
    none_fields = list(filter(lambda x: x[1] is None, user_data[user_id].items()))
    
    if not none_fields:
        return None
    
    for key, _ in none_fields:
        if key == 'user_birth':
            send_message(user_id, message='Укажите возраст от:')
            age_from = get_user_age()

            send_message(user_id, message='Укажите возраст до:')
            age_to = get_user_age()

            user_data[user_id]['age_from'] = age_from
            user_data[user_id]['age_to'] = age_to

        elif key == 'user_gender':
            send_message(user_id, message='Укажите пол М или Ж для поиска пары')
            user_gender = get_user_gender()
            user_data[user_id]['user_gender'] = user_gender

        elif key == 'user_city':
            send_message(user_id, message=f'Укажите город для поиска')

            city, city_id = get_user_city()
            user_data[user_id]['user_city'] = city
            user_data[user_id]['user_city_id'] = city_id

            send_message(user_id, message=f'выбран город {city.title()}')


def get_year_by_birth(user_birth: str) -> int | None:
    """
    Getting the year from a date.
    """
    if user_birth is None:
        return None

    year = user_birth.split('.')

    if len(year) == 3:
        return int(year[2])


def get_user_age() -> int:
    """
    Getting the age from the user.
    """
    while True:
        for event in VkLongPoll(session).listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                msg = event.text.strip()
                sender = event.user_id
                break
            
        if msg.isdigit():
            return int(msg)

        send_message(user_id=sender, message='Возраст должен быть числом!')


def get_user_city() -> tuple:
    """
    Getting from the user a city for searching 
    and sending a request to the API to check if the received city 
    exists in the database.
    """
    for event in VkLongPoll(session).listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            msg = event.text.strip().lower()
            sender = event.user_id

            response = get_cities_from_db(query=msg)

            cities = list(map(lambda x: x['title'].lower(), response['items']))

            if msg in cities:
                return response['items'][0]['title'], response['items'][0]['id']

            else:
                send_message(user_id=sender, message='такого города нет в базе данных.')


def get_user_gender() -> int:
    """
    Getting the gender from the user.
    """
    while True:
        for event in VkLongPoll(session).listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                msg: str = event.text.strip()
                sender: int = event.user_id
                break

        if msg.isalpha() and (msg.startswith('м') or msg.startswith('ж')):
            return 1 if msg.startswith('ж') else 2

        send_message(user_id=sender, message='Укажите пол М или Ж для поиска пары!')


def correct_user_info(data: dict, user_data: dict, user_id: int) -> dict:
    """
    Correction of data received from the API about the user.

    data = {'id': int, 'bdate': 'XX.XX.XXXX', 'sex': int, 'first_name': '', 
            'last_name': '', 'can_access_closed': True, 'is_closed': False}
    """
    year = get_year_by_birth(user_birth=data.get('bdate'))

    user_data[user_id] = {
        'user_birth': year,
        'user_gender': data.get('sex'),
        'user_city': None,
    }

    return user_data


def parse_photo_data(contact_data: dict) -> list:
    """
    Parsing a string and getting photo IDs from it.

    contact_data = {'user_id': int,
    'attachments': 'photo111111_123456789,photo111111_987654321,photo111111_654321789,'}
                    photo<user_id>_<photo_id>
    """
    photo_attachments: str = contact_data['attachments'].replace(',', '')
    photos = []

    for photo_id in photo_attachments.split(f"photo{contact_data['user_id']}_"):
        if photo_id:
            photos.append(photo_id)

    return photos


def show_contact_in_bot(contacts: list, user_id: int, keyboard_args: tuple) -> None:
    """
    Displays data of found contact profiles (name, profile link and photos).
    """
    length_contacts_lst = len(contacts)
    after_favorite_keyboard_args = (('Далее', 'blue'), ('Стоп', 'red'))
    output_message = 'Для просмотра следующего контакта нажмите Далее,\n'\
                    'для выхода из поиска нажмите Стоп'
    
    after_favorite_msg = 'Контакт сохранён в избранное.\n'\
                    'Для просмотра следующего контакта нажмите Далее,\n'\
                    'для выхода из поиска нажмите Стоп'

    for cnt, contact in enumerate(contacts, 1):
        is_favorite = False
        photo = get_contact_photo(contact_id=contact['id'])

        if photo:
            msg = f"{contact['first_name']} {contact['last_name']}\nhttps://vk.com/id{contact['id']}"
            send_message(
                user_id=user_id, 
                message=msg, 
                attachments=photo['attachments'], 
                keyboard_args=keyboard_args,
            )

            add_contact_to_db(
                contact_id=contact['id'], 
                photo=photo,
                sender_id=user_id)

            if cnt == (length_contacts_lst - 1):
                keyboard_args = (('Запомнить', 'blue'), ('Стоп', 'red'), )
                output_message = 'Для выхода из поиска нажмите Стоп'

                after_favorite_keyboard_args = (('Стоп', 'red'), )
                after_favorite_msg = 'Контакт сохранён в избранное.\n'\
                                    'Для выхода из поиска нажмите Стоп'

            for event in VkLongPoll(session).listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    msg = event.text.strip().lower()

                    if msg == 'далее':
                        break

                    elif msg == 'стоп':
                        return
                    
                    elif msg == 'запомнить':
                        check_is_favorite(sender=user_id, contact_id=contact['id'])
                        send_message(
                            user_id=user_id, 
                            message=after_favorite_msg, 
                            keyboard_args=after_favorite_keyboard_args,
                        )

                    else:
                        send_message(
                            user_id=user_id, 
                            message=output_message, 
                            keyboard_args=after_favorite_keyboard_args if is_favorite else keyboard_args,
                        )


def start_contact_search(sender: int) -> None:
    """
    Run command to find pair.
    """
    current_request = {}
    current_id = sender

    fields = get_current_user_data(user_id=sender)

    add_contact_to_db(current_id, fields, is_sender=True)

    current_request = correct_user_info(
        data=fields, 
        user_data=current_request,
        user_id=sender
    )

    get_info_by_user(user_data=current_request, user_id=sender)

    active_contacts: list = find_contacts(user_info=current_request, user_id=current_id, status=6)
    unmarried_contacts: list = find_contacts(user_info=current_request, user_id=current_id, status=1)
    all_contacts = active_contacts + unmarried_contacts

    viewed_contacts = [viewed_contact[0] for viewed_contact in select_is_view_contacts()]

    response_contacts: list = clean_contacts(all_contacts, viewed_contacts)

    if response_contacts:
        output_msg = 'Вы остановили поиск, пожалуйста выберите новую команду'
        show_contact_in_bot(
            contacts=response_contacts, 
            user_id=current_id,
            keyboard_args=(('Далее', 'blue'), ('Запомнить', 'blue'), ('Стоп', 'red'))
        )
    
    else:
        output_msg = 'Подходящих контактов не найдено.'

    send_message(
        user_id=current_id, 
        message=output_msg,
        keyboard_args=(('Привет Бот', 'blue'), ('Найти пару', 'blue'), ('Избранное', 'blue'), )
    )


def show_favorite_contact_in_bot(contacts_ids: list, user_id: int, keyboard_args: tuple) -> None:
    """
    Shows favorite contact profile details (name, profile link, and photos).
    """
    length_contacts_ids = len(contacts_ids)
    only_stop_button = (('Стоп', 'red'), )
    output_message = 'Для просмотра следующего контакта нажмите Далее,\n'\
                    'для выхода из поиска нажмите Стоп'

    for cnt, contact_id in enumerate(contacts_ids, 1):
        contact_info = select_contact_info(contact_id)
        photos = select_contact_photos(contact_id)

        photos_attachments = ''

        for photo in photos:
            photos_attachments += f"photo{contact_id}_{photo},"

        msg = f"{contact_info['first_name']} {contact_info['last_name']}\nhttps://vk.com/id{contact_id}"
        send_message(
            user_id=user_id, 
            message=msg, 
            attachments=photos_attachments, 
            keyboard_args=keyboard_args,
        )
        
        if cnt == (length_contacts_ids - 1):
            keyboard_args = only_stop_button
            output_message = 'Для выхода из поиска нажмите Стоп'

        for event in VkLongPoll(session).listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                msg = event.text.strip().lower()

                if msg == 'далее' and cnt < length_contacts_ids:
                    break

                elif msg == 'стоп':
                    return

                else:
                    send_message(
                        user_id=user_id, 
                        message=output_message, 
                        keyboard_args=keyboard_args
                    )


def start_favorite_contacts_command(sender: int) -> None:
    """
    Run the show profiles of favorite contacts command.
    """
    favorites_contacts = [viewed_contact[0] for viewed_contact in select_is_favorite_contacts(sender)]

    show_favorite_contact_in_bot(
        contacts_ids=favorites_contacts, 
        user_id=sender,
        keyboard_args=(('Далее', 'blue'), ('Стоп', 'red'))
    )
    send_message(
        user_id=sender, 
        message='Вы остановили поиск, пожалуйста выберите новую команду',
        keyboard_args=(('Привет Бот', 'blue'), ('Найти пару', 'blue'), ('Избранное', 'blue'), )
    )


def start_main_event() -> tuple:
    """
    Starting the main command to listen to events in the chatbot and receive commands from the user.
    """
    for event in VkLongPoll(session).listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            received_message = event.text.lower()
            sender = event.user_id

            if received_message in ('привет', 'привет бот'):
                fields = get_current_user_data(user_id=sender)
                send_message(
                    user_id=sender, 
                    message=f"Привет {fields['first_name']},\n"\
                            "для поиска пары нажми кнопку Найти пару",
                    keyboard_args=(('Найти пару', 'blue'), ('Избранное', 'blue'), )
                )

            elif received_message in ('найти', 'найти пару'):
                break

            elif received_message in ('избранное', 'топ'):
                break
                
            else:
                send_message(
                    user_id=sender, 
                    message='Выбери необходимую команду',
                    keyboard_args=(('Привет Бот', 'blue'), ('Найти пару', 'blue'), ('Избранное', 'blue'), )
                )

    return received_message, sender
