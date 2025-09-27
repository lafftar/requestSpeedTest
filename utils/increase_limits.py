import sys


def set_max_open_files():
    """
    Increases the open file limit to the maximum possible for the current process.
    - On Linux, it uses the `resource` module to set the soft limit to the hard limit.
    - On Windows, it does nothing, as the concept is different and limits are
      generally not an issue for this use case.
    """
    if sys.platform != "linux":
        print("Running on Windows: No programmatic file limit change is needed.")
        return

    try:
        import resource

        # Get the current soft and hard limits
        soft_limit, hard_limit = resource.getrlimit(resource.RLIMIT_NOFILE)

        print(f"Current limits: Soft = {soft_limit}, Hard = {hard_limit}")

        try:
            # Attempt to set the soft limit to the hard limit
            resource.setrlimit(resource.RLIMIT_NOFILE, (hard_limit, hard_limit))
            new_soft, new_hard = resource.getrlimit(resource.RLIMIT_NOFILE)
            print(f"Successfully raised soft limit to {new_soft}.")
        except ValueError:
            print(f"Could not raise soft limit. Attempting to set to a lower value.")
            # If setting to hard_limit fails (e.g. hard_limit is unlimited),
            # try setting to a very large number instead.
            try:
                # A common high value for servers
                high_limit = 65536
                resource.setrlimit(resource.RLIMIT_NOFILE, (high_limit, high_limit))
                new_soft, new_hard = resource.getrlimit(resource.RLIMIT_NOFILE)
                print(f"Successfully raised soft limit to {new_soft}.")
            except Exception as e:
                print(f"Failed to set a high limit: {e}")

    except ImportError:
        print("`resource` module not found. This script is intended for Linux.")


# --- Example Usage ---
# Call this function at the start of your application
if __name__ == "__main__":
    set_max_open_files()

    # Your httpx or rnet code would go here
    print("Ready to run high-concurrency network requests.")