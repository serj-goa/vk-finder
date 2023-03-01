from vk_finder.database.requests import db_session
from vk_finder.utils import start_contact_search, start_favorite_contacts_command, start_main_event


def main():
    try:
        while True:
            received_message, sender = start_main_event()

            if received_message in ('найти', 'найти пару'):
                start_contact_search(sender)

            elif received_message in ('избранное', 'топ'):
                start_favorite_contacts_command(sender)

    except KeyboardInterrupt:
        print('\nБот остановлен.')

    finally:
        db_session.close()


if __name__ == '__main__':
    main()
