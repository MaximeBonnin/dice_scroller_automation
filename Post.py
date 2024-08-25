import requests
import re


class Post:
    POSSIBLE_LANGUAGES = ["de", "en"]
    DICE_SCROLLER = "https://dice-scroller.com"

    def __init__(self, url: str) -> None:
        self.url = url
        self.translations = {lang: None for lang in Post.POSSIBLE_LANGUAGES}

        self.set_language()
        self.body = ""
        # self.set_body()
        # self.find_translations()

        # pprint(self.translations)

    def set_body(self):
        response = requests.get(self.url)
        self.body = response.text

    def find_translations(self):
        last_character_to_check = 2000  # since it should be in the header, this should be fine. Parsing would be better prob

        link_tag_pattern = '<link.+hreflang=".." \/>'
        hreflang_patter = '(?<=hreflang=")..(?=")'
        url_pattern = '(?<=href=").*?(?=")'
        title_pattern = "(?<=<title>).+(?= - Dice Scroller<\/title>)"

        self.title = re.search(
            string=self.body[:last_character_to_check], pattern=title_pattern
        ).group()
        self.title = (
            self.title.replace("&amp;", "&")
            .replace("&#038;", "&")
            .replace("&#8217;", "'")
            .replace("&#039;", "'")
        )
        found = re.findall(
            string=self.body[:last_character_to_check], pattern=link_tag_pattern
        )

        if not found:
            self.translations["de"] = self.url

        for match in found:
            lang_match = re.search(string=match, pattern=hreflang_patter).group()
            url_match = re.search(string=match, pattern=url_pattern).group()
            self.translations[lang_match] = url_match

    def set_language(self) -> None:
        self.language = "de"
        lang_index = len(Post.DICE_SCROLLER)
        lang_slice = self.url[lang_index : lang_index + 4]

        for lang in Post.POSSIBLE_LANGUAGES:
            if lang_slice == f"/{lang}/":
                self.language = lang

    def __str__(self) -> str:
        return self.url

    def __eq__(self, other):
        if type(other) is str:
            return self.url == other
        return self.url == other.url


if __name__ == "__main__":
    one = Post("https://dice-scroller.com/halblinge-in-dungeons-and-dragons/")
    print(one.title)
