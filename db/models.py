from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, Table, DATETIME

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
    writer_id = Column(Integer, ForeignKey('writer.id'))
    writer = relationship('Writer')
    tags = relationship('Tag', secondary=tag_post)
    image = Column(String)
    pub_date = Column(DATETIME)
    comments_id = Column(Integer)


class Writer(DB, UrlMixin, IdMixin, NameMixin):
    __tablename__ = 'writer'
    posts = relationship('Post')


class Tag(DB, UrlMixin, IdMixin, NameMixin):
    __tablename__ = 'tag'
    posts = relationship('Post', secondary=tag_post)


class Comment(DB, IdMixin):
    __tablename__ = 'comment'
    api_id = Column(Integer, ForeignKey('post.comments_id'))
    comment_writer = Column(String)
    comment_body = Column(String)

