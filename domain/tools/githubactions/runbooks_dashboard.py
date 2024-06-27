from domain.defaults.defaults import get_default_argument
from domain.lookup.octopus_lookups import lookup_projects, lookup_runbooks
from domain.response.copilot_response import CopilotResponse
from domain.sanitizers.sanitized_list import sanitize_name_fuzzy, sanitize_space
from domain.tools.debug import get_params_message
from domain.view.markdown.markdown_dashboards import get_runbook_dashboard_response
from infrastructure.octopus import get_spaces_generator, get_space_id_and_name_from_name, get_runbooks_dashboard, \
    get_project, get_tenant, get_runbook_fuzzy


def get_runbook_dashboard_callback(github_user):
    def get_runbook_dashboard_implementation(original_query, api_key, url, space_name, project_name,
                                             runbook_name):
        debug_text = get_params_message(github_user, True,
                                        get_runbook_dashboard_implementation.__name__,
                                        original_query=original_query,
                                        space_name=space_name,
                                        project_name=project_name,
                                        runbook_name=runbook_name)

        sanitized_space = sanitize_name_fuzzy(lambda: get_spaces_generator(api_key, url),
                                              sanitize_space(original_query, space_name))

        space_name = get_default_argument(github_user,
                                          sanitized_space["matched"] if sanitized_space else None, "Space")

        warnings = []

        if not space_name:
            space_name = next(get_spaces_generator(api_key, url), {"Name": "Default"}).get("Name")
            warnings.append(f"The query did not specify a space so the so the space named {space_name} was assumed.")

        space_id, actual_space_name = get_space_id_and_name_from_name(space_name, api_key, url)

        sanitized_project_names, sanitized_projects = lookup_projects(url, api_key, github_user, original_query,
                                                                      space_id, project_name)

        if not sanitized_project_names:
            return CopilotResponse("Please specify a project name in the query.")

        project = get_project(space_id, sanitized_project_names[0], api_key, url)

        sanitized_runbook_names = lookup_runbooks(url, api_key, github_user, original_query, space_id, project["Id"],
                                                  runbook_name)

        if not sanitized_runbook_names:
            return CopilotResponse("Please specify a runbook name in the query.")

        runbook = get_runbook_fuzzy(space_id, project['Id'], sanitized_runbook_names[0], api_key, url)

        debug_text.extend(get_params_message(github_user, False,
                                             get_runbook_dashboard_implementation.__name__,
                                             original_query=original_query,
                                             space_name=space_name,
                                             project_name=sanitized_project_names[0],
                                             runbook_name=sanitized_runbook_names[0]))

        dashboard = get_runbooks_dashboard(space_id, runbook['Id'], api_key, url)
        response = [get_runbook_dashboard_response(project, runbook, dashboard,
                                                   lambda x: get_tenant(space_id, x, api_key, url)["Name"])]

        response.extend(warnings)
        response.extend(debug_text)

        return CopilotResponse("\n\n".join(response))

    return get_runbook_dashboard_implementation
