import os
import vk_api

from dotenv import find_dotenv, load_dotenv


load_dotenv(find_dotenv())

session = vk_api.VkApi(token=os.getenv('VK_GROUP_TOKEN'))
user_session = vk_api.VkApi(token=os.getenv('VK_USER_TOKEN'))
