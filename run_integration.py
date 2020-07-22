import os
import sys

if __name__ == "__main__":
    if sys.argv[1] and sys.argv[2]:
        os.environ["C42_USER"] = sys.argv[1]
        os.environ["C42_PW"] = sys.argv[2]
        rc = os.system("pytest ./integration -v -rsxX -l --tb=short --strict")
        sys.exit(rc)
    else:
        print(
            "username and password were not supplied. Integration tests will be skipped."
        )
