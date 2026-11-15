"""Static site/author identity only; never claim it describes the current article."""
import json
import re

from .halo import validate_base_url

SEO_ID = 'aerospaceboy-site-identity'


def site_identity(config):
    base = validate_base_url(config['base_url']).rstrip('/')
    github = config['github_profile_url']
    if not re.fullmatch(r'https://github\.com/[A-Za-z0-9][A-Za-z0-9-]{0,38}/?', github):
        raise ValueError('Author sameAs must be an HTTPS GitHub profile')
    return {'@context': 'https://schema.org', '@graph': [
        {'@type': 'WebSite', '@id': base + '/#website', 'url': base + '/',
         'name': config['site_title'], 'description': config['site_description'],
         'inLanguage': 'zh-CN', 'publisher': {'@id': base + '/about#author'}},
        {'@type': 'Person', '@id': base + '/about#author', 'name': config['author_name'],
         'url': base + '/about', 'sameAs': [github]}
    ]}


def identity_json(config):
    # Safe in an HTML script element and in Halo's text-inlining pipeline.
    return json.dumps(site_identity(config), ensure_ascii=True, indent=2).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
