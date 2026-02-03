"""Azure services for SharePoint, Graph API, and Blob Storage."""

from app.services.azure.graph import graph_client, GraphClient
from app.services.azure.blob import blob_client, BlobClient
from app.services.azure.msal import msal_client, MsalClient

__all__ = [
    "graph_client",
    "GraphClient",
    "blob_client",
    "BlobClient",
    "msal_client",
    "MsalClient",
]
