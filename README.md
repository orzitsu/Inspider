# Inspider
A Web Spider/Crawler for Instagram written in Python.

## Changelog
#### [1.0.1] - 2017-07-10
- Update Inspider.py to fit the new Instagram API.

## Requirements
#### Python 3.x
For more details, visit [here](https://www.python.org/downloads/).
#### Beautiful Soup 4
Simplest way to install BS4, try pip: ```pip install beautifulsoup4```  
For more details, visit [here](https://www.crummy.com/software/BeautifulSoup/).

## Quick Start
Reading this section will help you learn how to use this module and modify your own code in a short time, for example code, click [Example.py](https://github.com/orzitsu/Inspider/blob/master/Example.py).  
#### 1. Import
```import Inspider```
#### 2. Initialization
```example = Inspider.Instagram()```  
#### 3. Start  

##### Login  
This method is *OPTIONAL*, it depends on whether you are going to visit private account or requst one's following / follower list.  
```example.login(username='Your Username/Phone number/email', password='Your Password')```  

##### User  
This method imitates visiting an Instagram account. Here we take visiting [https://www.instagram.com/instagram/](https://www.instagram.com/instagram/) for example, *'instagram'* is the username for this account.  
```usr = example.user(username='instagram')```  
```print(usr)```  

##### Following ( Login before using this method )  
Request one's following list. Again, take username *'instagram'* for example.  
```following_list = example.following(username='instagram')```  
```print(following_list)```  

##### Follower ( Login before using this method )  
Request one's Follower list. Again, take username *'instagram'* for example.  
```follower_list = example.follower(username='instagram')```  
```print(follower_list)```  

##### Tag  
This method imitates visiting an Instagram tag. Here we take visiting [#world](https://www.instagram.com/explore/tags/world/) for example, *'world'* is the tag's name.  
```tags = example.tag(name='world')```  
```print(tags)```  

##### Media  
This method imitates visiting a media page ( Photo / Video / GraphSideca ). To acquire the link of vedio or GraphSideca which contains a bunch of pictures, you'll need to use this method. Here we take visiting [https://www.instagram.com/p/BTDHrCsj7RC/](https://www.instagram.com/p/BTDHrCsj7RC/) for example, *'BTDHrCsj7RC'* is the code of the media.  
```media = example.media('BTDHrCsj7RC')```  
```print(media)```  

##### Search  
Search a keyword in Instagram, it can return users, tags or places. Here we use *'earth'* as keyword.  
```search_result = example.search(keyword='earth')```  
```print(search_result)```  

