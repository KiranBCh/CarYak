from twisted.python.failure import Failure as TwistedFailure


class CaptchaFailure(Exception):
    def __init__(self, message: str):
        super().__init__(
            f'Failed to solve the captcha. Error message: {message}')


class UnknownDealer(Exception):
    def __init__(self):
        super().__init__('The offer was accepted by an unknown dealer and the engine is unaware on how to make offers with them.')


class AccountNeeded(Exception):
    def __init__(self):
        super().__init__('You need an account to get this offer.')


class ProxyBlocked(Exception):
    def __init__(self):
        super().__init__('Proxy is blocked by the server.')


class InvalidContactInfo(Exception):
    def __init__(self):
        super().__init__('The contact information given was deemed as invalid.')


class ContactInfoInUse(Exception):
    def __init__(self):
        super().__init__('The contact information given was already used for other offers and can\'t be reused.')


class AutoCheckFailed(Exception):
    def __init__(self):
        super().__init__('Failed to retrieve AutoCheck data.')


class UnencounteredResponse(Exception):
    def __init__(self, error_code: int):
        super().__init__('The response received has not been encounted before and the engine does not know how to handle it.')

        self.error_code = error_code


class VinNotFound(Exception):
    def __init__(self):
        super().__init__('We couldn\'t find that VIN.')


class CantMakeOfferForVin(Exception):
    def __init__(self, needs_to_see_vehicle):
        super().__init__('An offer couldn\'t be made for that vin.')

        self.needs_to_see_vehicle = needs_to_see_vehicle


class OfferUnderReview(Exception):
    def __init__(self):
        super().__init__('The offer is being put under review and can\' be completed currently.')


class OfferAlreadyExists(Exception):
    def __init__(self):
        super().__init__('An offer already exists for this VIN.')


class MaxAttemptsReached(Exception):
    def __init__(self):
        super().__init__('Max attempts reached.')


class ScrapingTimeout(Exception):
    def __init__(self, url: str):
        super().__init__(f'Timeout on {url}')


class TwistedDNSLookupError(Exception):
    def __init__(self, url: str):
        super().__init__(f'DNS lookup error on {url}')


class TwistedTunnelError(Exception):
    def __init__(self):
        super().__init__(f'Couldn\'t connect to proxy.')


class GenericTwistedError(Exception):
    def __init__(self, failure: TwistedFailure):
        super().__init__(failure)
