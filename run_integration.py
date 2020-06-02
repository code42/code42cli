import sys
import os

if __name__ == "__main__":
    rc = os.system("pytest ./integration -v -rsxX -l --tb=short --strict")
    sys.exit(rc)
