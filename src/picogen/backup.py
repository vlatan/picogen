import subprocess
from pathlib import Path


def backup_content(bucket_name: str) -> None:
    """
    Sync files from a "content" directory to an S3 bucket.

    Parameters:
        bucket_name (str): Amazon S3 bucket name.
    """

    content_dir = Path.cwd() / "content"
    if not content_dir.is_dir():
        raise FileNotFoundError(f"No 'content' directory: '{content_dir}'.")

    # backup the markdown files
    sync_all = (
        f"aws s3 sync {content_dir} s3://{bucket_name} ",
        "--storage-class INTELLIGENT_TIERING --delete",
    )
    subprocess.run(sync_all, shell=True)
