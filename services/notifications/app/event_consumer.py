"""
RabbitMQ event consumer for notifications service.
Listens for events from other services and processes them.
"""
import json
import logging
import os
from typing import Dict, Any
import pika
from pika.exceptions import AMQPConnectionError

logger = logging.getLogger(__name__)


class EventConsumer:
    """RabbitMQ event consumer for processing inter-service events."""
    
    def __init__(self):
        self.connection = None
        self.channel = None
        self.rabbitmq_url = os.getenv(
            "RABBITMQ_URL", 
            "amqp://admin:admin123@rabbitmq.rabbitmq.svc.cluster.local:5672"
        )
        self.exchange_name = "ai_project_events"
        self.queue_name = "notifications_queue"
    
    def setup_connection(self):
        """Setup RabbitMQ connection and queue."""
        try:
            parameters = pika.URLParameters(self.rabbitmq_url)
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            # Declare exchange
            self.channel.exchange_declare(
                exchange=self.exchange_name,
                exchange_type='topic',
                durable=True
            )
            
            # Declare queue
            self.channel.queue_declare(queue=self.queue_name, durable=True)
            
            # Bind queue to exchange for user events
            self.channel.queue_bind(
                exchange=self.exchange_name,
                queue=self.queue_name,
                routing_key='user.*'
            )
            
            # Bind queue to exchange for auth events
            self.channel.queue_bind(
                exchange=self.exchange_name,
                queue=self.queue_name,
                routing_key='auth.*'
            )
            
            logger.info("Successfully connected to RabbitMQ and set up queue bindings")
            return True
            
        except AMQPConnectionError as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error setting up RabbitMQ: {e}")
            return False
    
    def process_message(self, ch, method, properties, body):
        """Process incoming messages."""
        try:
            # Parse message
            message = json.loads(body.decode('utf-8'))
            event_type = message.get('event_type')
            data = message.get('data', {})
            source = message.get('source', 'unknown')
            
            logger.info(f"Received event: {event_type} from {source} with data: {data}")
            
            # Route to appropriate handler
            if event_type == 'user.registered':
                self.handle_user_registered(data)
            elif event_type == 'auth.password_reset':
                self.handle_password_reset(data)
            else:
                logger.warning(f"Unknown event type: {event_type}")
            
            # Acknowledge message
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse message JSON: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    
    def handle_user_registered(self, data: Dict[str, Any]):
        """Handle user registration event."""
        email = data.get('email')
        name = data.get('name', 'User')
        
        logger.info(f"Processing user registration for {email}")
        
        # TODO: Send welcome email
        # TODO: Create user notification preferences
        # TODO: Send to analytics service
        
        print(f"📧 Would send welcome email to {email} (name: {name})")
    
    def handle_password_reset(self, data: Dict[str, Any]):
        """Handle password reset event."""
        email = data.get('email')
        name = data.get('name', 'User')
        
        logger.info(f"Processing password reset for {email}")
        
        # TODO: Send password reset email
        # TODO: Log security event
        
        print(f"🔐 Would send password reset email to {email} (name: {name})")
    
    def start_consuming(self):
        """Start consuming messages."""
        if not self.setup_connection():
            logger.error("Failed to setup RabbitMQ connection")
            return
        
        # Set up consumer
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue=self.queue_name,
            on_message_callback=self.process_message
        )
        
        logger.info("Starting to consume messages...")
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            logger.info("Stopping consumer...")
            self.channel.stop_consuming()
            if self.connection and not self.connection.is_closed:
                self.connection.close()


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Start consumer
    consumer = EventConsumer()
    consumer.start_consuming()
