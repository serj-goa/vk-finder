from vk_api.longpoll import VkLongPoll, VkEventType

from src.config.config import session
from src.vk_api_methods import find_contacts, get_current_user_data, get_cities_from_db, \
                                get_contact_photo, send_message


def clean_contacts(all_contacts: list) -> list:
    if not all_contacts:
        print('Подходящих контактов не найдено.')

        return all_contacts

    contacts = []

    for contact in all_contacts:
        if not contact['is_closed']:
            contacts.append(contact)

    return contacts


def get_info_by_user(user_data: dict, user_id: int) -> None:
    none_fields = list(filter(lambda x: x[1] is None, user_data[user_id].items()))
    
    if not none_fields:
        return None
    
    for key, value in none_fields:
        if key == 'user_birth':
            send_message(user_id, message='Укажите возраст от:')
            age_from = get_user_age()

            send_message(user_id, message='Укажите возраст до:')
            age_to = get_user_age()

            user_data[user_id]['age_from'] = age_from
            user_data[user_id]['age_to'] = age_to

        elif key == 'user_gender':
            pass

        elif key == 'user_city':
            send_message(user_id, message=f'Укажите город для поиска')

            city, city_id = get_user_city()
            user_data[user_id]['user_city'] = city
            user_data[user_id]['user_city_id'] = city_id

            send_message(user_id, message=f'выбран город {city.title()}')


def get_year_by_birth(user_birth: str) -> int | None:
    if user_birth is None:
        return None

    year = user_birth.split('.')

    if len(year) == 3:
        return int(year[2])


def get_user_age() -> int:
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


def parse_user_info_by_fields(data: dict, user_data: dict, user_id: int):
    year = get_year_by_birth(user_birth=data.get('bdate'))

    user_data[user_id] = {
        'user_birth': year,
        'user_gender': data.get('sex'),
        'user_city': None,
    }


def show_contact_in_bot(contacts, user_id, keyboard_args):

    for contact in contacts:
        photo = get_contact_photo(contact_id=contact['id'])

        if photo:
            msg = f"{contact['first_name']} {contact['last_name']}\nhttps://vk.com/id{contact['id']}"
            send_message(
                user_id=user_id, 
                message=msg, 
                attachments=photo['attachments'],
                keyboard_args=keyboard_args,
            )

            for event in VkLongPoll(session).listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    msg = event.text.strip().lower()

                    if msg == 'далее':
                        break
                    elif msg == 'стоп':
                        return


def start_contact_search(sender: int):
    current_request = {}
    current_id = sender

    fields = get_current_user_data(user_id=sender)
    print(fields)

    parse_user_info_by_fields(
        data=fields, 
        user_data=current_request,
        user_id=sender
    )

    get_info_by_user(user_data=current_request, user_id=sender)

    all_contacts = find_contacts(user_info=current_request, user_id=current_id)
    response_contacts = clean_contacts(all_contacts)

    show_contact_in_bot(
        contacts=response_contacts, 
        user_id=current_id, 
        keyboard_args=(('Далее', 'blue'), ('Стоп', 'red'))
    )

    send_message(
        user_id=current_id, 
        message='Вы остановили поиск, пожалуйста выберите новую команду',
        keyboard_args=(('Привет Бот', 'blue'), ('Найти пару', 'blue'), )
    )


def start_main_event() -> tuple:
    for event in VkLongPoll(session).listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            reseived_message = event.text.lower()
            sender = event.user_id

            if reseived_message in ('привет', 'привет бот'):
                fields = get_current_user_data(user_id=sender)
                send_message(
                    user_id=sender, 
                    message=f"Привет {fields['first_name']},\n\
                            для поиска пары нажми кнопку Найти пару",
                    keyboard_args=(('Найти пару', 'blue'), )
                )

            elif reseived_message in ('найти', 'найти пару'):
                break
                
            else:
                send_message(
                    user_id=sender, 
                    message='Выбери необходимую команду',
                    keyboard_args=(('Привет Бот', 'blue'), ('Найти пару', 'blue'), )
                )

    return reseived_message, sender
