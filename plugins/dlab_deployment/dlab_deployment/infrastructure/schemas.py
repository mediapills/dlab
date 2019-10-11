CREATE_PROJECT_SCHEMA = {
    'project': {
        'type': 'object',
        'properties': {
            'name': {'type': 'string'},
            'key': {'type': 'string'},
            'useSharedImages': {'type': 'string'},
            'tag': {'type': 'string'},
            'userTag': {'type': 'string'},
            'customTag': {'type': 'string'},
            'keyName': {'type': 'string'},
        }
    },
    'cloudProperties': {
        'type': 'object',
        'properties': {
            'os': {'type': 'string'},
            'sbn': {'type': 'string'},
            'subnetId': {'type': 'string'},
            'vpcId': {'type': 'string'},
            'region': {'type': 'string'},
            'zone': {'type': 'string'},
            'securityGroupIds': {'type': 'string'},
            'confTagResourceId': {'type': 'string'},
        }
    },
    'required': ['project', 'cloudProperties']
}
