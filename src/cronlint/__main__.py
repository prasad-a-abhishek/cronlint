"""Allow `python -m cronlint` to invoke the CLI."""

from .cli import main

raise SystemExit(main())