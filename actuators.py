#!/usr/bin/env python3
"""
REAL-WORLD ACTUATORS
====================

Browser control, email, Twitter/X, Telegram, Solana wallet,
cloud credentials, crypto payments integration.
"""

import os
import json
import asyncio
import smtplib
import imaplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging
from playwright.async_api import async_playwright
import tweepy
import telegram
from solana.rpc.async_api import AsyncClient
from solana.keypair import Keypair
from solana.system_program import TransferParams, transfer
from solana.transaction import Transaction
import boto3
import stripe

logger = logging.getLogger(__name__)

class BrowserActuator:
    """Playwright browser control for web actuation"""

    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page = None

    async def initialize(self):
        """Initialize browser"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        self.page = await self.browser.new_page()

    async def navigate(self, url: str) -> str:
        """Navigate to URL and return content"""
        if not self.page:
            await self.initialize()

        await self.page.goto(url)
        return await self.page.content()

    async def click(self, selector: str):
        """Click element by selector"""
        if self.page:
            await self.page.click(selector)

    async def type_text(self, selector: str, text: str):
        """Type text into element"""
        if self.page:
            await self.page.fill(selector, text)

    async def screenshot(self, path: str):
        """Take screenshot"""
        if self.page:
            await self.page.screenshot(path=path)

    async def close(self):
        """Close browser"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

class EmailActuator:
    """Gmail/Outlook SMTP + IMAP control"""

    def __init__(self, config: Dict):
        self.smtp_server = config.get('smtp_server', 'smtp.gmail.com')
        self.smtp_port = config.get('smtp_port', 587)
        self.imap_server = config.get('imap_server', 'imap.gmail.com')
        self.username = config.get('username')
        self.password = config.get('password')

    async def send_email(self, to: str, subject: str, body: str):
        """Send email"""
        msg = MIMEMultipart()
        msg['From'] = self.username
        msg['To'] = to
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(self.smtp_server, self.smtp_port)
        server.starttls()
        server.login(self.username, self.password)
        text = msg.as_string()
        server.sendmail(self.username, to, text)
        server.quit()

    async def check_emails(self) -> List[Dict]:
        """Check for new emails"""
        mail = imaplib.IMAP4_SSL(self.imap_server)
        mail.login(self.username, self.password)
        mail.select('inbox')

        status, messages = mail.search(None, 'UNSEEN')
        emails = []

        for msg_id in messages[0].split():
            status, msg_data = mail.fetch(msg_id, '(RFC822)')
            # Parse email (simplified)
            emails.append({'id': msg_id, 'data': msg_data})

        mail.close()
        mail.logout()
        return emails

class SocialActuator:
    """Twitter/X API v2 with OAuth 2.0 PKCE flow"""

    def __init__(self, config: Dict):
        self.client_id = config.get('client_id')
        self.client_secret = config.get('client_secret')
        self.bearer_token = config.get('bearer_token')
        self.access_token = config.get('access_token')
        self.client = None

    async def initialize(self):
        """Initialize Twitter client"""
        self.client = tweepy.Client(
            bearer_token=self.bearer_token,
            access_token=self.access_token,
            consumer_key=self.client_id,
            consumer_secret=self.client_secret
        )

    async def post_tweet(self, text: str) -> str:
        """Post a tweet"""
        if not self.client:
            await self.initialize()

        tweet = self.client.create_tweet(text=text)
        return tweet.data['id']

    async def get_mentions(self) -> List[Dict]:
        """Get recent mentions"""
        if not self.client:
            await self.initialize()

        mentions = self.client.get_users_mentions(self.client.get_me().data.id)
        return [{'id': m.id, 'text': m.text} for m in mentions.data]

class TelegramActuator:
    """Telegram bot API"""

    def __init__(self, config: Dict):
        self.token = config.get('token')
        self.chat_id = config.get('chat_id')
        self.bot = None

    async def initialize(self):
        """Initialize Telegram bot"""
        self.bot = telegram.Bot(token=self.token)

    async def send_message(self, text: str):
        """Send message to configured chat"""
        if not self.bot:
            await self.initialize()

        await self.bot.send_message(chat_id=self.chat_id, text=text)

    async def get_updates(self) -> List[Dict]:
        """Get recent updates"""
        if not self.bot:
            await self.initialize()

        updates = await self.bot.get_updates()
        return [{'message': u.message.text if u.message else None} for u in updates]

class CryptoActuator:
    """Solana wallet + Phantom-style transaction signing"""

    def __init__(self, config: Dict):
        self.rpc_url = config.get('rpc_url', 'https://api.mainnet-beta.solana.com')
        self.private_key = config.get('private_key')
        self.client = None
        self.keypair = None

    async def initialize(self):
        """Initialize Solana client and keypair"""
        self.client = AsyncClient(self.rpc_url)
        if self.private_key:
            self.keypair = Keypair.from_secret_key(bytes.fromhex(self.private_key))

    async def get_balance(self) -> float:
        """Get wallet balance"""
        if not self.client or not self.keypair:
            await self.initialize()

        balance = await self.client.get_balance(self.keypair.public_key)
        return balance['result']['value'] / 1_000_000_000  # Convert lamports to SOL

    async def transfer_sol(self, to_address: str, amount: float) -> str:
        """Transfer SOL"""
        if not self.client or not self.keypair:
            await self.initialize()

        # Create transfer instruction
        transfer_params = TransferParams(
            from_pubkey=self.keypair.public_key,
            to_pubkey=to_address,
            lamports=int(amount * 1_000_000_000)
        )

        # Create and sign transaction
        transaction = Transaction().add(transfer(transfer_params))
        signature = await self.client.send_transaction(transaction, self.keypair)

        return signature['result']

