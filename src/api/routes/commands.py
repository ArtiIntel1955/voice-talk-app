"""Voice Commands API Routes"""

from fastapi import APIRouter, HTTPException

from ..api.schemas import CommandExecuteRequest, CommandExecuteResponse
from ..ai.commands.registry import get_command_registry
from ..config.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/commands", tags=["commands"])


@router.post("/execute", response_model=CommandExecuteResponse)
async def execute_command(request: CommandExecuteRequest):
    """
    Execute a voice command

    Args:
        request: Command execution request
    """
    try:
        registry = get_command_registry()

        # Execute command
        success, message, result = registry.execute_command(
            request.command,
            parameter=request.parameters.get("target", "") if request.parameters else "",
            require_confirmation=request.require_confirmation
        )

        return CommandExecuteResponse(
            status="success" if success else "failed",
            command=request.command,
            message=message,
            result=result
        )

    except Exception as e:
        logger.error(f"Error executing command: {e}")
        raise HTTPException(status_code=500, detail=f"Command error: {str(e)}")


@router.get("/list")
async def list_commands():
    """List available voice commands"""
    try:
        registry = get_command_registry()
        commands = registry.list_commands()

        return {
            "count": len(commands),
            "commands": commands
        }

    except Exception as e:
        logger.error(f"Error listing commands: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/search")
async def search_commands(query: str):
    """
    Search for matching commands

    Args:
        query: User input query
    """
    try:
        registry = get_command_registry()
        result = registry.search_command(query)

        if not result:
            return {
                "found": False,
                "message": f"No command found for: {query}"
            }

        command, parameter = result

        return {
            "found": True,
            "command_name": command.name,
            "command_description": command.description,
            "parameter": parameter,
            "requires_confirmation": command.requires_confirmation
        }

    except Exception as e:
        logger.error(f"Error searching commands: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/status")
async def get_command_status():
    """Get voice command system status"""
    try:
        registry = get_command_registry()

        return {
            "enabled": True,
            "total_commands": len(registry.commands),
            "commands": [cmd.name for cmd in registry.commands.values()]
        }

    except Exception as e:
        logger.error(f"Error getting command status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
