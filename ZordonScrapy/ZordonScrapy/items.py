# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ZordonscrapyItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class MovieItem(scrapy.Item):
    cod_imdb = scrapy.Field()
    title = scrapy.Field()
    original_title = scrapy.Field()
    release_date = scrapy.Field()
    director = scrapy.Field()
    writers = scrapy.Field()
    main_cast_members = scrapy.Field()
    meta_score = scrapy.Field()
    mpaa_rating = scrapy.Field()
    runtime = scrapy.Field()
    imdb_rating = scrapy.Field()
    genres = scrapy.Field()
    budget = scrapy.Field()
    world_wide_box_office = scrapy.Field()
    language = scrapy.Field()
    countries = scrapy.Field()
