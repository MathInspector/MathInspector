"""version detector. Precedence: installed dist, git, 'UNKNOWN'."""
try:
    from ._dist_ver import VERSION
except ImportError:
    try:
        from setuptools_scm import get_version
        VERSION = get_version(root='..', relative_to=__file__)
    except (ImportError, LookupError):
        VERSION = "UNKNOWN"
