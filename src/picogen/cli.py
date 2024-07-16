import argparse
from .deploy import deploy_website
from .backup import backup_content
from .generate import generate_website


def main() -> None:
    """
    Take CLI arguments and generate/deploy/backup files to AWS S3 bucket(s).
    """

    parser = argparse.ArgumentParser(
        description=(
            "Deploy static website to AWS S3 bucket "
            "and/or backup your makrdown files "
            "to a separate S3 bucket."
        ),
    )
    parser.add_argument(
        "-g",
        "--generate",
        action="store_true",
        help='generate a static website into the "build" dir',
    )
    parser.add_argument(
        "-d",
        "--deploy",
        metavar="BUCKET_NAME",
        help='sync the "build" dir with a bucket',
    )
    parser.add_argument(
        "-b",
        "--backup",
        metavar="BUCKET_NAME",
        help='sync the "content" dir with a bucket',
    )
    args = parser.parse_args()

    if args.generate:
        generate_website()
        print(f'Static website generated in "build" directory')

    if args.deploy:
        deploy_website(args.deploy)
        print(f'"build" directory synced with s3://{args.deploy}')

    if args.backup:
        backup_content(args.backup)
        print(f'"content" directory synced with s3://{args.backup}')


if __name__ == "__main__":
    main()
