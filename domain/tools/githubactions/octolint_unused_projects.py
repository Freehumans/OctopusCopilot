import asyncio

from domain.lookup.octopus_multi_lookup import lookup_space_level_resources
from domain.response.copilot_response import CopilotResponse
from domain.tools.debug import get_params_message
from infrastructure.octolint import run_octolint_check_async


def octolint_callback(octopus_details, github_user, original_query, check_name):
    def octolint(space):
        """
        This is a generic function that can call any Octolint check.
        :param space: The name of the space to run the check in.
        """

        async def inner_function():
            debug_text = get_params_message(
                github_user,
                True,
                octolint_callback.__name__,
                space=space,
            )

            api_key, url = octopus_details()

            space_resources = lookup_space_level_resources(
                url,
                api_key,
                github_user,
                original_query,
                space,
            )

            if not space_resources["space_id"]:
                return CopilotResponse(
                    "The name of the space to run the check in must be defined."
                )

            debug_text.extend(
                get_params_message(
                    github_user,
                    False,
                    octolint_callback.__name__,
                    space=space_resources["space_name"],
                )
            )

            results = await run_octolint_check_async(
                api_key, url, space_resources["space_id"], check_name
            )

            # The plain text response needs to be tweaked slightly to support markdown
            results = results.replace("\n", "\n\n")

            wiki_page = f"Read the [documentation](https://github.com/OctopusSolutionsEngineering/OctopusRecommendationEngine/wiki/{check_name}) for more information on these results and practical next steps."

            results = [results, wiki_page]
            results.extend(debug_text)

            return CopilotResponse("\n\n".join(results))

        return asyncio.run(inner_function())

    return octolint