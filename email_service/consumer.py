from kafka import KafkaConsumer
import json
import logging
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("FROM_EMAIL", "noreply@videogametrading.com")
    
    def send_email(self, to_email: str, subject: str, body: str):
        if not self.smtp_username or not self.smtp_password:
            logger.warning(f"SMTP credentials not configured. Would send email to {to_email}: {subject}")
            logger.info(f"Email body: {body}")
            return
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'html'))
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_email}")
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
    
    def process_notification(self, message: dict):
        event_type = message.get("event_type")
        data = message.get("data", {})
        
        if event_type == "password_changed":
            self._handle_password_changed(data)
        elif event_type == "trade_offer_created":
            self._handle_trade_offer_created(data)
        elif event_type == "trade_offer_accepted":
            self._handle_trade_offer_accepted(data)
        elif event_type == "trade_offer_rejected":
            self._handle_trade_offer_rejected(data)
        else:
            logger.warning(f"Unknown event type: {event_type}")
    
    def _handle_password_changed(self, data: dict):
        user_email = data.get("user_email")
        user_name = data.get("user_name")
        
        subject = "Password Changed - Video Game Trading"
        body = f"""
        <html>
        <body>
            <h2>Password Changed</h2>
            <p>Hello {user_name},</p>
            <p>Your password has been successfully changed.</p>
            <p>If you did not make this change, please contact support immediately.</p>
            <br>
            <p>Best regards,<br>Video Game Trading Team</p>
        </body>
        </html>
        """
        
        self.send_email(user_email, subject, body)
    
    def _handle_trade_offer_created(self, data: dict):
        offerer_email = data.get("offerer_email")
        offerer_name = data.get("offerer_name")
        receiver_email = data.get("receiver_email")
        receiver_name = data.get("receiver_name")
        offered_game = data.get("offered_game")
        requested_game = data.get("requested_game")
        
        offerer_subject = "Trade Offer Sent - Video Game Trading"
        offerer_body = f"""
        <html>
        <body>
            <h2>Trade Offer Sent</h2>
            <p>Hello {offerer_name},</p>
            <p>You have successfully sent a trade offer:</p>
            <ul>
                <li><strong>You offer:</strong> {offered_game}</li>
                <li><strong>You request:</strong> {requested_game}</li>
                <li><strong>To:</strong> {receiver_name}</li>
            </ul>
            <p>You will be notified when {receiver_name} responds to your offer.</p>
            <br>
            <p>Best regards,<br>Video Game Trading Team</p>
        </body>
        </html>
        """
        
        receiver_subject = "New Trade Offer Received - Video Game Trading"
        receiver_body = f"""
        <html>
        <body>
            <h2>New Trade Offer Received</h2>
            <p>Hello {receiver_name},</p>
            <p>You have received a new trade offer from {offerer_name}:</p>
            <ul>
                <li><strong>They offer:</strong> {offered_game}</li>
                <li><strong>They request:</strong> {requested_game}</li>
            </ul>
            <p>Please log in to your account to accept or reject this offer.</p>
            <br>
            <p>Best regards,<br>Video Game Trading Team</p>
        </body>
        </html>
        """
        
        self.send_email(offerer_email, offerer_subject, offerer_body)
        self.send_email(receiver_email, receiver_subject, receiver_body)

    def _handle_trade_offer_accepted(self, data: dict):
        offerer_email = data.get("offerer_email")
        offerer_name = data.get("offerer_name")
        receiver_email = data.get("receiver_email")
        receiver_name = data.get("receiver_name")
        offered_game = data.get("offered_game")
        requested_game = data.get("requested_game")

        offerer_subject = "Trade Offer Accepted - Video Game Trading"
        offerer_body = f"""
        <html>
        <body>
            <h2>Trade Offer Accepted!</h2>
            <p>Hello {offerer_name},</p>
            <p>Great news! {receiver_name} has accepted your trade offer:</p>
            <ul>
                <li><strong>You offer:</strong> {offered_game}</li>
                <li><strong>You receive:</strong> {requested_game}</li>
            </ul>
            <p>Please coordinate with {receiver_name} to complete the trade.</p>
            <br>
            <p>Best regards,<br>Video Game Trading Team</p>
        </body>
        </html>
        """

        receiver_subject = "Trade Offer Accepted - Video Game Trading"
        receiver_body = f"""
        <html>
        <body>
            <h2>Trade Offer Accepted</h2>
            <p>Hello {receiver_name},</p>
            <p>You have accepted the trade offer from {offerer_name}:</p>
            <ul>
                <li><strong>You receive:</strong> {offered_game}</li>
                <li><strong>You offer:</strong> {requested_game}</li>
            </ul>
            <p>Please coordinate with {offerer_name} to complete the trade.</p>
            <br>
            <p>Best regards,<br>Video Game Trading Team</p>
        </body>
        </html>
        """

        self.send_email(offerer_email, offerer_subject, offerer_body)
        self.send_email(receiver_email, receiver_subject, receiver_body)

    def _handle_trade_offer_rejected(self, data: dict):
        offerer_email = data.get("offerer_email")
        offerer_name = data.get("offerer_name")
        receiver_email = data.get("receiver_email")
        receiver_name = data.get("receiver_name")
        offered_game = data.get("offered_game")
        requested_game = data.get("requested_game")

        offerer_subject = "Trade Offer Rejected - Video Game Trading"
        offerer_body = f"""
        <html>
        <body>
            <h2>Trade Offer Rejected</h2>
            <p>Hello {offerer_name},</p>
            <p>{receiver_name} has declined your trade offer:</p>
            <ul>
                <li><strong>You offered:</strong> {offered_game}</li>
                <li><strong>You requested:</strong> {requested_game}</li>
            </ul>
            <p>You can browse other games and make new trade offers.</p>
            <br>
            <p>Best regards,<br>Video Game Trading Team</p>
        </body>
        </html>
        """

        receiver_subject = "Trade Offer Rejected - Video Game Trading"
        receiver_body = f"""
        <html>
        <body>
            <h2>Trade Offer Rejected</h2>
            <p>Hello {receiver_name},</p>
            <p>You have rejected the trade offer from {offerer_name}:</p>
            <ul>
                <li><strong>They offered:</strong> {offered_game}</li>
                <li><strong>They requested:</strong> {requested_game}</li>
            </ul>
            <br>
            <p>Best regards,<br>Video Game Trading Team</p>
        </body>
        </html>
        """

        self.send_email(offerer_email, offerer_subject, offerer_body)
        self.send_email(receiver_email, receiver_subject, receiver_body)


def main():
    bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
    topic = os.getenv("KAFKA_TOPIC_NOTIFICATIONS", "email-notifications")
    group_id = os.getenv("KAFKA_GROUP_ID", "email-notification-group")

    logger.info(f"Starting email consumer service...")
    logger.info(f"Bootstrap servers: {bootstrap_servers}")
    logger.info(f"Topic: {topic}")
    logger.info(f"Group ID: {group_id}")

    email_service = EmailService()

    while True:
        try:
            consumer = KafkaConsumer(
                topic,
                bootstrap_servers=bootstrap_servers,
                group_id=group_id,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                auto_offset_reset='earliest',
                enable_auto_commit=True
            )

            logger.info("Kafka consumer connected successfully. Waiting for messages...")

            for message in consumer:
                try:
                    logger.info(f"Received message: {message.value}")
                    email_service.process_notification(message.value)
                except Exception as e:
                    logger.error(f"Error processing message: {e}")

        except Exception as e:
            logger.error(f"Kafka consumer error: {e}")
            logger.info("Retrying in 10 seconds...")
            time.sleep(10)


if __name__ == "__main__":
    main()

