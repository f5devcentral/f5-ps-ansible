# -*- coding: utf-8 -*-
#
# Copyright: Simon Kowallik for the F5 DevCentral Community
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import sys
import importlib.util
import os
import yaml


def read_module_docs(module_path):
    module_dir = os.path.abspath(os.path.dirname(module_path))
    sys.path.append(os.getcwd())
    sys.path.append(os.getcwd() + "/" + module_dir)

    module_name = os.path.basename(module_path).split(".")[0]

    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    try:
        examples = module.EXAMPLES
    except AttributeError:
        examples = None

    try:
        returns = module.RETURN
    except AttributeError:
        returns = None

    return (module_name, module.DOCUMENTATION, examples, returns)


def generate_markdown(DOCUMENTATION, EXAMPLES=None, RETURNS=None):
    data = yaml.safe_load(DOCUMENTATION)

    module = data.get("module", "")
    short_description = data.get("short_description", "")
    description = data.get("description", [])
    author = data.get("author", [])
    version_added = data.get("version_added", "")
    options = data.get("options", {})
    attributes = data.get("attributes", {})
    notes = data.get("notes", [])

    markdown_doc = f"# {module}\n\n"
    markdown_doc += f"**Short Description:** {short_description}\n\n"
    markdown_doc += "**Description:**\n\n"
    for desc in description:
        markdown_doc += f"- {desc}\n"
    markdown_doc += "\n"
    markdown_doc += f"**Author:** {', '.join(author)}\n\n"
    markdown_doc += f"**Version Added:** {version_added}\n"

    markdown_doc += "\n## Options\n\n"
    markdown_doc += "| Option | Description | Required | Type | Default | Choices |\n"
    markdown_doc += "|--------|-------------|----------|------|---------|---------|\n"
    for option, details in options.items():
        description = details.get("description", "")
        required = details.get("required", "")
        type_ = f"`{details.get('type')}`" if details.get("type") else ""
        default = f"`{details.get('default')}`" if details.get("default") else ""
        choices_list = details.get("choices", [])
        choices = f"`{', '.join(choices_list)}`" if choices_list else ""
        markdown_doc += f"| {option} | {description} | {required} | {type_} | {default} | {choices} |\n"

    markdown_doc += "\n## Attributes\n\n"
    markdown_doc += "| Attribute | Support | Description |\n"
    markdown_doc += "|-----------|---------|-------------|\n"
    for attr, details in attributes.items():
        description = details.get("description", "")
        support = details.get("support", "")
        markdown_doc += f"| {attr.capitalize()} | {support} | {description} |\n"

    markdown_doc += "\n## Notes\n\n"
    for note in notes:
        markdown_doc += f"- {note}\n"

    if RETURNS is not None:
        data = yaml.safe_load(RETURNS)
        markdown_doc += "\n## Return Values\n\n"
        markdown_doc += "| Key | Description | Returned | Type | Elements |\n"
        markdown_doc += "|-----|-------------|----------|------|----------|\n"
        for key, details in data.items():
            description = details.get("description", "")
            returned = details.get("returned", "")
            type_ = f"`{details.get('type')}`" if details.get("type") else ""
            elements = f"`{details.get('elements')}`" if details.get("elements") else ""
            markdown_doc += (
                f"| {key} | {description} | {returned} | {type_} | {elements} |\n"
            )

    if EXAMPLES is not None:
        markdown_doc += "\n## Examples\n\n"
        markdown_doc += "```yaml\n"
        markdown_doc += EXAMPLES
        markdown_doc += "```"

    return markdown_doc


def main(MODULE_PATHS, MODULE_DOC_BASEPATH, DOC_TEMPLATE, raw="", endraw=""):
    counter = 100
    for module_path in MODULE_PATHS:
        module_name, docs, examples, returns = read_module_docs(module_path)
        DOCUMENTATION = generate_markdown(docs, examples, returns)
        # use doc_template to create the markdown file
        module_markdown_doc = DOC_TEMPLATE.format(
            MODULE_NAME=module_name,
            DOCUMENTATION=DOCUMENTATION,
            COUNTER=counter,
            raw=raw,
            endraw=endraw,
        )
        counter += 1

        with open(f"{MODULE_DOC_BASEPATH}/{module_name}.md", "w") as f:
            f.write(module_markdown_doc)


RELATIVE_MODULE_PATHS = [
    "./ansible_collections/f5_ps_ansible/f5os/plugins/modules/f5os_restconf_config.py",
    "./ansible_collections/f5_ps_ansible/f5os/plugins/modules/f5os_restconf_get.py",
]

MODULE_DOC_BASEPATH = "./docs/f5os/"

DOC_TEMPLATE = """---
title: {MODULE_NAME}
parent: f5_ps_ansible.f5os
nav_order: {COUNTER}
nav_enabled: true
---
{raw}

{DOCUMENTATION}

{endraw}
"""

if __name__ == "__main__":
    main(
        RELATIVE_MODULE_PATHS,
        MODULE_DOC_BASEPATH,
        DOC_TEMPLATE,
        raw="{% raw %}",
        endraw="{% endraw %}",
    )
