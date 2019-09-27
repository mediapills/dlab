
CREATE_NOTEBOOK_SCHEMA = {
    'notebook': {
        'type': 'object',
        'properties': {
            'type': {'type': 'string'},
            'notebook_name': {'type': 'string'},
            'spark_config': {
                'type': 'object',
                'properties': {
                    'Classification': {'type': 'string'},
                    'Properties': {
                        'type': 'object',
                        'additionalProp': {'type': 'object'}
                    },
                    'Configurations': {'type': 'array'}
                }
            },
            'git_creds': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'name': {'type': 'string'},
                        'hostname': {'type': 'string'},
                        'email': {'type': 'string'},
                        'login': {'type': 'string'},
                        'password': {'type': 'string'},
                    }
                }
            },
            'project': {'type': 'string'},
            'tags': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'name': {'type': 'string'},
                        'value': {'type': 'string'},
                    }
                }
            },
        }
    },
    'cloudConfig': {
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
    'required': ['notebook', 'cloudConfig']
}


INSTALL_LIB_SCHEMA = {
    'type': 'array',
    'items': {
        'type': 'object',
        'required': ['group', 'name', 'version'],
        'properties': {
            'group': {'type': 'string'},
            'name': {'type': 'string'},
            'version': {'type': 'string'},
        }
    }
}

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
    }
}
