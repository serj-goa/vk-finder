import sqlalchemy as sa

from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


class Contact(Base):
    __tablename__ = 'contacts'

    vk_id = sa.Column(sa.Integer, primary_key=True)
    firstname = sa.Column(sa.String(length=60))
    lastname = sa.Column(sa.String(length=80))

    created_at = sa.Column(sa.DateTime(timezone=True), index=True, server_default=sa.func.now())


class Photo(Base):
    __tablename__ = 'photos'

    vk_id = sa.Column(sa.Integer, sa.ForeignKey(Contact.vk_id, ondelete='CASCADE'), primary_key=True)
    vk_photo_id = sa.Column(sa.String(length=32), primary_key=True)

    created_at = sa.Column(sa.DateTime(timezone=True), index=True, server_default=sa.func.now())

    contact = relationship(Contact, backref='photos')


class BotSearchResult(Base):
    __tablename__ = 'bot_search_results'

    who_looking_vk_id = sa.Column(sa.Integer, sa.ForeignKey(Contact.vk_id, ondelete='CASCADE'), primary_key=True, nullable=False)
    who_found_vk_id = sa.Column(sa.Integer, sa.ForeignKey(Contact.vk_id, ondelete='CASCADE'), primary_key=True, nullable=False)

    is_viewed = sa.Column(sa.Boolean, index=True, default=True)
    is_favorited = sa.Column(sa.Boolean, index=True, default=False)
    is_black_listed = sa.Column(sa.Boolean, index=True, default=False)

    created_at = sa.Column(sa.DateTime(timezone=True), index=True, server_default=sa.func.now())
    viewed_at = sa.Column(sa.DateTime(timezone=True), nullable=True, server_default=sa.func.now())
    favorited_at = sa.Column(sa.DateTime(timezone=True), nullable=True)
    black_listed_at = sa.Column(sa.DateTime(timezone=True), nullable=True)

    who_looking = relationship(Contact, foreign_keys=[who_looking_vk_id])
    who_found = relationship(Contact, foreign_keys=[who_found_vk_id])
