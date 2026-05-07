import boto3
import os
from dotenv import load_dotenv
from scripts.logger import get_logger
from scripts.config import OUTPUT_DIR

# Load credentials from .env file
load_dotenv()

logger = get_logger("s3_upload")


def get_s3_client():
    """
    Creates and returns an S3 client using
    credentials from .env file.
    """
    client = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION")
    )
    return client


def upload_file_to_s3(local_filepath, s3_filename):
    """
    Uploads a single file from local output/
    folder to S3 bucket.
    """
    bucket_name = os.getenv("AWS_BUCKET_NAME")

    try:
        client = get_s3_client()
        client.upload_file(local_filepath, bucket_name, s3_filename)
        logger.info(f"Uploaded to S3: s3://{bucket_name}/{s3_filename}")
        return True

    except Exception as e:
        logger.error(f"S3 upload failed for {s3_filename}: {e}")
        return False


def upload_all_reports():
    """
    Scans the output/ folder and uploads
    every CSV file to S3.
    """
    logger.info("Starting S3 upload for all reports...")

    # Find all CSV files in output folder
    csv_files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith(".csv")]

    if not csv_files:
        logger.warning("No CSV files found in output/ folder")
        return

    success_count = 0
    for filename in csv_files:
        local_path = os.path.join(OUTPUT_DIR, filename)

        # Upload to reports/ folder inside S3 bucket
        s3_path = f"reports/{filename}"

        if upload_file_to_s3(local_path, s3_path):
            success_count += 1

    logger.info(f"S3 upload complete: {success_count}/{len(csv_files)} files uploaded")


def verify_s3_upload():
    """
    Lists all files in S3 bucket to confirm upload.
    """
    bucket_name = os.getenv("AWS_BUCKET_NAME")

    try:
        client = get_s3_client()
        response = client.list_objects_v2(
            Bucket=bucket_name,
            Prefix="reports/"
        )

        if "Contents" not in response:
            logger.warning("No files found in S3 bucket")
            return

        logger.info(f"Files in S3 bucket s3://{bucket_name}/reports/:")
        for obj in response["Contents"]:
            logger.info(f"  {obj['Key']} — {obj['Size']} bytes")

    except Exception as e:
        logger.error(f"S3 verify failed: {e}")


if __name__ == "__main__":
    upload_all_reports()
    verify_s3_upload()