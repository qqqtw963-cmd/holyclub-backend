import re

import boto3
from django.core.management import BaseCommand

from app.common.utils import color_string


class Command(BaseCommand):
    help = "SES 샌드박스 모드 해제를 요청합니다."

    def handle(self, *args, **options):
        website_url = self.validate_website_url(input(color_string("cyan", "웹사이트 주소: (ex: https://example.com)")))
        contact_email = self.validate_email(input(color_string("cyan", "컨텍 이메일: (ex: example@example.com)")))
        blank_message = "\n(아무것도 입력하지 않으면 기본값이 사용됩니다): "
        default_description_1 = "We plan to use the mailing list primarily for email verification during user registration and for password recovery purposes. Users will provide their email addresses during the sign-up process, which will then be used to send a verification email to confirm their identity. Additionally, in the case of forgotten passwords, users can request a password reset email. Both of these processes ensure that we have accurate and up-to-date email addresses while also securing user accounts. Throughout the email address collection process, we will prioritize the privacy and protection of our users' personal information."
        default_description_2 = "We plan to handle bounces and complaints through an automated system integrated with Amazon SES. For bounces, we will utilize SES's bounce handling feature to automatically detect and remove invalid email addresses from our mailing list. This ensures that we maintain a clean and efficient list, reducing the likelihood of future bounces. For complaints, we will use SES's complaint handling feature to process feedback from recipients who mark our emails as spam. These email addresses will also be promptly removed from our mailing list to respect recipients' preferences and maintain our sender reputation."
        default_description_3 = "Each email we send will include an unsubscribe link at the bottom, allowing recipients to easily opt out of future emails. When recipients click this link, they will be directed to a page where they can confirm their decision to unsubscribe. This request will be processed immediately, and the recipient's email address will be removed from our mailing list to ensure they no longer receive our emails. Additionally, we will provide a contact email address where recipients can manually request to be unsubscribed, and such requests will be handled promptly by our support team."
        default_description_4 = "The sending rate and sending quota specified in this request were determined based on our current and projected email volume needs. We primarily send emails for user registration verification and password recovery, which are critical for account security. Our estimates are based on our current user base and anticipated growth, ensuring we can handle peak usage times without any issues. These projections allow us to maintain a balance between efficiency and system reliability, ensuring optimal performance and user experience."
        use_case_description = [
            input(color_string("cyan", f"메일 발송 목록을 어떻게 작성하거나 만들 계획인가요?{blank_message}")) or default_description_1,
            input(color_string("cyan", f"반송 메일과 수신 거부를 어떻게 처리할 계획인가요?{blank_message}")) or default_description_2,
            input(color_string("cyan", f"수신자가 귀하가 보내는 이메일을 수신 거부하는 방법은 무엇입니까?{blank_message}"))
            or default_description_3,
            input(
                color_string(
                    "cyan",
                    f"이 요청에서 귀하가 지정한 송신률 또는 발신 할당량을 어떻게 선택하셨습니까?{blank_message}",
                )
            )
            or default_description_4,
        ]
        print("\n".join(use_case_description))

        ses_client = boto3.client("sesv2", region_name="ap-northeast-2")
        ses_client.put_account_details(
            MailType="TRANSACTIONAL",
            WebsiteURL=website_url,
            ContactLanguage="EN",
            UseCaseDescription="\n".join(use_case_description),
            AdditionalContactEmailAddresses=[contact_email],
            ProductionAccessEnabled=True,
        )

    def validate_website_url(self, website_url):
        url_pattern = re.compile(r"^(?:http|ftp)s?://")
        if not re.match(url_pattern, website_url):
            print(color_string("red", "Invalid website URL"))
            return self.validate_website_url(input(color_string("cyan", "Website URL: ")))
        return website_url

    def validate_email(self, email):
        email_pattern = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
        if not re.match(email_pattern, email):
            print(color_string("red", "Invalid Email"))
            return self.validate_email(input(color_string("cyan", "Contact Email: ")))
        return email
