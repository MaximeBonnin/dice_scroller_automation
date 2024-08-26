import deepl
import re
from slugify import slugify
import base64
import json
import requests
from openai import OpenAI
import logging
import os

# required environment variables:
#   - OPENAI_API_KEY
#   - DEEPL_KEY
#   - WP_USER
#   - WP_PW           (this is not your login, but the auth password)

LOGFILE = "app.log"
translate_logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    filename=LOGFILE,
    filemode="a",
    format="%(asctime)s [%(name)s %(levelname)s] - %(message)s"
)

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

auth_key = os.environ["DEEPL_KEY"]
translator = deepl.Translator(auth_key)

wordpress_user = os.environ["WP_USER"]
wordpress_password = os.environ["WP_PW"]
wordpress_credentials = wordpress_user + ":" + wordpress_password
wordpress_token = base64.b64encode(wordpress_credentials.encode())
wordpress_header = {
    "Authorization": "Basic " + wordpress_token.decode("utf-8"),
    "Content-Type": "application/json",
}


def delete_log_file():
    with open("app.log", "w"):
        pass


def get_id_from_url(url: str) -> str:
    resp = requests.get(url)
    id_pattern = "(?<=name='comment_post_ID' value=').*?(?=' id)"
    found = re.search(string=resp.text, pattern=id_pattern)
    id = found.group()
    int(id)  # verify it is a valid number? bad solution but should work
    return id


def find_translation(url: str, lang: str = "en") -> str:
    last_character_to_check = 2000  # since it should be in the header, this should be fine. Parsing would be better prob
    response = requests.get(url)
    pattern = f'https:\/\/dice-scroller.com\/{lang}/[^"]*/'
    found = re.search(string=response.text[:last_character_to_check], pattern=pattern)

    if found:
        return found.group()

    return False


def handle_links(string: str) -> str:
    translate_logger.info("Checking for links to replace...")
    anchor_pattern = '<a href=\\"https:\/\/dice-scroller.com\/.*?">.*?<\/a>'
    list_of_anchor_tags = re.findall(pattern=anchor_pattern, string=string)
    for anchor_tag in list_of_anchor_tags:
        url_pattern = 'https:\/\/dice-scroller.com\/[^"]*/'
        url = re.search(string=anchor_tag, pattern=url_pattern).group()
        replacement = find_translation(url)

        if replacement:
            translate_logger.info(
                f"Replacing URL: {url[:10]} ... {url[-20:]} ==> {replacement}"
            )
            string = string.replace(url, replacement)

        else:
            # replace anchor tag
            anchor_content_pattern = "(?<=>).*?(?=</a>)"
            anchor_replacement = re.search(
                pattern=anchor_content_pattern, string=anchor_tag
            ).group()
            translate_logger.info(
                f"Replacing Anchor: {anchor_tag[:10]} ... {anchor_tag[-20:]} ==> {anchor_replacement}"
            )
            string = string.replace(anchor_tag, anchor_replacement)

    return string


def get_wp_post(id: str) -> dict:
    translate_logger.info(f"GET post with ID: {id}")
    url = f"https://dice-scroller.com/wp-json/wp/v2/posts/{id}"
    resp = requests.get(url=url)
    translate_logger.info("Status: " + f"{resp.status_code}")
    with open("reponse.json", "w") as f:
        translate_logger.info("Writing to file...")
        f.writelines(json.dumps(resp.json(), indent=2))

    return resp.json()


def translate_with_deepl(string: str) -> str:
    translate_logger.info("Translate using DeepL...")
    result = translator.translate_text(string, target_lang="EN-US")
    return result.text


def verifiy_using_gpt(german: str, english: str) -> str:
    translate_logger.info("Verify using GPT...")
    completion = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are part of an automated translation system for Dungeons and Dragons posts from German to English. You will be provided a German post and an English translation. Preserve the HTML and any links or URLs as they are, only edit the human-readable content. Make sure the Dungeons and Dragons terms are translated correctly and correct them if they are not. Respond with the full translated text, including the html.",
            },
            {"role": "user", "content": f"{german} \n\n\n\n\n\n{english}"},
        ],
    )
    return completion.choices[0].message.content


def fill_in_data(json: dict, content: str) -> dict:
    translated_title = translate_with_deepl(json["title"]["rendered"])
    slugified_title = slugify(translated_title)

    output = {
        # "date": "",
        # "date_gmt": "",
        "slug": slugified_title,
        "status": "draft",
        # password
        "title": translated_title,
        "content": content,
        "author": json["author"],
        # "exerpt": "",
        "featured_media": json["featured_media"],
        "comment_status": json["comment_status"],
        "ping_status": json["ping_status"],
        "sticky": json["sticky"],
        "template": json["template"],
        "meta": {
            "description": "Test meta description",
            "_yoast_wpseo_metadesc": "Test meta desc",
        },
        # "categories": "",
        # "tags": ""
        "format": json["format"],
    }
    return output


def post_to_wp(data) -> None:
    translate_logger.info("Posting to WordPress...")
    api_url = "https://dice-scroller.com/wp-json/wp/v2/posts"
    response = requests.post(api_url, headers=wordpress_header, json=data)
    translate_logger.info("Reponse: " + f"{response.status_code})")
    assert response.status_code == 201, "Response should be 201: Created"
    translate_logger.info("Draft created in WordPress")


def translate(url: str):
    if not url or "https://dice-scroller.com/" not in url:
        translate_logger.error("URL including 'https://dice-scroller.com/' required.")
        return
    id = get_id_from_url(url)
    wp_post_json = get_wp_post(id)
    if find_translation(url):
        translate_logger.error("URL already translated")
        return
    content = wp_post_json["content"]["rendered"]
    content = handle_links(content)
    deepl_translated = translate_with_deepl(content)
    gpt_verified = verifiy_using_gpt(german=content, english=deepl_translated)
    post_data = fill_in_data(wp_post_json, gpt_verified)
    post_to_wp(post_data)
    translate_logger.info("Post translated!")
    translate_logger.info(
        f"Translated post in editor: <a href='https://dice-scroller.com/wp-admin/post.php?post={id}&action=edit'>https://dice-scroller.com/wp-admin/post.php?post={id}&action=edit</a>"
    )


if __name__ == "__main__":
    translate("https://dice-scroller.com/hexenmeister-in-dnd/")
