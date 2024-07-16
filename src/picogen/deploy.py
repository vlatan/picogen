import subprocess
from pathlib import Path


def deploy_website(bucket_name: str) -> None:
    """
    Sync files from a "build" directory to an S3 bucket.

    Parameters:
        bucket_name (str): Amazon S3 bucket name.
    """

    build_dir = Path.cwd() / "build"
    if not build_dir.is_dir():
        raise FileNotFoundError(f"No 'build' directory: '{build_dir}'.")

    # sync images(jpg, jpeg, png, gif, svg), css and js
    # to s3://{args.deploy} with big max-age
    sync_static = (
        f'aws s3 sync {build_dir} s3://{bucket_name} --exclude "*" '
        '--include "*.jpg" --include "*.jpeg" --include "*.png" '
        '--include "*.gif" --include "*.svg" --include "*.webp" '
        '--include "*.css" --include "*.js" '
        '--cache-control "public, max-age=31536000" '
        "--storage-class INTELLIGENT_TIERING --delete"
    )
    subprocess.run(sync_static, shell=True)

    # sync json, ico, xml, xsl files
    # to s3://{args.deploy} with small max-age
    sync_other = (
        f'aws s3 sync {build_dir} s3://{bucket_name} --exclude "*" '
        '--include "*.json" --include "*.ico" --include "*.xml" '
        '--include "*.xsl" --cache-control "public, max-age=86400" '
        "--storage-class INTELLIGENT_TIERING --delete"
    )
    subprocess.run(sync_other, shell=True)

    # sync the rest of the files with no max-age cache
    sync_rest = (
        f"aws s3 sync {build_dir} s3://{bucket_name} "
        "--storage-class INTELLIGENT_TIERING --delete",
    )
    subprocess.run(sync_rest, shell=True)
