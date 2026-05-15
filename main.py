# main.py
from server import mcp

import icd10  # noqa: F401
import loinc  # noqa: F401
import rxnorm  # noqa: F401

if __name__ == "__main__":
    mcp.run()
