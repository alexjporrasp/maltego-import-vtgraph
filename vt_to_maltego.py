# Execute script along a graph ID to save Vt Graph in a format that can be
# imported by Maltego.
# Usage:
# $ python vt_to_maltego <graph_id> <csv_export_file>

from vt_api import graph_api
import random
import string
import sys

# Associates the nodes value to its generated id for Maltego.
VALUE_ID = {}

USED_ID = set()

def generate_entity_id() -> str:
    """
        Returns a string of length 13 containing lower case ascii letters and
        digits. If the generated string already exists, it creates another one.
    """
    entity_id = ''.join(
        random.choice(string.digits) for _ in range(13)
    )
    while entity_id in USED_ID:
        entity_id = ''.join(
        random.choice(string.digits) for _ in range(13)
        )
    USED_ID.add(entity_id)
    return entity_id

def get_file_node_str(entity_id: str, value: str) -> str:
    """
        Returns a string containing the lines to include in the CSV file
        for a hash node.
    """
    return (
        "maltego.Hash,Hash,Hash Type,Owner,Before,After,Included Media Types,Excluded Media Types\n"
        "EntityID,properties.hash,type,owner,before,after,includeMediaType,excludeMediaType\n"
        '{},{}," ",,,,,\n'.format(entity_id, value)
    )

def get_ip_node_str(entity_id: str, value: str) -> str:
    """
        Returns a string containing the lines to include in the CSV file
        for a ip address node.
    """
    return (
        "maltego.IPv4Address,IP Address,Internal,owner,Before,After,Include Media Type,Exclude Media Type\n"
        "EntityID,ipv4-address,ipaddress.internal,owner,Before,After,includeMediaType,excludeMediaType\n"
        "{},{},false,,,,,\n".format(entity_id, value)
    )

def get_domain_node_str(entity_id: str, value: str) -> str:
    """
        Returns a string containing the lines to include in the CSV file
        for a domain node.
    """
    return (
        "maltego.Domain,Domain Name,WHOIS Info\n"
        "EntityID,fqdn,whois-info\n"
        "{},{},\n".format(entity_id, value)
    )

# URLs value are their SHA256.
def get_url_node_str(entity_id: str, value: str) -> str:
    """
        Returns a string containing the lines to include in the CSV file
        for a url node.
    """
    response = graph_api.get_full_url(value)['data']['attributes']
    return (
        "maltego.URL,Short title,URL,Title,owner,Before,After,Include Media Type,Exclude Media Type\n"
        "EntityID,short-title,url,title,owner,Before,After,includeMediaType,excludeMediaType\n"
        "{},{},{},{},,,,,\n".format(entity_id, response['url'], response['url'], response.get('title', ''))
    )

def get_node_str(value: str, node_type: str) -> str:
    """
        Returns what is hoing to be written in the CSV file
        as a string.
    """
    if node_type in {'file', 'ip_address', 'domain', 'url'}:
        entity_id = generate_entity_id()
        VALUE_ID[value] = entity_id
    if node_type == 'file':
        return get_file_node_str(entity_id, value)
    if node_type == 'ip_address':
        return get_ip_node_str(entity_id, value)
    if node_type == 'domain':
        return get_domain_node_str(entity_id, value)
    if node_type == 'url':
        return get_url_node_str(entity_id, value)
    return ''

def get_links_str(links: dict) -> str:
    """
        Args:
            links: A dictionary containing the relations as key value pair,
            including their type, for example: 
            { 
                ('www.hooli.com', 'resolutions') : ['relationships_resolutions_wwwhoolicom'],
                ('relationships_resolutions_wwwhoolicom', 'resolutions') : ['8.8.8.8']
            }

        Returns:
            The header and the graph links in Maltego CSV format as a string.
    """
    result = (
        "Maltego Link,Source Entity ID,Target Entity ID,Label,Show Label,Color,Style,Thickness,Description\n"
        "LinkID,SourceEntityID,TargetEntityID,maltego.link.manual.type,maltego.link.show-label,maltego.link.color,maltego.link.style,maltego.link.thickness,maltego.link.manual.description\n"
    )
    for source, rel_type in links:
        # Makes sure it is not a relationship node.
        if source in VALUE_ID:
            for relationship in links[(source, rel_type)]:
                for target in links[(relationship, rel_type)]:
                    result += '{},{},{},{},1,,-1,-1,\n'.format(
                                    generate_entity_id(),
                                    VALUE_ID[source],
                                    VALUE_ID[target],
                                    rel_type
                                )
    return result

# TODO(alexporras): Include Actor, Department, Email, Victim, Device, Port, Service, SSL Cert, Wallet
if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise ValueError("Usage: \npython vt_to_maltego <graph_id> <csv_export_file>")
    api_response = graph_api.get_graph(sys.argv[1])

    if 'data' not in api_response  or 'attributes' not in api_response['data']:
        raise ValueError('No data in the graph API response.')
    
    graph = api_response['data']['attributes']
    with open(sys.argv[2], 'w+') as export_file:
        for node in graph['nodes']:
            export_file.write(get_node_str(node['entity_id'], node['type']))
            export_file.write('\n')
        
        links = {}
        for link in graph['links']:
            links[(link['source'], link['connection_type'])] = (
                links.get(
                    (link['source'], link['connection_type']),
                    []
                ) + [link['target']])
 
        export_file.write(get_links_str(links))