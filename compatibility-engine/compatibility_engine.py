import typer
from typing import Optional
from api_conflict import find_api_conflicts_semantic

app = typer.Typer(help="Microservices Compatibility Analysis Engine")

def run_api_conflict(repos_dir: str, output: Optional[str] = None):
    find_api_conflicts_semantic(repos_dir, output)

def run_dependency_conflict(repos_dir: str):
    typer.echo(f"[dependency-conflict] Analyzing dependency version conflicts in {repos_dir} (placeholder)")

def run_springboot_version(repos_dir: str):
    typer.echo(f"[springboot-version] Checking Spring Boot version compatibility in {repos_dir} (placeholder)")

def run_scoring(repos_dir: str):
    typer.echo(f"[scoring] Calculating compatibility scores in {repos_dir} (placeholder)")

def run_report(repos_dir: str, output: str = "report.json"):
    typer.echo(f"[report] Generating compatibility report for {repos_dir} to {output} (placeholder)")

@app.command()
def api_conflict(
    repos_dir: str = typer.Argument(..., help="Directory containing analyzed microservice repos"),
    output: Optional[str] = typer.Option(None, help="Output file for the API conflict results (JSON)")
):
    run_api_conflict(repos_dir, output)

@app.command()
def dependency_conflict(repos_dir: str = typer.Argument(..., help="Directory containing analyzed microservice repos")):
    run_dependency_conflict(repos_dir)

@app.command()
def springboot_version(repos_dir: str = typer.Argument(..., help="Directory containing analyzed microservice repos")):
    run_springboot_version(repos_dir)

@app.command()
def scoring(repos_dir: str = typer.Argument(..., help="Directory containing analyzed microservice repos")):
    run_scoring(repos_dir)

@app.command()
def report(
    repos_dir: str = typer.Argument(..., help="Directory containing analyzed microservice repos"),
    output: str = typer.Option("report.json", help="Output file for the report")
):
    run_report(repos_dir, output)

if __name__ == "__main__":
    app()
