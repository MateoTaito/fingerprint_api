class FingerprintEnrollmentError(Exception):
    pass

class FingerprintVerificationError(Exception):
    pass

class FingerprintNotFoundError(Exception):
    pass

class UserNotFoundError(Exception):
    pass

class InvalidFingerprintDataError(Exception):
    pass