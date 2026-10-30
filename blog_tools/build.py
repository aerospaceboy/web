"""Build reviewable Halo Console deployment files without contacting the site."""

import argparse
import hashlib
import json
import re
from pathlib import Path

from . import configure_console
from .publish import ROOT, load_posts

STYLE_ID = "aerospaceboy-global-style"
NAV_ID = "aerospaceboy-mobile-navigation-script"


def validate_injected_text(source):
    # Halo processes global injection with Thymeleaf text inlining. A JS nested
    # array written without whitespace can accidentally become an expression.
    if any(marker in source for marker in ("[[", "[(")):
        raise ValueError("Injected code contains a Thymeleaf inline-expression opener; separate the brackets")


def navigation_source(config):
    settings = {"privacyPolicyPath": config.get("privacy_policy_path", "/privacy-policy"),
                "defaultCoverPath": config.get("default_cover_path", ""),
                "nebulaBackgroundPath": config.get("nebula_background_path", ""),
                "resumePath": config.get("resume_path", "")}
    for value in settings.values():
        if value and (not isinstance(value, str) or not value.startswith("/") or
                      value.startswith("//") or any(c in value for c in "\r\n<>\\")):
            raise ValueError("Public paths must be relative to the site origin")
    github = config.get("github_profile_url", "")
    if not isinstance(github, str) or (github and not re.fullmatch(r"https://github\.com/[A-Za-z0-9][A-Za-z0-9-]{0,38}/?", github)):
        raise ValueError("GitHub destination must be an HTTPS profile on github.com")
    settings["githubProfileUrl"] = github
    prefix = "window.__abPublicConfig = " + json.dumps(settings, ensure_ascii=True).replace("<", "\\u003c") + ";\n"
    source = prefix + "\n".join((ROOT / "customization" / name).read_text(encoding="utf-8")
                               for name in ("mobile-navigation.js", "header-layout.js", "space-effects.js", "pointer-effects.js", "resume-enhancement.js", "site-hub.js", "motion-effects.js"))
    validate_injected_text(source)
    return source


def build(output=ROOT / "build", config_path=ROOT / "config/site.json"):
    output = Path(output)
    config = json.loads(Path(config_path).read_text(encoding="utf-8-sig"))
    css = (ROOT / "customization/aerospaceboy-custom.css").read_text(encoding="utf-8")
    if "</style" in css.lower():
        raise ValueError("CSS contains a closing style tag")
    validate_injected_text(css)
    digest = hashlib.sha256(css.encode("utf-8")).hexdigest()
    navigation = navigation_source(config)
    if "</script" in navigation.lower():
        raise ValueError("Navigation contains a closing script tag")
    navigation_digest = hashlib.sha256(navigation.encode("utf-8")).hexdigest()
    output.mkdir(parents=True, exist_ok=True)
    (output / "global-head.html").write_text(
        f'<style id="{STYLE_ID}" data-ab-sha256="{digest}">\n{css}</style>\n'
        f'<script id="{NAV_ID}" data-ab-sha256="{navigation_digest}">\n{navigation}</script>\n', encoding="utf-8")
    (output / "about-excerpt.txt").write_text(config["about_description"] + "\n", encoding="utf-8")
    (output / "site-description.txt").write_text(config["site_description"] + "\n", encoding="utf-8")
    plan = {"base_url": config["base_url"], "css_sha256": digest,
            "navigation_sha256": navigation_digest,
            "global_head_file": "global-head.html", "about_excerpt_file": "about-excerpt.txt",
            "site_description_file": "site-description.txt",
            "articles": len(load_posts(ROOT / "content/posts.json")),
            "requires_console_save": True}
    (output / "manifest.json").write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return plan


def main(argv=None):
    configure_console()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "build")
    args = parser.parse_args(argv)
    print(json.dumps(build(args.output), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
