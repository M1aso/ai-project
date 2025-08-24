"""
RabbitMQ-based event publisher for auth service.
Handles publishing events to other services via message queue.
"""
import json
import logging
import os
from typing import Dict, Any, Optional
import pika
from pika.exceptions import AMQPConnectionError, AMQPChannelError

logger = logging.getLogger(__name__)


class EventPublisher:
    """RabbitMQ event publisher for inter-service communication."""
    
    def __init__(self):
        self.connection: Optional[pika.BlockingConnection] = None
        self.channel: Optional[pika.channel.Channel] = None
        self.rabbitmq_url = os.getenv(
            "RABBITMQ_URL", 
            "amqp://admin:admin123@rabbitmq.rabbitmq.svc.cluster.local:5672"
        )
        self.exchange_name = "ai_project_events"
        self._setup_connection()
    
    def _setup_connection(self):
        """Setup RabbitMQ connection and exchange."""
        try:
            # Parse RabbitMQ URL
            parameters = pika.URLParameters(self.rabbitmq_url)
            
            # Create connection
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            # Declare exchange (topic exchange for routing)
            self.channel.exchange_declare(
                exchange=self.exchange_name,
                exchange_type='topic',
                durable=True
            )
            
            logger.info(f"Successfully connected to RabbitMQ at {self.rabbitmq_url}")
            
        except AMQPConnectionError as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            self.connection = None
            self.channel = None
        except Exception as e:
            logger.error(f"Unexpected error setting up RabbitMQ: {e}")
            self.connection = None
            self.channel = None
    
    def publish_event(self, routing_key: str, event_data: Dict[str, Any]) -> bool:
        """
        Publish an event to RabbitMQ.
        
        Args:
            routing_key: The routing key for the event (e.g., 'user.registered')
            event_data: The event payload data
            
        Returns:
            bool: True if published successfully, False otherwise
        """
        if not self.channel or not self.connection or self.connection.is_closed:
            logger.warning("RabbitMQ connection not available, attempting to reconnect...")
            self._setup_connection()
            
        if not self.channel:
            logger.error("Cannot publish event - RabbitMQ connection failed")
            return False
        
        try:
            # Prepare message
            message = {
                "event_type": routing_key,
                "data": event_data,
                "source": "auth-service"
            }
            
            # Publish message
            self.channel.basic_publish(
                exchange=self.exchange_name,
                routing_key=routing_key,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                    content_type='application/json'
                )
            )
            
            logger.info(f"Published event: {routing_key} with data: {event_data}")
            return True
            
        except AMQPChannelError as e:
            logger.error(f"Channel error publishing event {routing_key}: {e}")
            return False
        except Exception as e:
            logger.error(f"Error publishing event {routing_key}: {e}")
            return False
    
    def close(self):
        """Close RabbitMQ connection."""
        try:
            if self.connection and not self.connection.is_closed:
                self.connection.close()
                logger.info("RabbitMQ connection closed")
        except Exception as e:
            logger.error(f"Error closing RabbitMQ connection: {e}")


# Global event publisher instance
_event_publisher: Optional[EventPublisher] = None


def get_event_publisher() -> EventPublisher:
    """Get the global event publisher instance."""
    global _event_publisher
    if _event_publisher is None:
        _event_publisher = EventPublisher()
    return _event_publisher


def publish_user_registered(email: str, name: str = None) -> bool:
    """Publish user registration event."""
    event_data = {"email": email}
    if name:
        event_data["name"] = name
    
    publisher = get_event_publisher()
    return publisher.publish_event("user.registered", event_data)


def publish_password_reset(email: str, name: str = None) -> bool:
    """Publish password reset event."""
    event_data = {"email": email}
    if name:
        event_data["name"] = name
    
    publisher = get_event_publisher()
    return publisher.publish_event("auth.password_reset", event_data)
