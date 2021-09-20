import sys
import time
from random import randrange

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType


class Kinder:
    def __init__(self, token=None, c_token=None):
        self.v = None
        self.vk = None
        self.token = token
        self.c_token = c_token

        if self.token and self.c_token:
            self.vk = vk_api.VkApi(token=self.token).get_api()

            self.c_vk = vk_api.VkApi(token=self.c_token)
            self.c_lp = VkLongPoll(vk_api.VkApi(token=self.c_token))

            try:
                self.users_get()
            except vk_api.exceptions.ApiError as error_msg:
                print(error_msg)
                sys.exit()


    def users_get(self, id_=None):
        try:
            some_user = self.vk.users.get(user_ids=id_, fields='sex, bdate, city, relation')
            time.sleep(0.3)
        except vk_api.exceptions.ApiError as error_msg:
            print(error_msg)
            return

        return some_user

    def get_prof_photos(self, id_):
        try:
            profile = self.vk.photos.get(owner_id=id_, album_id='profile', extended=1)
            time.sleep(0.3)
        except vk_api.exceptions.ApiError as error_msg:
            print(error_msg)
            return

        return profile

    def search(self, params):
        tool = vk_api.tools.VkTools(self.vk)
        try:
            res = tool.get_all_iter('users.search', 1000, values=params)
        except vk_api.exceptions.ApiError as error_msg:
            print(error_msg)
            return

        return res

    def write_msg(self, user_id, message):
        self.c_vk.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7), })

    def read_msg(self):
        for event in self.c_lp.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:
                    return event


class Talk:
    def __init__(self, k, id_):
        self.k = k
        self.id_ = id_

    def write(self, message):
        self.k.write_msg(self.id_, message)

    def read(self):
        text = False
        while not text:
            event = self.k.read_msg()
            if event.user_id == self.id_:
                text = event.text
        return text
