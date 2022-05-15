from src.data_store import data_store
from src import config
from os import listdir
import os

GENERIC_PROFILE_IMAGE_NAME = "0d6615773aad20b57351.jpg"
GENERIC_PROFILE_URL = config.url + "imgurl/" + GENERIC_PROFILE_IMAGE_NAME

OWNER_PERMISSION = 1
MEMBER_PERMISSION = 2

THUMBS_UP_REACT = 1

HASH_URL_LENGTH = 20
PHOTO_X_BOUND = 2
PHOTO_Y_BOUND = 3

def clear_v1():
    store = data_store.get()
    store['users'].clear()
    store['channels'].clear()
    store['messages'].clear()
    store['dms'].clear()
    store['standups'].clear()
    user_stats = store['user_stats']
    user_stats['channels_joined'].clear()
    user_stats['dms_joined'].clear()
    user_stats['messages_sent'].clear()
    workspace_stats = store['workspace_stats']
    workspace_stats['channels_exist'].clear()
    workspace_stats['dms_exist'].clear()
    workspace_stats['messages_exist'].clear()
    data_store.set(store)
    list_of_images = listdir("src/static")
    for image in list_of_images:
        if str(image) != GENERIC_PROFILE_IMAGE_NAME:
            os.remove("src/static/" + image)

    