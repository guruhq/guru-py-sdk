"""Resource modules — one file per Guru API resource group.

Each resource class receives an HttpClient via constructor injection and
provides typed CRUD operations. Resource classes never construct HTTP
requests directly — they delegate to HttpClient methods.
"""
