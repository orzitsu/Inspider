# -*- coding: utf-8 -*-
__author__ = 'Orzitsu Loong'

import Inspider

if __name__ == '__main__':
    example = Inspider.Instagram()

    # Login ( OPTIONAL )
    # example.login(username='REPALCE THIS WITH YOUR OWN ACCOUNT', password='REPLACE THIS WITH YOUR PASSWORD')

    # User
    usr = example.user(username='instagram')
    print(usr)

    # Following
    following_list = example.following(username='instagram')
    print(following_list)

    # Follower
    follower_list = example.follower(username='instagram')
    print(follower_list)

    # Tag
    tags = example.tag(name='world')
    print(tags)

    # Media
    media = example.media('BTDHrCsj7RC')
    print(media)

    # Search
    search_result = example.search(keyword='earth')
    print(search_result)
