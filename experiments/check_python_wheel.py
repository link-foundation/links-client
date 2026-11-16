"""Run with a fresh interpreter after installing the built Python wheel."""

from importlib.metadata import version

import links_client
from links_client.api.ilinks import ILinks
from links_client.api.recursive_links import RecursiveLinks

assert links_client.__version__ == version("links-client")
assert links_client.ILinks is ILinks
assert links_client.RecursiveLinks is RecursiveLinks
for name in links_client.__all__:
    assert getattr(links_client, name) is not None, name
print(f"Installed links-client {links_client.__version__}: all public imports passed")
