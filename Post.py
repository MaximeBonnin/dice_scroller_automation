import requests
from bs4 import BeautifulSoup
from pprint import pprint
import re

class Post():
    POSSIBLE_LANGUAGES = ["en"]
    DICE_SCROLLER = "https://dice-scroller.com"
    
    def __init__(self, url: str) -> None:
        self.url = url
        self.translations = {lang: None for lang in Post.POSSIBLE_LANGUAGES}
        
        self.set_language()
        self.set_body()
        self.find_translations()
        
        # pprint(self.translations)
        
    def set_body(self):
        response = requests.get(self.url)
        self.body = response.text
        
        
    def find_translations(self):
        last_character_to_check = 2000 # since it should be in the header, this should be fine. Parsing would be better prob

        link_tag_pattern = "<link.+hreflang=\"..\" \/>"
        hreflang_patter = "(?<=hreflang=\")..(?=\")"
        url_pattern = "(?<=href=\").*?(?=\")"
        
        found = re.findall(string=self.body[:last_character_to_check], pattern=link_tag_pattern)
        for match in found:
            lang_match = re.search(string=match, pattern=hreflang_patter).group()
            url_match = re.search(string=match, pattern=url_pattern).group()
            self.translations[lang_match] = url_match


    def set_language(self) -> None:
        self.language = "de"
        lang_index = len(Post.DICE_SCROLLER)
        lang_slice = self.url[lang_index:lang_index+4]

        for lang in Post.POSSIBLE_LANGUAGES:
            if lang_slice == f"/{lang}/":
                self.language = lang
            
        

    def __str__(self) -> str:
        return self.url
    

if __name__ == "__main__":
    Post("https://dice-scroller.com/halblinge-in-dungeons-and-dragons/")