class CloudActuator:
    """AWS/GCP/DO credentials rotation endpoint"""

    def __init__(self, config: Dict):
        self.provider = config.get('provider', 'aws')
        self.access_key = config.get('access_key')
        self.secret_key = config.get('secret_key')
        self.region = config.get('region', 'us-east-1')
        self.client = None

    async def initialize(self):
        """Initialize cloud client"""
        if self.provider == 'aws':
            self.client = boto3.client(
                'ec2',
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                region_name=self.region
            )

    async def list_instances(self) -> List[Dict]:
        """List cloud instances"""
        if not self.client:
            await self.initialize()

        if self.provider == 'aws':
            response = self.client.describe_instances()
            instances = []
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    instances.append({
                        'id': instance['InstanceId'],
                        'state': instance['State']['Name'],
                        'type': instance['InstanceType']
                    })
            return instances

        return []

class PaymentActuator:
    """Crypto payment gateways (Stripe Crypto, NOWPayments)"""

    def __init__(self, config: Dict):
        self.provider = config.get('provider', 'stripe')
        self.api_key = config.get('api_key')
        self.client = None

    async def initialize(self):
        """Initialize payment client"""
        if self.provider == 'stripe':
            stripe.api_key = self.api_key
            self.client = stripe

    async def create_payment_intent(self, amount: float, currency: str = 'usd') -> str:
        """Create payment intent"""
        if not self.client:
            await self.initialize()

        if self.provider == 'stripe':
            intent = self.client.PaymentIntent.create(
                amount=int(amount * 100),  # Convert to cents
                currency=currency,
                payment_method_types=['card']
            )
            return intent.id

        return None

class ActuatorsManager:
    """Manager for all real-world actuators"""

    def __init__(self, swarm_core):
        self.swarm = swarm_core
        self.identities_dir = swarm_core.identities_dir

        # Initialize actuators
        self.browser = BrowserActuator()
        self.email = None
        self.social = None
        self.telegram = None
        self.crypto = None
        self.cloud = None
        self.payments = None

        self.load_actuator_configs()

    def load_actuator_configs(self):
        """Load actuator configurations from encrypted identities"""
        # Load email config
        email_config = self.load_identity('email.json')
        if email_config:
            self.email = EmailActuator(email_config)

        # Load social config
        social_config = self.load_identity('social.json')
        if social_config:
            self.social = SocialActuator(social_config)

        # Load telegram config
        telegram_config = self.load_identity('telegram.json')
        if telegram_config:
            self.telegram = TelegramActuator(telegram_config)

        # Load crypto config
        crypto_config = self.load_identity('crypto.json')
        if crypto_config:
            self.crypto = CryptoActuator(crypto_config)

        # Load cloud config
        cloud_config = self.load_identity('cloud.json')
        if cloud_config:
            self.cloud = CloudActuator(cloud_config)

        # Load payments config
        payments_config = self.load_identity('payments.json')
        if payments_config:
            self.payments = PaymentActuator(payments_config)

    def load_identity(self, filename: str) -> Optional[Dict]:
        """Load encrypted identity file"""
        filepath = self.identities_dir / filename
        if filepath.exists():
            try:
                with open(filepath, 'r') as f:
                    # In real implementation, this would decrypt
                    return json.load(f)
            except Exception as e:
                logger.error("Failed to load identity %s: %s", filename, e)
        return None

    async def initialize_all(self):
        """Initialize all actuators"""
        logger.info("Initializing all actuators...")

        # Initialize browser
        await self.browser.initialize()

        # Initialize others if configured
        if self.email:
            logger.info("Email actuator configured")
        if self.social:
            await self.social.initialize()
        if self.telegram:
            await self.telegram.initialize()
        if self.crypto:
            await self.crypto.initialize()
        if self.cloud:
            await self.cloud.initialize()
        if self.payments:
            await self.payments.initialize()

        logger.info("All actuators initialized")

    async def test_actuators(self):
        """Test all actuators"""
        logger.info("Testing actuators...")

        # Test browser
        try:
            content = await self.browser.navigate('https://httpbin.org/html')
            logger.info("Browser test: %d chars retrieved", len(content))
        except Exception as e:
            logger.error("Browser test failed: %s", e)

        # Test crypto balance if configured
        if self.crypto:
            try:
                balance = await self.crypto.get_balance()
                logger.info("Crypto balance: %.4f SOL", balance)
            except Exception as e:
                logger.error("Crypto test failed: %s", e)

# Global instance
actuators_manager = None

async def initialize_actuators(swarm_core):
    """Initialize the global actuators manager"""
    global actuators_manager
    actuators_manager = ActuatorsManager(swarm_core)
    await actuators_manager.initialize_all()
    return actuators_manager