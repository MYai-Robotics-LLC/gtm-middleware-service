import os
from datetime import timedelta
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from livekit import api
from typing import Optional, Dict, Any
from livekit.protocol.room import RoomConfiguration
from livekit.protocol.agent_dispatch import RoomAgentDispatch

router = APIRouter(prefix="/livekit")

class RequestData(BaseModel):
    room_name: str = Field(..., description='iveKit room name')
    participant_identity: str = Field(..., description="Unique participant identity")
    participant_name: Optional[str]	= Field(None, description="Display name shown to other participants")
    participant_metadata: Optional[str] = Field(None, description="Participant's metadata")
    participant_attributes: Optional[Dict[str, str]] = Field(..., description="Participant's attributes")
    room_config: Optional[Dict[str, Any]]	= Field(..., description='Room configuration')
    ttl: int = Field(3600, description="Token TTL in seconds", ge=60, le=86400)


@router.post("/tokens")
async def create_token(body: RequestData):
    def to_agent_dispatch(config: dict):
        return RoomAgentDispatch(agent_name=config['agent_name'], metadata=config['metadata'])

    token = (
        api.AccessToken()
        .with_identity(body.participant_identity)
        .with_name(body.participant_name or body.participant_identity)
        .with_grants(api.VideoGrants(room_join=True, room=body.room_name))
        .with_ttl(timedelta(seconds=body.ttl))
        .with_metadata(body.participant_metadata or '{}')
        .with_attributes(body.participant_attributes or {})
    )
    
    if body.room_config:
        token = token.with_room_config(RoomConfiguration(
            name=body.room_name,
            agents=list(map(to_agent_dispatch, body.room_config.get('agents'))),
            sync_streams=True
        ))

    return JSONResponse({
        'server_url': os.getenv('LIVEKIT_URL'),
        'participant_token': token.to_jwt(),
    }, 201)
