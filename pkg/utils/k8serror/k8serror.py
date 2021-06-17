

class K8serror(object):
    def __init__(self, err=None):
        self.err = err

    def IsNotFound(self, err):
        if err.reason == "Not Found":
            return True
        else:
            return False

    def IsAlreadyExists(self, err):
        if err.reason == "Conflict":
            return True
        else:
            return False