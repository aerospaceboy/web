"""Compatibility entry point; defaults to an offline plan. Use --apply to publish."""

from blog_tools.publish import main


if __name__ == "__main__":
    raise SystemExit(main())
