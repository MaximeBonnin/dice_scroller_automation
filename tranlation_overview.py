import requests
import xmltodict
from pprint import pprint
from translate import find_translation
from Post import Post

SITEMAP_URL = "https://dice-scroller.com/post-sitemap.xml"



def get_list_of_posts() -> list["Post"]:
    response = requests.get(SITEMAP_URL)
    xml_as_dict = xmltodict.parse(response.text)
    post_list = []
    for entry in xml_as_dict["urlset"]["url"]:
        print(f"Creating post: {entry['loc']}")
        post_list.append(Post(entry["loc"]))
    return post_list



def translation_overview():
    post_list = get_list_of_posts()




if __name__ == "__main__":
    translation_overview()