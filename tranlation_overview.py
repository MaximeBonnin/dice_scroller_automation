import asyncio
import aiohttp
import requests
import xmltodict
from Post import Post


SITEMAP_URL = "https://dice-scroller.com/post-sitemap.xml"


async def async_create_post(session, url, **kwargs) -> Post:
    try:
        async with session.get(url, **kwargs) as resp:
            new_post = Post(url)
            new_post.body = await resp.text()
            new_post.find_translations()
            return new_post
    except asyncio.ClientConnectorError as e:
        print(e)



async def get_all_posts():
    async with aiohttp.ClientSession() as session:
        response = requests.get(SITEMAP_URL)
        xml_as_dict = xmltodict.parse(response.text)

        tasks = []
        for entry in xml_as_dict["urlset"]["url"]:
            tasks.append(async_create_post(session=session, url=entry["loc"]))
        posts: list["Post"] = await asyncio.gather(*tasks, return_exceptions=True)
        return posts


if __name__ == '__main__':
    response_list = asyncio.run(get_all_posts()) 
    print(response_list)