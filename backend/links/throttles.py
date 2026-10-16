from rest_framework.throttling import SimpleRateThrottle


class CreateLinkThrottle(SimpleRateThrottle):
    scope = 'create'

    def get_cache_key(self, request, view):
        return self.cache_format % {'scope': self.scope, 'ident': self.get_ident(request)}


class StatisticsThrottle(CreateLinkThrottle):
    scope = 'stats'
