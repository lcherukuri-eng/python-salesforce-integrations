from pathlib import Path
from app.pubsub import(   
    pubsub_api_pb2, 
    pubsub_api_pb2_grpc
)
from app.dependencies import get_sf_token
import asyncio
import grpc
import time
import os
import io
import json
from fastavro import schemaless_reader
import logging

logger = logging.getLogger(__name__)

class CustomerActivityConsumer:
    """Consumes Salesforce Customer Activity Platform Events."""    
    
    TOPIC_NAME = "/event/Customer_Activity__e"

    REPLAY_FILE = (
        Path(__file__).parent
        / "data"
        / "replay_id.txt"
    )

    def __init__(self):
            self.access_token = None
            self.instance_url = None
            self.stub = None
            self.schema_cache = {}
    

    def get_last_replay_id(self):
        if self.REPLAY_FILE.exists():
            return self.REPLAY_FILE.read_text().strip()
        return None

    def save_replay_id(self, replay_id):
        self.REPLAY_FILE.write_text(str(replay_id))

    async def authenticate(self):
        token = get_sf_token()

        self.access_token = token["access_token"]
        self.instance_url = token["instance_url"]

        return token
    

    async def create_stub(self): 
        channel = grpc.secure_channel(
            "api.pubsub.salesforce.com:7443",
            grpc.ssl_channel_credentials()
        )

        self.stub = pubsub_api_pb2_grpc.PubSubStub(channel)
        logger.info("PubSubStub created")
   

    def request_generator(self):
        last_replay_id = self.get_last_replay_id()

        if last_replay_id:
            logger.info("Using saved replay id: %s", last_replay_id)

            yield pubsub_api_pb2.FetchRequest(
                topic_name=self.TOPIC_NAME,
                replay_preset=pubsub_api_pb2.ReplayPreset.CUSTOM,
                replay_id=bytes.fromhex(last_replay_id),
                num_requested=1
            )

        else:
            logger.info("No replay id found. Using LATEST")

            yield pubsub_api_pb2.FetchRequest(
                topic_name=self.TOPIC_NAME,
                replay_preset=pubsub_api_pb2.ReplayPreset.LATEST,
                num_requested=1
            )

        while True:
            time.sleep(30)

            yield pubsub_api_pb2.FetchRequest(
                num_requested=1
            )


    async def get_schema_json(self, schema_id):
        if schema_id not in self.schema_cache:
            logger.info("Schema cache miss for schema_id=%s", schema_id)

            schema = await self.get_schema(schema_id)

            self.schema_cache[schema_id] = schema.schema_json

        else:
            logger.info("Schema cache hit for schema_id=%s", schema_id)

        return self.schema_cache[schema_id]
    

    async def subscribe(self):
        logger.info("Starting subscription")

        metadata = self.get_metadata()

        responses = self.stub.Subscribe(
            self.request_generator(),
            metadata=metadata
        )
        
        logger.info("Subscription established")

        try:
            logger.info("Waiting for responses...")
            for response in responses:  

                for event in response.events:
                    self.save_replay_id(event.replay_id.hex())

                    schema_json = await self.get_schema_json(
                        event.event.schema_id
                    )

                    decoded_event = await self.decode_payload(
                        event.event.payload,
                        schema_json
                    )

                    await self.process_event(decoded_event)                   

            logger.info(
                "Subscription stream ended. Code=%s Details=%s",
                responses.code(),
                responses.details()
            )


        except Exception as e:
            logger.exception("Subscription failed")


    def get_metadata(self):
        return (
            ("accesstoken", self.access_token),
            ("instanceurl", self.instance_url),
            ("tenantid", os.getenv("SF_ORG_ID"))
        )
    
    async def get_schema(self, schema_id):

        metadata = self.get_metadata()

        request = pubsub_api_pb2.SchemaRequest(
            schema_id=schema_id
        )

        response = self.stub.GetSchema(
            request,
            metadata=metadata
        )      

        return response

    async def decode_payload(self, payload, schema_json):

        parsed_schema = json.loads(schema_json)

        decoded_event = schemaless_reader(
            io.BytesIO(payload),
            parsed_schema
        )

        return decoded_event

    async def process_event(self, event):
        customer_id = event.get("Customer_Id__c")
        activity_type = event.get("Activity_Type__c")
        activity_source = event.get("Activity_Source__c")

        logger.info(
            "Customer=%s Activity=%s Source=%s",
            customer_id,
            activity_type,
            activity_source,
        )

    # Utility method for validating a topic and viewing topic metadata.
    async def get_topic(self):
        metadata = self.get_metadata()
    
        request = pubsub_api_pb2.TopicRequest(
            topic_name=self.TOPIC_NAME
        )
    
        response = self.stub.GetTopic(
            request,
            metadata=metadata
        )
    
        logger.info(
            "Topic=%s Publish=%s Subscribe=%s SchemaId=%s",
            response.topic_name,
            response.can_publish,
            response.can_subscribe,
            response.schema_id,
        )


async def main():
    consumer = CustomerActivityConsumer()
    await consumer.authenticate()
    await consumer.create_stub()
    await consumer.subscribe()   

if __name__ == "__main__":
    asyncio.run(main())
