from datetime import datetime, timedelta, timezone
import snscrape.modules.twitter as scrape
import pytz
import re


def getTweets(user, amount):
    # getTweets('AzurLane_EN', 25)
    tweets = []
    for i, t in enumerate(scrape.TwitterSearchScraper('from:' + user).get_items()):
        if i > amount:
            break
        if t.media:
            tweets.append([t.date, t.sourceLabel, t.rawContent, t.url, t.media])
        else:
            tweets.append([t.date, t.sourceLabel, t.rawContent, t.url, 'None'])
    return tweets


def getStatus(tweets):
    start = "We will start maintenance on"
    start2 = "Part 1"
    during = "Here's a 1-hour advance notification for the coming maintenance period"
    extend = "will need to extend the maintenance period"
    end = "Maintenance has ended"

    for tweet in tweets:
        if end in tweet[2]:
            return ["No maintenance", tweet[3]]

        elif extend in tweet[2]:
            '''
            maintenance_length: number of hours maintenance is extended by
            maintenance new end time: extended maintenance tweet post time + extra maintenance_length
            Remaining maintenance time: new end time - time.now()
            '''
            maintenance_length = int(re.findall(r'\d', re.search("approximately [0-9] hour", tweet[2]).group())[0])
            seconds = (timedelta(hours=maintenance_length) + tweet[0] - datetime.now(
                timezone.utc).astimezone()).total_seconds()
            hours = int(seconds / 3600)
            minutes = int(seconds % 3600 / 60)
            return [f"Maintenance extended - ends in {hours:02d}:{minutes:02d}", tweet[3]]

        elif during in tweet[2] and (datetime.now(timezone.utc).astimezone() - timedelta(hours=1)) >= tweet[0]:
            '''
            maintenance length: get number of hours maintenance is said to be, add 1 hour to it
                                because the tweet is posted 1 hour before maintenance begins
            maintenance end time: tweet post time + maintenance length
            time till: subtract time.now() from the calculated maintenance end time
            '''
            maintenance_length = int(re.findall(r'\d', re.search("approximately [0-9] hour", tweet[2]).group())[0])
            end_time = tweet[0] + timedelta(hours=maintenance_length + 1)
            seconds = (end_time - datetime.now(timezone.utc).astimezone()).total_seconds()
            hours = int(seconds / 3600)
            minutes = int(seconds % 3600 / 60)
            return [f"Maintenance ends in {hours:02d}:{minutes:02d}", tweet[3]]

        elif start in tweet[2]:
            '''
            date: the date in the maintenance announcement tweets are posted in this format: %m/%d
            timezone: US Pacific Time
            maintenance date: create the date of maintenance from the given date, the time: 00:00:00, and timezone
            time till: convert to utc and subtract the current time from maintenance start time
            '''
            date = tweet[2].split()[7].split('/')
            tz = pytz.timezone("America/Los_Angeles")
            maintenance_date = tz.localize(
                datetime.strptime(f"{tweet[0].year}-{date[0]}-{date[1]} 00:00:00", "%Y-%m-%d %H:%M:%S"))
            utcDate = maintenance_date.astimezone(pytz.utc)
            seconds = (utcDate - datetime.now(timezone.utc).astimezone()).total_seconds()
            hours = int(seconds / 3600)
            minutes = int(seconds % 3600 / 60)
            return [f"Maintenance starts in {hours:02d}:{minutes:02d}", tweet[3]]

        # elif start2 in tweet[2]:
        #     url = tweet[4][1].fullUrl
        #     request_site = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        #     img_from_url = urllib.request.urlopen(request_site)
        #     img = Image.open(img_from_url)
        #     result = pytesseract.image_to_string(img, config='-l eng')
        #
        #     return ['Media:', tweet[3]]

        # else:
        #     return ["No maintenance", "https://twitter.com/AzurLane_EN"]
