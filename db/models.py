from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, Table

DB = declarative_base()


class UrlMixin:
    url = Column(String, nullable=False, unique=True)


class IdMixin:
    id = Column(Integer, primary_key=True, autoincrement=True)


class NameMixin:
    name = Column(String, nullable=False)


tag_post = Table(
    'tag_post',
    DB.metadata,
    Column('post_id', Integer, ForeignKey('post.id')),
    Column('tag_id', Integer, ForeignKey('tag.id'))
)


class Post(DB, UrlMixin):
    __tablename__ = 'post'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    author_id = Column(Integer, ForeignKey('author.id'))
    author = relationship('Author')
    tags = relationship('Tag', secondary=tag_post)


class Author(DB, UrlMixin, IdMixin, NameMixin):
    __tablename__ = 'author'
    posts = relationship('Post')


class Tag(DB, UrlMixin, IdMixin, NameMixin):
    __tablename__ = 'tag'
    posts = relationship('Post', secondary=tag_post)
