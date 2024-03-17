import json
import os
import unittest

import azure.functions as func
from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_for_logs

from function_app import copilot_handler_internal
from infrastructure.users import save_users_octopus_url_from_login, save_default_values
from tests.infrastructure.octopus_config import Octopus_Api_Key, Octopus_Url
from tests.infrastructure.octopus_infrastructure_test import run_terraform


class CopilotChatTest(unittest.TestCase):
    """
    This test simulates the complete copilot workflow, excluding an Oauth login.
    """

    @classmethod
    def setUpClass(cls):
        # Simulate the result of a user login and saving their Octopus details
        try:
            save_users_octopus_url_from_login(os.environ["TEST_GH_USER"],
                                              Octopus_Url,
                                              Octopus_Api_Key,
                                              os.environ["ENCRYPTION_PASSWORD"],
                                              os.environ["ENCRYPTION_SALT"],
                                              os.environ["AzureWebJobsStorage"])
            save_default_values(os.environ["TEST_GH_USER"],
                                "space",
                                "Simple",
                                os.environ["AzureWebJobsStorage"])
            save_default_values(os.environ["TEST_GH_USER"],
                                "project",
                                "Project1",
                                os.environ["AzureWebJobsStorage"])
        except Exception as e:
            print(
                "Run Azureite with: "
                + "docker run -d -p 10000:10000 -p 10001:10001 -p 10002:10002 mcr.microsoft.com/azure-storage/azurite")
            return

        cls.mssql = DockerContainer("mcr.microsoft.com/mssql/server:2022-latest").with_env(
            "ACCEPT_EULA", "True").with_env("SA_PASSWORD", "Password01!")
        cls.mssql.start()
        wait_for_logs(cls.mssql, "SQL Server is now ready for client connections")

        mssql_ip = cls.mssql.get_docker_client().bridge_ip(cls.mssql.get_wrapped_container().id)

        cls.octopus = DockerContainer("octopusdeploy/octopusdeploy").with_bind_ports(8080, 8080).with_env(
            "ACCEPT_EULA", "Y").with_env("DB_CONNECTION_STRING",
                                         "Server=" + mssql_ip + ",1433;Database=OctopusDeploy;User=sa;Password=Password01!").with_env(
            "ADMIN_API_KEY", Octopus_Api_Key).with_env("DISABLE_DIND", "Y").with_env(
            "ADMIN_USERNAME", "admin").with_env("ADMIN_PASSWORD", "Password01!").with_env(
            "OCTOPUS_SERVER_BASE64_LICENSE", os.environ["LICENSE"])
        cls.octopus.start()
        wait_for_logs(cls.octopus, "Web server is ready to process requests")

        output = run_terraform("../terraform/simple/space_creation", Octopus_Url, Octopus_Api_Key)
        run_terraform("../terraform/simple/space_population", Octopus_Url, Octopus_Api_Key,
                      json.loads(output)["octopus_space_id"]["value"])
        run_terraform("../terraform/empty/space_creation", Octopus_Url, Octopus_Api_Key)

    @classmethod
    def tearDownClass(cls):
        try:
            cls.octopus.stop()
        except Exception as e:
            pass

        try:
            cls.mssql.stop()
        except Exception as e:
            pass

    def test_chat_request(self):
        prompt = "List the variables defined in the project \"Project1\" in space \"Simple\"."
        req = func.HttpRequest(
            method='POST',
            body=json.dumps({
                "messages": [
                    {
                        "content": prompt
                    }
                ]
            }).encode('utf8'),
            url='/api/form_handler',
            params=None,
            headers={
                "X-GitHub-Token": os.environ["GH_TEST_TOKEN"]
            })

        response = copilot_handler_internal(req)
        response_text = response.get_body().decode('utf8')

        self.assertTrue("Test.Variable" in response_text)


if __name__ == '__main__':
    unittest.main()