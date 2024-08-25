def deploy_release_wrapper(query, callback, logging):
    def deploy_release(space_name=None, project_name=None, release_version=None, environment_name=None,
                       tenant_name=None, **kwargs):
        """Responds to queries like: Deploy release version "1.4.1" of project "Deploy ECS Container" in the space
           "Default" to the "Development" environment, or Deploy release version "2.0.8" of project "WebApp" in the
           space "Mark Harrison" to the environment "Test" for tenant "Contoso"

        Args:
        space_name: The name of the space
        project_name: The name of the project
        release_version: The release version
        environment_name: The name of the environment to deploy to.
        tenant_name: The (optional) name of the tenant to deploy to.
        """

        if logging:
            logging("Enter:", "deploy_release")

        for key, value in kwargs.items():
            if logging:
                logging(f"Unexpected Key: {key}", "Value: {value}")

        # This is just a passthrough to the original callback
        return callback(query,
                        space_name,
                        project_name,
                        release_version,
                        environment_name,
                        tenant_name)

    return deploy_release