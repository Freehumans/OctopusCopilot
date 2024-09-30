import asyncio

from domain.lookup.octopus_multi_lookup import lookup_space_level_resources
from infrastructure.octolint import run_octolint_check_async


def octolint_unused_projects_wrapper(callback, logging):
    def octolint_unused_projects(space=None, **kwargs):
        """
        Checks for unused projects in the space. Example prompts include:
        * Check for unused projects in the space "MySpace".
        * Find unused projects in the space "MySpace".

        Args:
        space: The name of the space to run the check in.
        """

        for key, value in kwargs.items():
            if logging:
                logging(f"Unexpected Key: {key}", "Value: {value}")

        return callback(space)

    return octolint_unused_projects
