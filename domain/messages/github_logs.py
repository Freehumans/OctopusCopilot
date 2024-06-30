def build_github_logs_prompt(few_shot=None):
    """
    Build a message prompt for the LLM that instructs it to parse github workflow run logs
    :param few_shot: Additional user messages providing a few shot example.
    :return: The messages to pass to the llm.
    """

    if few_shot is None:
        few_shot = []

    messages = [
        ("system", "You understand Octopus Deploy log output."),
        ("system", "You are a concise and helpful agent."),
        ("system", "Answer the question given the supplied deployment log output."),
        # The user can ask for the output in a markdown code block specifically, but we should also ask the agent
        # to do this by default.
        ("system", "Print any log output in a markdown code block."),
        ("system",
         "You must assume that the supplied workflow run log and all items in it directly relate to the owner, repo, and workflow from the question."),
        *few_shot,
        ("user", "Question: {input}"),
        # https://help.openai.com/en/articles/6654000-best-practices-for-prompt-engineering-with-the-openai-api
        # Put instructions at the beginning of the prompt and use ### or """ to separate the instruction and context
        ("user", "Deployment Log: ###\n{context}\n###"),
        ("user", "Answer:")]

    return messages
