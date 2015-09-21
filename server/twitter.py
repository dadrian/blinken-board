from __future__ import absolute_import, print_function
from secrets import consumer_key, consumer_secret, access_token, access_token_secret

import asyncio
import websockets
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import json
import logger
import cv2
import tempfile
import urllib.request
import shutil
import time
from PIL import Image
import io

MAX_VIDEO_LENGTH = 45  # seconds

def wait_for(t):
    diff = t - time.time()
    while diff > 0:
        time.sleep(diff*0.9)
        diff = t - time.time()


class StdOutListener(StreamListener):

    @asyncio.coroutine
    def send_png(self, png):
        ws = yield from websockets.client.connect('ws://127.0.0.1:8765/public_png')
        yield from ws.send(png)

    @asyncio.coroutine
    def video_to_pngs(self, fname, loop=True):
        ws = yield from websockets.client.connect('ws://127.0.0.1:8765/public_png')
        start_time = time.time()
        last_frame = start_time
        cap = cv2.VideoCapture(fname)
        fps = cap.get(cv2.CAP_PROP_FPS)
        delay = 1.0 / fps
        cap.set(cv2.CAP_PROP_POS_AVI_RATIO, 1)
        num_frames = cap.get(cv2.CAP_PROP_POS_FRAMES)
        logger.trace('%s FPS, %d frames total' % (str(fps), num_frames))
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        i = 0

        while True:
            ret, frame = cap.read()
            i += 1
            if i == num_frames - 1: # cut off last frame for smoother looping
                i = 0
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                if not(loop):
                    return

            scale = cv2.resize(frame, (57, 45))
            img = cv2.imencode('.png', scale)[1].tostring()

            wait_for(last_frame + delay)
            # send frame over websocket
            yield from ws.send(img)
            last_frame = time.time()


            if last_frame > (start_time + MAX_VIDEO_LENGTH):
                return


    def process_media_tweet(self, obj):
        logger.trace('media tweet')
        for media in obj['extended_entities']['media']:
            logger.trace('type: %s' % (media['type']))
            if media['type'] == 'photo':
                # picture
                url = media['media_url_https']
                with urllib.request.urlopen(url) as response:
                    img = Image.open(io.BytesIO(response.read()))
                    small_img = img.resize((57, 45), Image.ANTIALIAS)
                    out = io.BytesIO()
                    small_img.save(out, format='PNG')

                    loop = asyncio.get_event_loop()
                    loop.run_until_complete(self.send_png(out.getvalue()))
                    loop.close()

            elif 'video_info' in media:
                # video (animated gif as mp4, (mp4?, mov?))
                for variant in media['video_info']['variants']:
                    logger.trace('variant type: %s' % (variant['content_type']))
                    if variant['content_type'] == 'video/mp4':
                        url = variant['url']
                        logger.trace('downloading ' + url)
                        f = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
                        with urllib.request.urlopen(url) as response:
                            shutil.copyfileobj(response, f)

                        # Hack to turn asyncio into a blocking call
                        loop = asyncio.get_event_loop()
                        loop.run_until_complete(self.video_to_pngs(f.name, loop=(media['type']=='animated_gif')))
                        loop.close()



    def process_text_tweet(self, obj):
        logger.trace('text only tweet')
        pass

    def process_tweet(self, obj):
        logger.trace('Got a tweet to us')
        if 'extended_entities' in obj:
            self.process_media_tweet(obj)
        else:
            self.process_text_tweet(obj)

    """ A listener handles tweets are the received from the stream.
    This is a basic listener that just prints received tweets to stdout.
    """
    def on_data(self, data):
        logger.trace('Tracked tweet: ' + data)
        obj = json.loads(data)
        if 'user_mentions' in obj['entities']:
            for mention in obj['entities']['user_mentions']:
                if mention['screen_name'] == 'wall_hacks':
                    self.process_tweet(obj)
        return True

    def on_error(self, status):
        print(status)

