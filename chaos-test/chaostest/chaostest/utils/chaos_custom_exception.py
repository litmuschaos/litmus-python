__author__ = 'Vijay_Thomas@intuit.com'


class ChaosTestException(Exception):

    def __init__(self, message):
        self.message = message
        super(ChaosTestException, self).__init__(self.message)

    def __str__(self):
        return "Chaos test exception=" + self.message
