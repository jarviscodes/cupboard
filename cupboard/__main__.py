import requests
import typer
from rich.console import Console
from bs4 import BeautifulSoup
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

    console.print("[bold cyan][underline]Hosts file check[/bold cyan][/underline]:")
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

def passive_crawl(host):
    with requests.Session() as session:
        resp_robot = session.get("http://" + host + "/robots.txt")
        resp_git = session.get("http://" + host + "/.git")
        resp_webpage = session.get(host)

    if resp_robot.status_code == 200:
        console.print("Found Robots.txt: ")
        console.print(resp_robot.text)
    if resp_git.status_code == 200:
        console.print("Found .git directory, dump this with gitdumper!")

    webpage_text = resp_webpage.text
    webpage_soup = BeautifulSoup(webpage_text, "html.parser")
    if webpage_soup:
        all_links = webpage_soup.find_all("a")
        for link in all_links:
            console.print(link.get("href"))



@app.command()
def webmap(port: int, vhost:str, subdomain_enum: bool, directory_enum: bool):
    console.print("Info from passive crawling...")
    passive_crawl(f"{vhost}:{port}")


if __name__ == "__main__":
    app()