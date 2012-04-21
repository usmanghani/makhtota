# Scrapy settings for dli project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'dli'
BOT_VERSION = '1.0'

SPIDER_MODULES = ['dli.spiders']
NEWSPIDER_MODULE = 'dli.spiders'
DEFAULT_ITEM_CLASS = 'dli.items.DliItem'
USER_AGENT = '%s/%s' % (BOT_NAME, BOT_VERSION)

