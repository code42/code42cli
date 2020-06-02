import sys
import os

if __name__ == "__main__":
    try:
        profile_password = os.environ["USER_PW"]
        # TODO Validate profile is set
    except KeyError:
        print("Profile password not found in environment. Integration tests will be skipped.")
        sys.exit(1)

    rc = os.system("pytest ./integration -v -rsxX -l --tb=short --strict")
    sys.exit(rc)
