def generate_service_structure_mermaid(service_summaries):
    """
    Generate a Mermaid diagram (graph TD) showing services, their APIs, and dependencies.
    """
    lines = ["graph TD;"]
    for service in service_summaries:
        sname = service["name"]
        lines.append(f'  {sname}(["{sname}"])')
        for api in service.get("api", []):
            api_id = f'{sname}_{api}'.replace("/", "_").replace(".", "_")
            lines.append(f'  {sname} --> {api_id}(["API: {api}"])')
        for dep in service.get("dependencies", []):
            dep_id = dep.get("name", "dep").replace(":", "_").replace(".", "_")
            lines.append(f'  {sname} --> {dep_id}(["Dep: {dep.get('name', '')}"])')
    return "\n".join(lines)

def write_mermaid_to_markdown(mermaid_str, filename="consolidation_progress.md"):
    with open(filename, "w") as f:
        f.write("# Consolidation Progress\n\n")
        f.write("```mermaid\n")
        f.write(mermaid_str)
        f.write("\n```") 