import logging
from dotenv import load_dotenv
from livekit import agents, rtc
from livekit.agents import AgentServer, AgentSession, room_io, JobContext
from livekit.plugins import (
    google,
    noise_cancellation,
)

from assistant import Assistant
from utils import Utils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gemini-lk")


class JobHandler:
    def __init__(self) -> None:
        self.utils = Utils()

    async def handle_job(self, ctx: JobContext) -> None:
        logger.info(f"Starting job handling for room: {ctx.room.name}")

        try:
            await ctx.connect()

            session = AgentSession(
                llm=google.realtime.RealtimeModel(
                    voice="Achird",
                    temperature=0.8,
                    model="gemini-live-2.5-flash-native-audio",
                    vertexai=True,
                ),
            )

            await session.start(
                room=ctx.room,
                agent=Assistant(self.utils),
                room_options=room_io.RoomOptions(
                    audio_input=room_io.AudioInputOptions(
                        noise_cancellation=lambda params: (
                            noise_cancellation.BVCTelephony()
                            if params.participant.kind
                            == rtc.ParticipantKind.PARTICIPANT_KIND_SIP
                            else noise_cancellation.BVC()
                        ),
                    ),
                ),
            )

            logger.info("Agent session started, generating initial reply")
            await session.generate_reply(
                instructions="Greet the customer in Sinhala: Ayubhowan, Mama Nilan Hutch paribogika sewa anshayen. obata sahaya wanne keseda?"
            )
        except Exception as e:
            logger.error(f"Error starting session: {e}", exc_info=True)
            raise


async def entrypoint(ctx: JobContext) -> None:
    logger.info(f"Received job request: {ctx.job.id}")
    handler = JobHandler()
    await handler.handle_job(ctx)


class Main:
    def __init__(self) -> None:
        load_dotenv(".env.local")
        self.server = AgentServer()
        self._register_handlers()
        logger.info("Main application initialized")

    def _register_handlers(self) -> None:
        self.server.rtc_session()(entrypoint)
        logger.info("RTC session handlers registered")

    def run(self) -> None:
        logger.info("Starting AgentServer")
        agents.cli.run_app(self.server)


if __name__ == "__main__":
    Main().run()
