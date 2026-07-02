import logging
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from django.conf import settings
from django.template.loader import render_to_string

from app.email_log.models import EmailLog, EmailLogStatus, EmailSendPurposeChoices

logger = logging.getLogger(__name__)

AWS_IO_CONFIG = Config(
    connect_timeout=3,
    read_timeout=5,
    retries={"max_attempts": 1, "mode": "standard"},
)


def send_email_with_django_template(
    recipient,
    title,
    purpose: EmailSendPurposeChoices,
    context,
):
    sender = settings.DEFAULT_FROM_EMAIL
    client = boto3.client("ses", region_name="ap-northeast-2", config=AWS_IO_CONFIG)
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    logo_key = "_static/img/Logo.png"

    template_name = purpose.value
    if "naver" in recipient:
        template_name += "_naver"

    # 템플릿 경로 결정
    template_path = f"emails/{template_name}.html"

    # HTML 템플릿을 CID 이미지로 변환
    body_html = render_to_string(template_path, context)

    # 템플릿 내 S3 로고 URL을 CID 참조로 교체
    body_html = body_html.replace(
        f'src="https://{bucket_name}.s3.ap-northeast-2.amazonaws.com/{logo_key}"',
        'src="cid:logo"',
    )
    body_html = body_html.replace(
        'src="https://holyclub-dev-bucket.s3.ap-northeast-2.amazonaws.com/_static/img/Logo.png"',
        'src="cid:logo"',
    )

    # multipart/related 메시지 생성
    msg = MIMEMultipart("related")
    msg["Subject"] = title
    msg["From"] = sender
    msg["To"] = recipient

    # HTML 본문 추가
    html_part = MIMEText(body_html, "html", "utf-8")
    msg.attach(html_part)

    # S3에서 로고 이미지 다운로드 후 첨부
    try:
        s3_client = boto3.client("s3", region_name="ap-northeast-2", config=AWS_IO_CONFIG)
        logo_response = s3_client.get_object(Bucket=bucket_name, Key=logo_key)
        logo_data = logo_response["Body"].read()

        # 이미지 첨부
        logo_attachment = MIMEImage(logo_data, "png")
        logo_attachment.add_header("Content-ID", "<logo>")
        logo_attachment.add_header("Content-Disposition", "inline", filename="logo.png")
        msg.attach(logo_attachment)

    except ClientError as e:
        logger.warning(f"Failed to download logo from S3: {e}")
    except Exception as e:
        logger.error(f"Error attaching logo: {e}")

    # SendRawEmail로 전송
    response = {}
    error_msg = ""

    try:
        response = client.send_raw_email(
            Source=sender,
            Destinations=[recipient],
            RawMessage={"Data": msg.as_string()},
        )
        logger.info(response)
    except ClientError as e:
        error_msg = str(e)
        logger.error(error_msg)
        return {"error": error_msg}
    except Exception as e:
        error_msg = str(e)
        logger.error(error_msg)
        return {"error": error_msg}

    try:
        email_log = EmailLog.objects.create(
            recipient=recipient,
            purpose=purpose,
            status=EmailLogStatus.READY,
            fail_reason=error_msg,
        )

        if response.get("ResponseMetadata", {}).get("HTTPStatusCode") == 200:
            email_log.status = EmailLogStatus.SUCCESS
        else:
            email_log.status = EmailLogStatus.FAILURE
            email_log.fail_reason = error_msg
        email_log.save()
    except Exception as e:
        logger.error(f"Failed to persist email log: {e}")

    return response
