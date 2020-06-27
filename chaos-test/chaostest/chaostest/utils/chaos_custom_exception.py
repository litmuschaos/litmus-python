
class ChaosTestException(Exception):

    def __init__(self, message, error):
        self.message = message
        self.error = error
        super(ChaosTestException, self).__init__(self.message)

    def __str__(self):
        return "Chaos test exception==" + self.message
