from dlab_core.infrastructure.controllers import BaseCLIController


class BaseDeploymentCLIController(BaseCLIController):
    @staticmethod
    def deploy_ssn():
        raise NotImplementedError

    @staticmethod
    def destroy_ssn():
        raise NotImplementedError

    @classmethod
    def deploy_endpoint(cls):
        raise NotImplementedError

    @classmethod
    def destroy_endpoint(cls):
        raise NotImplementedError
