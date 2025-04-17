import typer
from rich.console import Console

from cupboard.utils import parse_hosts_file, validate_ip, online_sanity_check, write_host_to_hosts_file

console = Console()
verbose = True
open_ports = []

app = typer.Typer()

@app.command()
def inithost(boxname: str, ip_address: str):
    initial_hostname = boxname.lower() + ".htb"
    is_valid = validate_ip(ip_address)
    if not is_valid:
        console.print(f"[red]Invalid IP[/red]: [bold cyan]{ip_address}[/]")
    else:
        console.print(f"[bold green]Valid IP[/]: [bold cyan]{ip_address}[/]")
    sanity_check_results = []
    console.print("[bold cyan][underline]Port Sanity Check[/bold cyan][/underline]:")
    for item in online_sanity_check(ip_address):
        sanity_check_results.append(item[1])
        if item[1]:
            open_ports.append(item[0])

        console.print(f"[bold yellow]{item[0]}[/] => {'[bold green]Open' if item[1] else '[bold red]Closed'}[/]")

    if any(sanity_check_results):
        host_status_string = "[green]online[/green]"
    else:
        host_status_string = "[red]offline[/red]"
    console.print(f"Host [bold cyan]{initial_hostname}[/] appears {host_status_string}.")
    console.print(f"Opened ports: [bold yellow]{', '.join([str(port) for port in open_ports])}[/]")
    hosts_file_contents = parse_hosts_file()

    for key in hosts_file_contents.keys():
        if key == ip_address:
            already_in_file = True
            break
        already_in_file = False

    if already_in_file:
        console.print(
            f"{ip_address} already in [bold yellow]/etc/hosts[/] with name(s): [bold cyan]{','.join(hosts_file_contents[key])}[/]")
    else:
        write_host_to_hosts_file(ip_address, initial_hostname)
        console.print(f"Added [bold cyan]{ip_address}[/] to [bold yellow]/etc/hosts[/] with name: [bold cyan]{initial_hostname}[/]")

@app.command()
def webmap():
    pass

if __name__ == "__main__":
    app()