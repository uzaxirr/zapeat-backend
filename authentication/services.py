import logging

from django.conf import settings
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

class SMSService:
    """
    Handles SMS sending via Twilio with comprehensive error management
    """
    def __init__(self):
        try:
            self.client = Client(
                settings.TWILIO_ACCOUNT_SID,
                settings.TWILIO_AUTH_TOKEN
            )
        except Exception as e:
            logging.error(f"Twilio Client Initialization Error: {e}")
            raise

    def send_verification_sms(self, phone_number: str, verification_code: str):
        """
        Send verification SMS with error handling and logging
        
        Args:
            phone_number (str): Recipient's phone number in E.164 format
            verification_code (str): 6-digit verification code
        
        Returns:
            bool: Whether SMS was sent successfully
        """
        try:
            message = self.client.messages.create(
                body=f"Your verification code is: {verification_code}",
                from_=settings.TWILIO_PHONE_NUMBER,
                to=phone_number
            )

            # Log successful SMS sending
            logging.info(f"Verification SMS sent to {phone_number}. SID: {message.sid}")
            return True

        except TwilioRestException as twilio_error:
            # Handle Twilio-specific errors
            logging.error(f"Twilio SMS Error: {twilio_error}")

            # Map Twilio error codes to more meaningful messages
            error_map = {
                21211: "Invalid phone number format",
                21214: "Phone number not verified with Twilio",
                21421: "Rate limit exceeded"
            }

            error_message = error_map.get(
                twilio_error.code,
                "Failed to send verification SMS"
            )

            raise ValueError(error_message)

        except Exception as e:
            # Catch-all for unexpected errors
            logging.error(f"Unexpected SMS sending error: {e}")
            raise ValueError("SMS service temporarily unavailable")