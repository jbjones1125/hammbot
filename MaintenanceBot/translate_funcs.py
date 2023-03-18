from googletrans import Translator
from urllib.request import Request
from urllib.error import HTTPError
from PIL import Image
import urllib.request
import pytesseract
import polyglot
import io
import re

translator = Translator()


def extractURL(text):
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    urls = re.findall(regex, text)
    text = re.sub(regex, '', text)
    return urls, text


def translate_text(message_content):
    words = message_content[1:]               # remove ?translate from message content
    msg = ' '.join([word for word in words])  # if no URLs just put it back together
    txt = translator.translate(msg).text      # translate the message
    if len(txt.replace(' ', '')) > 0:         # This prevents a blank message being sent if only URLs were inputted
        return translator.translate(msg).text


def translate_url(url):
    translations = []
    for link in url:
        link = link[0]
        if len(link) > 1:
            try:
                request_site = Request(link, headers={"User-Agent": "Mozilla/5.0"})
                img_from_url = urllib.request.urlopen(request_site)
                img = Image.open(img_from_url)
                # TODO: add support for all available languages
                result = pytesseract.image_to_string(img, config='-l eng+fra+ita+deu+spa+jpn+jpn_vert+chi_sim')
                im_translated = translator.translate(result, dest='english')
                text = str(im_translated.text)
                translations.append(text)
                img.close()
            except urllib.error.HTTPError:
                translations.append("Error: Invalid URL")

    return translations


def translate_image(img_bytes):
    img = Image.open(io.BytesIO(img_bytes))
    # TODO: add support for all available languages
    result = pytesseract.image_to_string(img, config='-l jpn+eng+jpn_vert+chi_sim+fra+ita+deu+spa')
    im_translated = translator.translate(result, dest='english')
    text = str(im_translated.text)
    img.close()
    return text
