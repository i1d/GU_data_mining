from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from . import models

table_mapper = {
    'post_data': models.Post,
    'writer_data': models.Writer
}


class Database:
    def __init__(self, db_url):
        engine = create_engine(db_url)
        models.DB.metadata.create_all(bind=engine)
        self.maker = sessionmaker(bind=engine)

    def get_or_create(self, session, model, filter, **data):
        db_instance = session.query(model).filter_by(**filter).first()
        if not db_instance:
            db_instance = model(**data)
        return db_instance

    def create_post(self, data):
        session = self.maker()
        post = None
        for key, model in table_mapper.items():
            instance = self.get_or_create(session, model, {'url': data[key]['url']}, **data[key])
            if isinstance(instance, models.Post):
                post = instance
            elif isinstance(instance, models.Writer):
                post.writer = instance
        post.tags.extend([
            self.get_or_create(session, models.Tag, {'url': tag_data['url']}, **tag_data)
            for tag_data in data['tags_data']
        ])
        try:
            session.add(post)
            session.commit()
        except Exception as e:
            print(e)
            session.rollback()
        finally:
            session.close()
        print(data['post_data']['url'])

    def create_comment(self, comment_data):
        session = self.maker()
        comment = models.Comment(**comment_data)
#        comment.posts.extend([
#                             com_data for com_data in comment_data
#        ])
     #   comment.comment_writer = comment_data['comment_writer']
     #   comment.comment_body = comment_data['comment_body']
     #   comment.api_id = comment_data['api_id']
        try:
            session.add(comment)
            session.commit()
        except Exception as e:
            print(e)
            session.rollback()
        finally:
            session.close()
        print(comment_data['api_id'])

