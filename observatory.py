import requests
from checks import AgentCheck
from dateutil import parser


class ObservatoryCheck(AgentCheck):
    @staticmethod
    def compose_tags(api_response, hostname):
        tags = []

        interesting_keys = [
            'scan_id',
            'grade',
            'likelihood_indicator'
        ]

        for key in interesting_keys:
            tags.append('%s:%s' % (key, api_response[key]))

        tags.append('hostname:%s' % hostname)

        return tags

    @staticmethod
    def grade_to_dec(grade):
        grade_map = {
            'A+': 12,
            'A': 11,
            'A-': 10,
            'B+': 9,
            'B': 8,
            'B-': 7,
            'C+': 6,
            'C': 5,
            'C-': 4,
            'D+': 3,
            'D': 2,
            'D-': 1,
            'F': 0
        }
        return grade_map[grade] if grade in grade_map else 0

    @staticmethod
    def is_scan_ready(response):
        return 'state' in response and response['state'] == "FINISHED"

    def check(self, instance):

        if 'host' not in instance:
            self.log.error('Skipping instance, no host found.')
            return

        host = instance['host']

        default_timeout = self.init_config.get('default_timeout', 5)
        timeout = float(instance.get('timeout', default_timeout))
        instance_tags = instance.get('tags', [])
        is_hidden = instance.get('hidden', False)
        api_url = instance.get('api_url', 'https://http-observatory.security.mozilla.org/api/v1')

        response = self.scan(api_url=api_url, host=host, timeout=timeout, hidden=is_hidden)

        if not self.is_scan_ready(response):
            self.log.info('Observatory scan of %s is not finished yet, '
                          'skipping reporting until it is complete.' % host)
            return

        tags = self.compose_tags(response, host) + instance_tags
        self.report_metrics(response, tags)
        self.log.info('Host %s Observatory score is %s' % (host, response['grade']))

    def report_metrics(self, response, tags):
        keys = [
            'tests_quantity',
            'tests_passed',
            'tests_failed',
            'score'
        ]

        for key in keys:
            self.gauge('mozilla.observatory.http.%s' % key, response[key], tags=tags)

        self.gauge('mozilla.observatory.http.grade', self.grade_to_dec(response['grade']), tags=tags)
        self.gauge('mozilla.observatory.http.score', response['score'], tags=tags)
        duration = self.get_scan_duration(response['start_time'], response['end_time'])
        self.gauge('mozilla.observatory.http.scan_duration', duration, tags=tags)

    @staticmethod
    def get_scan_duration(start, end):
        start = parser.parse(start)
        end = parser.parse(end)
        duration = end - start
        return duration.total_seconds()

    def scan(self, api_url, host, timeout, hidden=False):
        url = "%s/analyze" % api_url
        r = requests.post(url, params={'host': host, hidden: hidden}, timeout=timeout)
        if r.status_code != 200:
            self.log.error('URL %s responded with status code %s, unable to continue.' % (url, r.status_code))
            return
        json = r.json()
        return json


if __name__ == '__main__':
    check, instances = ObservatoryCheck.from_yaml('/etc/dd-agent/conf.d/observatory.yaml')
    for instance in instances:
        print "\nRunning the check against host: %s" % (instance['host'])
        check.check(instance)
        if check.has_events():
            print 'Events: %s' % (check.get_events())
        print 'Metrics: %s' % (check.get_metrics())
