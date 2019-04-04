from py2cytoscape.data.cyrest_client import CyRestClient


cy  = CyRestClient()
network1 = cy.network.create_from("test.graphml")

mystyle = cy.style.create("ClassDefault")
