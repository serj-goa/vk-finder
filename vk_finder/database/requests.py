from sqlalchemy.orm import declarative_base

from vk_finder.config.connection import Session
from vk_finder.database.models import BotSearchResult, Contact, Photo


db_session = Session()


def select_contact_count(user_id) -> int:
    """
    Selects the number of contacts stored in the database.
    """
    return db_session.query(Contact).filter(Contact.vk_id == user_id).count()


def select_contact_info(user_id) -> dict:
    """
    Selects from the database information about contact (firstname and lastname).
    """
    contact = db_session.query(Contact).get(user_id)
    return {
        'first_name': contact.firstname,
        'last_name': contact.lastname,
    }


def select_contact_photos(user_id) -> list:
    """
    Selects from the database all contact images identifiers.
    """
    photos = []

    for photo in db_session.query(Photo).filter(Photo.vk_id == user_id).all():
        photos.append(photo.vk_photo_id)

    return photos


def select_is_favorite_contacts(user_id: int) -> list:
    """
    Selects from the database all favorites contact profiles.
    """
    return db_session.query(BotSearchResult.who_found_vk_id).filter(BotSearchResult.is_favorited == True).filter(BotSearchResult.who_looking_vk_id == user_id).all()


def select_is_view_contacts() -> list:
    """
    Selects from the database all the viewed contact profiles.
    """
    return db_session.query(BotSearchResult.who_found_vk_id).filter(BotSearchResult.is_viewed == True).all()


def save_data(model_name: str, fields: dict) -> None:
    """
    Saves a new instance of the model in the database.
    """
    models = {
        'bot_search_results': BotSearchResult,
        'contacts': Contact,
        'photos': Photo,
    }

    model = models[model_name](**fields)

    db_session.add(model)
    db_session.commit()


def check_is_favorite(sender: int, contact_id: int) -> None:
    """
    Adds a mark with a contact indicating that it is in the list 
    of selected by a certain user.
    """
    record = db_session.query(BotSearchResult).get((sender, contact_id))
    record.is_favorited = True

    db_session.commit()
