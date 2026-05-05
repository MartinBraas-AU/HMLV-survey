"""Compatibility wrapper for the unified figure generator.

The publication timeline style that used to live here has been merged into
generate_figures.py. Keep this entry point so existing commands continue to
work while all figure logic remains in one script.
"""

from generate_figures import main


if __name__ == "__main__":
    main()
