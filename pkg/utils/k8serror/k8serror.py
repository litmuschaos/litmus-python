
# K8serror class is handling kubernetes errors
class K8serror(object):
    def __init__(self, err=None):
        self.err = err

    # IsNotFound returns true if the specified error was created by NewNotFound
    def IsNotFound(self, err):
        if err.reason == "Not Found": return True; return False

    # IsAlreadyExists determines if the err is an error which indicates that a specified resource already exists
    def IsAlreadyExists(self, err):
        if err.reason == "Conflict": return True; return False