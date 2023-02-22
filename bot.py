from src.utils import start_contact_search, start_main_event


def main():
    try:
        while True:
            reseived_message, sender = start_main_event()

            if reseived_message in ('найти', 'найти пару'):
                start_contact_search(sender)

    except KeyboardInterrupt:
        print('\nБот остановлен.')


if __name__ == '__main__':
    main()
