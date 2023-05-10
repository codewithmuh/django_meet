import copy
import json

from rest_framework.renderers import JSONRenderer


class ApiRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        status_code = renderer_context['response'].status_code
        response = copy.deepcopy(data)

        if not str(status_code).startswith('2'):
            try:
                if isinstance(data, list):
                    data = data[0]
                keys = data.keys()
                response = {}
                for key in keys:
                    if isinstance(data.get(key), list):
                        response["message"] = data.get(key)[0]
                    elif isinstance(data.get(key), str):
                        response["message"] = data.get(key)
                    else:
                        response[key] = data.get(key)
            except Exception as e:
                print(e)
                response["message"] = None

        return super(ApiRenderer, self).render(response, accepted_media_type, renderer_context)
