class AccessLog:
    def __init__(self, timestamp, user, access_status):
        self.timestamp = timestamp
        self.user = user
        self.access_status = access_status

    def __repr__(self):
        return f"AccessLog(timestamp={self.timestamp}, user={self.user}, access_status={self.access_status})"