from flask_restful import Resource


class TemplateAPI(Resource):
    allowed_types = ['exploratory', 'computational']

    def get(self, type):
        if type not in self.allowed_types:
            return {"code": 0, "message": "string"}, 400
        return {}, 200
