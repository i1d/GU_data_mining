import os
import dotenv
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from instagram_parse.spiders.instagram import InstagramSpider


if __name__ == "__main__":
    crawler_settings = Settings()
    crawler_settings.setmodule("instagram_parse.settings")
    crawler_proc = CrawlerProcess(settings=crawler_settings)
    dotenv.load_dotenv(".env")
    instagram_tags = ["python_coder", "geekbrains_ru", "motorcycle_travel"]
    instagram_users = ['global_step']
    instagram_params = {
        "username": os.getenv("USERNAME"),
        "enc_password": os.getenv("ENC_PASSWORD"),
        "tags": instagram_tags,
        'users': instagram_users
    }
    crawler_proc.crawl(InstagramSpider, **instagram_params)
    crawler_proc.start()