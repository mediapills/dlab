CREATE_PROJECT_SCHEMA = {
    'project': {
        'type': 'object',
        'properties': {
            'useSharedImages': {'type': 'bool'},
            'key': {'type': 'string'},
            'name': {'type': 'string'},
        },
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
