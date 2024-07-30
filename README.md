# Automated translation of WordPress Posts using ChatGPT and DeepL using Python

This project is mostly for personal use but if you can get some inspiration out of it, feel free!

## Use case

Together with a friend I run a small German Dungeons and Dragons Blog called [Dice-Scroller](https://dice-scroller.com/). We write our posts in German but would like to also have them translated into other languages, mainly English, to gain more readers.

We started doing translation manually, which worked okay for a bit but got really boring very quickly. So I thought, why not just automate it?

## How it works

1. Get the Post content from the WordPress Page (using the wordpress REST API)
2. Use DeepL API to translate the Post
3. Use OpenAI API (GPT-4 turbo) to verify that the translation is good. This means verifying, that D&D specific terms are used correctly and not translated literally.
4. Create a draft with the translated post in WordPress, so it can be finalized and posted manually. 

## Known issues / TODOs

Currently, the meta description is not set by the script. There is not endpoint for it in the REST API and the plugin we use (Yoast) seems to charge for this use case. 

The localization is not done automatically, so directly posting the translation will result in an English post on a German site. We use Polylang to manage translated posts and have to manually set this as well.

"""bash
source venv/Scripts/activate

"""