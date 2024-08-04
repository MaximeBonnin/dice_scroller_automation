import requests
import xmltodict
from pprint import pprint
from translate import find_translation

SITEMAP_URL = "https://dice-scroller.com/post-sitemap.xml"
DICE_SCROLLER = "https://dice-scroller.com"



def get_list_of_urls(sitemap) -> list["str"]:
    response = requests.get(SITEMAP_URL)
    xml_as_dict = xmltodict.parse(response.text)
    url_list: list["str"] = [l["loc"] for l in xml_as_dict["urlset"]["url"]] 
    return url_list


def split_into(url_list: list, languages: list["str"] = ["en"]) -> dict[str, list["str"]]:   
    lang_index = len(DICE_SCROLLER)
    list_copy = url_list.copy()
    output_dict = {
        "de": list_copy
    }
    
    for lang in languages:
        output_dict[lang] = []
        for url in url_list:
            lang_slice = url[lang_index:lang_index+4]
            if lang_slice == f"/{lang}/":
                output_dict[lang].append(url)
                output_dict["de"].remove(url) # this should be optimized if it is very slow

    return output_dict

def check_all_translations(url_dict: dict[str, list["str"]]):
    remaining = url_dict.copy()
    
    for german_url in url_dict["de"]:
        # print(f"Removing {german_url}")
        remaining["de"].remove(german_url)
        found_url = find_translation(german_url)
        if found_url:
            for lang, translated_urls in remaining.items():
                if lang == "de":
                    continue

                if found_url in translated_urls:
                    # print(f"Removing {found_url}")
                    remaining[lang].remove(found_url)
                
                else:
                    print(f"Something is wrong with {found_url}")

    pprint(remaining)

        


def main():
    url_list = get_list_of_urls(SITEMAP_URL)
    filtered = split_into(url_list, languages=["en"])
    check_all_translations(filtered)




if __name__ == "__main__":
    main()