if __name__ == '__main__':

    logger.setLogLevel(logger.TRACE)
    logger.info('Go!')
    listener = StdOutListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    #stream = Stream(auth, listener)
    #stream.filter(track=['wall_hacks'])

    #listener.on_data('''{"created_at":"Sun Sep 20 16:40:37 +0000 2015","id":645638705387032576,"id_str":"645638705387032576","text":"@wall_hacks animated? http:\/\/t.co\/2ZZPLm0TLY","source":"\\u003ca href=\\"http:\/\/twitter.com\\" rel=\\"nofollow\\"\\u003eTwitter Web Client\\u003c\/a\\u003e","truncated":false,"in_reply_to_status_id":null,"in_reply_to_status_id_str":null,"in_reply_to_user_id":3714000255,"in_reply_to_user_id_str":"3714000255","in_reply_to_screen_name":"wall_hacks","user":{"id":3719342489,"id_str":"3719342489","name":"Wallh ackertest","screen_name":"wall_hacks_test","location":"","url":null,"description":null,"protected":false,"verified":false,"followers_count":0,"friends_count":1,"listed_count":0,"favourites_count":0,"statuses_count":4,"created_at":"Sun Sep 20 16:27:56 +0000 2015","utc_offset":null,"time_zone":null,"geo_enabled":false,"lang":"en","contributors_enabled":false,"is_translator":false,"profile_background_color":"C0DEED","profile_background_image_url":"http:\/\/abs.twimg.com\/images\/themes\/theme1\/bg.png","profile_background_image_url_https":"https:\/\/abs.twimg.com\/images\/themes\/theme1\/bg.png","profile_background_tile":false,"profile_link_color":"0084B4","profile_sidebar_border_color":"C0DEED","profile_sidebar_fill_color":"DDEEF6","profile_text_color":"333333","profile_use_background_image":true,"profile_image_url":"http:\/\/abs.twimg.com\/sticky\/default_profile_images\/default_profile_2_normal.png","profile_image_url_https":"https:\/\/abs.twimg.com\/sticky\/default_profile_images\/default_profile_2_normal.png","default_profile":true,"default_profile_image":true,"following":null,"follow_request_sent":null,"notifications":null},"geo":null,"coordinates":null,"place":null,"contributors":null,"retweet_count":0,"favorite_count":0,"entities":{"hashtags":[],"trends":[],"urls":[],"user_mentions":[{"screen_name":"wall_hacks","name":"Wall Hackerton","id":3714000255,"id_str":"3714000255","indices":[0,11]}],"symbols":[],"media":[{"id":645638703164035073,"id_str":"645638703164035073","indices":[22,44],"media_url":"http:\/\/pbs.twimg.com\/tweet_video_thumb\/CPXE-tNWEAErO6B.png","media_url_https":"https:\/\/pbs.twimg.com\/tweet_video_thumb\/CPXE-tNWEAErO6B.png","url":"http:\/\/t.co\/2ZZPLm0TLY","display_url":"pic.twitter.com\/2ZZPLm0TLY","expanded_url":"http:\/\/twitter.com\/wall_hacks_test\/status\/645638705387032576\/photo\/1","type":"photo","sizes":{"small":{"w":340,"h":340,"resize":"fit"},"medium":{"w":400,"h":400,"resize":"fit"},"thumb":{"w":150,"h":150,"resize":"crop"},"large":{"w":400,"h":400,"resize":"fit"}}}]},"extended_entities":{"media":[{"id":645638703164035073,"id_str":"645638703164035073","indices":[22,44],"media_url":"http:\/\/pbs.twimg.com\/tweet_video_thumb\/CPXE-tNWEAErO6B.png","media_url_https":"https:\/\/pbs.twimg.com\/tweet_video_thumb\/CPXE-tNWEAErO6B.png","url":"http:\/\/t.co\/2ZZPLm0TLY","display_url":"pic.twitter.com\/2ZZPLm0TLY","expanded_url":"http:\/\/twitter.com\/wall_hacks_test\/status\/645638705387032576\/photo\/1","type":"animated_gif","sizes":{"small":{"w":340,"h":340,"resize":"fit"},"medium":{"w":400,"h":400,"resize":"fit"},"thumb":{"w":150,"h":150,"resize":"crop"},"large":{"w":400,"h":400,"resize":"fit"}},"video_info":{"aspect_ratio":[1,1],"variants":[{"bitrate":0,"content_type":"video\/mp4","url":"https:\/\/pbs.twimg.com\/tweet_video\/CPXE-tNWEAErO6B.mp4"}]}}]},"favorited":false,"retweeted":false,"possibly_sensitive":false,"filter_level":"low","lang":"en","timestamp_ms":"1442767237408"}''')

    listener.on_data('''{"created_at":"Sun Sep 20 16:39:25 +0000 2015","id":645638402528931841,"id_str":"645638402528931841","text":"@wall_hacks Nyan Nyan Nyan http:\/\/t.co\/loeqnUmpDw","source":"\\u003ca href=\\"http:\/\/twitter.com\\" rel=\\"nofollow\\"\\u003eTwitter Web Client\\u003c\/a\\u003e","truncated":false,"in_reply_to_status_id":null,"in_reply_to_status_id_str":null,"in_reply_to_user_id":3714000255,"in_reply_to_user_id_str":"3714000255","in_reply_to_screen_name":"wall_hacks","user":{"id":3719342489,"id_str":"3719342489","name":"Wallh ackertest","screen_name":"wall_hacks_test","location":"","url":null,"description":null,"protected":false,"verified":false,"followers_count":0,"friends_count":1,"listed_count":0,"favourites_count":0,"statuses_count":3,"created_at":"Sun Sep 20 16:27:56 +0000 2015","utc_offset":null,"time_zone":null,"geo_enabled":false,"lang":"en","contributors_enabled":false,"is_translator":false,"profile_background_color":"C0DEED","profile_background_image_url":"http:\/\/abs.twimg.com\/images\/themes\/theme1\/bg.png","profile_background_image_url_https":"https:\/\/abs.twimg.com\/images\/themes\/theme1\/bg.png","profile_background_tile":false,"profile_link_color":"0084B4","profile_sidebar_border_color":"C0DEED","profile_sidebar_fill_color":"DDEEF6","profile_text_color":"333333","profile_use_background_image":true,"profile_image_url":"http:\/\/abs.twimg.com\/sticky\/default_profile_images\/default_profile_2_normal.png","profile_image_url_https":"https:\/\/abs.twimg.com\/sticky\/default_profile_images\/default_profile_2_normal.png","default_profile":true,"default_profile_image":true,"following":null,"follow_request_sent":null,"notifications":null},"geo":null,"coordinates":null,"place":null,"contributors":null,"retweet_count":0,"favorite_count":0,"entities":{"hashtags":[],"trends":[],"urls":[],"user_mentions":[{"screen_name":"wall_hacks","name":"Wall Hackerton","id":3714000255,"id_str":"3714000255","indices":[0,11]}],"symbols":[],"media":[{"id":645638401186791428,"id_str":"645638401186791428","indices":[27,49],"media_url":"http:\/\/pbs.twimg.com\/media\/CPXEtIQXAAQJ6YH.png","media_url_https":"https:\/\/pbs.twimg.com\/media\/CPXEtIQXAAQJ6YH.png","url":"http:\/\/t.co\/loeqnUmpDw","display_url":"pic.twitter.com\/loeqnUmpDw","expanded_url":"http:\/\/twitter.com\/wall_hacks_test\/status\/645638402528931841\/photo\/1","type":"photo","sizes":{"thumb":{"w":150,"h":150,"resize":"crop"},"large":{"w":250,"h":250,"resize":"fit"},"small":{"w":250,"h":250,"resize":"fit"},"medium":{"w":250,"h":250,"resize":"fit"}}}]},"extended_entities":{"media":[{"id":645638401186791428,"id_str":"645638401186791428","indices":[27,49],"media_url":"http:\/\/pbs.twimg.com\/media\/CPXEtIQXAAQJ6YH.png","media_url_https":"https:\/\/pbs.twimg.com\/media\/CPXEtIQXAAQJ6YH.png","url":"http:\/\/t.co\/loeqnUmpDw","display_url":"pic.twitter.com\/loeqnUmpDw","expanded_url":"http:\/\/twitter.com\/wall_hacks_test\/status\/645638402528931841\/photo\/1","type":"photo","sizes":{"thumb":{"w":150,"h":150,"resize":"crop"},"large":{"w":250,"h":250,"resize":"fit"},"small":{"w":250,"h":250,"resize":"fit"},"medium":{"w":250,"h":250,"resize":"fit"}}}]},"favorited":false,"retweeted":false,"possibly_sensitive":false,"filter_level":"low","lang":"in","timestamp_ms":"1442767165201"}''')
