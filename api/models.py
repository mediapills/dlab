import json
from datetime import datetime


class BaseModel(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    @property
    def date(self):
        return datetime.now()


class DlabModel(BaseModel):
    def __init__(self, **kwargs):
        if 'request' in kwargs and isinstance(kwargs['request'], dict):
            kwargs['request'] = json.dumps(kwargs['request'])

        super(DlabModel, self).__init__(**kwargs)
        self.updated = self.date
        if 'id' not in kwargs:
            self.created = self.updated


class FIFOModel(BaseModel):
    pass
