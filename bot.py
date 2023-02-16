from vk_api.longpoll import VkLongPoll, VkEventType

from src.config.config import session
from src.utils import correct_user_info, find_persons, parse_user_info, \
    send_message, set_default_flags, show_clarifying_message

current_request = {}
current_id = None
sessions_flags = {
    'start_request': False,
    'send_msg_date': False,
    'send_msg_gender': False,
    'send_msg_city': False,
}
set_default_flags(flags=sessions_flags)
search_data = False

try:
    for event in VkLongPoll(session).listen():

        if search_data:
            response = find_persons(user_info=current_request, user_id=current_id)
            print(f'Response:\n{response}')
            search_data = False

        elif sessions_flags['start_request']:
            if not (
                    current_request[current_id]['user_birth'] and \
                    current_request[current_id]['user_gender'] and \
                    current_request[current_id]['user_city']
            ):
                show_clarifying_message(
                    user_data=current_request,
                    user_id=current_id,
                    flags=sessions_flags
                )

            else:
                print(f'Send request.\n{current_request}')
                send_message(user_id=current_id, message=f'Send request.')
                search_data = True

                set_default_flags(flags=sessions_flags)

        if not (event.type == VkEventType.MESSAGE_NEW and event.to_me):
            continue

        reseived_message = event.text.lower()
        sender = event.user_id

        if reseived_message == 'привет':
            send_message(user_id=sender, message=f'Хай, {sender}')

        elif reseived_message == 'пока':
            send_message(user_id=sender, message='Пока((')

        elif reseived_message == 'найти' and not sessions_flags['start_request']:
            sessions_flags['start_request'] = True
            current_id = sender
            fields = session.method(
                'users.get',
                {
                    'user_ids': sender,
                    'fields': 'sex, bdate, city,',
                }
            )[0]
            print(fields)

            parse_user_info(
                data=fields,
                user_data=current_request,
                user_id=sender
            )

        elif sessions_flags['start_request']:
            correct_user_info(
                user_data=current_request,
                user_id=sender,
                flags=sessions_flags,
                event=event
            )

        else:
            send_message(user_id=sender, message='Не понял вашего ответа...')
            set_default_flags(flags=sessions_flags)

except KeyboardInterrupt:
    print('\nБот остановлен.')
