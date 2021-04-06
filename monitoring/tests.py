import os

from django.test import TestCase
from PIL import Image

class AddServer(TestCase):

    def test_find_server(self):
        path = "/home/zile/study/MONITORING/game-monitoring/media/monitoring/servers_avatar/"
        files = os.listdir(path)
        for file in files:
            print(file)
            if file[-3:] == 'tga':
                im = Image.open(path + file)
                rgb_im = im.convert('RGB')
                print(path + file[:-3] + 'jpg')
                rgb_im.save(path + file[:-3] + 'jpg')
            # os.rename(path + file, path + file[: -8] + ".tga")
            # print (file[: -8])
        # self.assertEqual(Server.objects.filter(ip=self.ip, port=self.port).count(), 0, "Added disconnected server.")
