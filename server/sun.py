
import urllib.request
import json
import time
import datetime
import logger

sun_datas = {}

def get_sun_data(d):
    global sun_datas

    if d in sun_datas:
        return sun_datas[d]

    url = 'http://api.sunrise-sunset.org/json?lat=42.293559&lng=-83.7160317&date=%s&formatted=0' % (d)
    logger.trace(url)
    response = urllib.request.urlopen(url)
    content = response.read()
    data = json.loads(content.decode('utf8'))
    if data['status'] != 'OK':
        raise Exception('Error fetching sunrise-sunset API: %s' % (data['status']))

    sun_datas[d] = data
    return data


def is_civil_twilight(t=None):
    if t is None:
        t = time.gmtime()
    # It might be that we are still in "yesterday's" civil twilight, so we must check that
    yesterday = datetime.datetime.fromtimestamp(time.mktime(t))
    yesterday -= datetime.timedelta(days=1)
    for day in [t, yesterday.timetuple()]:
        logger.trace('checking day %s' % (str(day)))
        data = get_sun_data(time.strftime('%Y-%m-%d', day))
        begin_t = time.strptime(data['results']['civil_twilight_begin'], '%Y-%m-%dT%H:%M:%S+00:00')
        end_t = time.strptime(data['results']['civil_twilight_end'], '%Y-%m-%dT%H:%M:%S+00:00')
        logger.trace('begin_t: %s' % (str(begin_t)))
        logger.trace('end_t: %s' % (str(end_t)))
        logger.trace('t: %s' % (str(t)))
        if begin_t < t < end_t:
            return True
    return False


if __name__ == '__main__':
    #logger.setLogLevel(logger.TRACE)
    logger.info('2015-09-18 00:08:00: ' + str(is_civil_twilight(time.strptime('2015-09-18 00:08:00', '%Y-%m-%d %H:%M:%S'))))
    logger.info('2015-09-18 00:10:00: ' + str(is_civil_twilight(time.strptime('2015-09-18 00:10:00', '%Y-%m-%d %H:%M:%S'))))
    t = time.gmtime()
    logger.info('currently (%s): %s' % (time.strftime('%Y-%m-%d %H:%M:%S', t), is_civil_twilight(t)))



