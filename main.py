from selenium import webdriver
from time import sleep
from account import user, pw
import requests 

class InstaBot(object):

    # method copied from https://github.com/aj-4/ig-followers/blob/master/main.py
    def __init__(self, username, pw):
        # sets up a basic Instagram bot by logging in for user 
        self.username = username
        self.pw = pw
        self.driver = webdriver.Chrome()
        self.driver.get("https://instagram.com")
        sleep(2)
        self.driver.find_element_by_xpath(
            "/html/body/div[1]/section/main/article/div[2]/div[2]/p/a").click()
        sleep(2)
        self.driver.find_element_by_xpath(
            "//input[@name=\"username\"]").send_keys(self.username)
        self.driver.find_element_by_xpath(
            "//input[@name=\"password\"]").send_keys(self.pw)
        self.driver.find_element_by_xpath(
            "//button[@type=\"submit\"]").click()
        sleep(4)
        self.driver.find_element_by_xpath(
            "//button[contains(text(), 'Not Now')]").click()
    
    # method modified from same source above
    def get_unfollowers(self):
        # gets list of users not following you back
        self.driver.find_element_by_xpath(
            "//a[contains(@href,'/{}')]".format(self.username)).click()
        sleep(2)
        self.driver.find_element_by_xpath(
            "//a[contains(@href,'/following')]").click()
        self.following = self.get_names()
        self.driver.find_element_by_xpath(
            "//a[contains(@href,'/followers')]").click()
        self.followers = self.get_names()
        self.not_following_back = set()
        for user in self.following:
            if user not in self.followers:
                self.not_following_back.add(user)
        print("Users not following you back: ")
        print(self.not_following_back)
        self.driver.find_element_by_xpath(
            "//*[@id='react-root']/section/nav/div[2]/div/div/div[1]").click()

    # method modified from same source above
    def get_names(self):
        # gets list of names by scrolling through "following" and "followers"
        sleep(2)
        scroll_box = self.driver.find_element_by_xpath(
            "/html/body/div[4]/div/div[2]")
        last_ht, ht = 0, 1
        while last_ht != ht:
            last_ht = ht
            sleep(1)
            ht = self.driver.execute_script("""
                arguments[0].scrollTo(0, arguments[0].scrollHeight); 
                return arguments[0].scrollHeight;
                """, scroll_box)
        links = scroll_box.find_elements_by_tag_name('a')
        names = [name.text for name in links if name.text != '']
        names_set = set(names)
        self.driver.find_element_by_xpath(
            "/html/body/div[4]/div/div[1]/div/div[2]/button").click()
        return names_set

    def get_num_followers(self, user):
        # uses Requests to obtain number of followers for given user  
        url = 'https://www.instagram.com/' + user
        r = requests.get(url).text
        start = '"edge_followed_by":{"count":'
        end = '},"followed_by_viewer"'
        return int(r[r.find(start)+len(start):r.rfind(end)])

    def unfollow(self):
        # unfollows each non-celebrity not following you back
        self.unfollowed = []
        for user in self.not_following_back:
            self.driver.find_element_by_xpath(
                "//*[@id='react-root']/section/nav/" + 
                "div[2]/div/div/div[2]/input").send_keys(user)
            sleep(2)
            self.driver.find_element_by_xpath(
                "//a[contains(@href,'/{}/')]".format(user)).click()
            sleep(2)
            numFollowers = self.get_num_followers(user)
            sleep(2)
            # identifies non-celebrities as those with less than 10000 followers
            if numFollowers < 10000:
                self.driver.find_element_by_xpath(
                    "//button[@class='_5f5mN    -fzfL     _6VtSN     yZn4P   ']").click() 
                sleep(1)
                self.driver.find_element_by_xpath(
                    "/html/body/div[4]/div/div/div[3]/button[1]").click()
                self.unfollowed.append(user)
            self.driver.find_element_by_xpath(
                "//*[@id='react-root']/section/nav/div[2]/div/div/div[1]").click()
        print("You just unfollowed: ")
        print(self.unfollowed)

mybot = InstaBot(user, pw)
mybot.get_unfollowers()
mybot.unfollow()