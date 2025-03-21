# Various utility functions for interacting with the OSM
from osmclient.client import *

def get_properties(project_code='', participant_code='', property_name=''):
    pc = OSMProjectApiClient()
    dc = OSMIoTManagmentAPIClient()

    property_definition = dc.getPropertyDefinitionByName(property_name)
    project = pc.getProjectByCode(project_code)
    participant = pc.getParticipantByCode(participant_code);
    values = pc.listParticipantPropertiesInProject(project.id, participant.id, property_definition.id, 0, 10000000)
    return values


