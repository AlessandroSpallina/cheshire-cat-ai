import logging

from fastapi import Query, Request, APIRouter
from typing import Dict

router = APIRouter()


# DELETE delete_memories
@router.delete("/delete/{memory_id}/")
async def delete_memories(memory_id: str) -> Dict:
    """Delete specific memory."""
    return {"error": "to be implemented"}


# GET recall_memories
@router.get("/recall/")
async def recall_memories_from_text(
    request: Request,
    text: str = Query(description="Find memories similar to this text."),
    k: int = Query(default=100, description="How many memories to return."),
) -> Dict:
    """Search k memories similar to given text."""

    ccat = request.app.state.ccat
    vector_memory = ccat.memory.vectors

    episodes = vector_memory.episodic.recall_memories_from_text(text=text, k=k)
    documents = vector_memory.declarative.recall_memories_from_text(text=text, k=k)

    episodes = [dict(m[0]) | {"score": float(m[1])} for m in episodes]
    documents = [dict(m[0]) | {"score": float(m[1])} for m in documents]

    return (
        {
            "episodes": episodes,
            "documents": documents,
        },
    )


# DELETE one collection
@router.delete("/collection/{collection_id}")
async def collection(request: Request, collection_id: str = "") -> Dict:
    """Delete and create a collection """

    to_return = {}
    if collection_id != "":
        ccat = request.app.state.ccat
        vector_memory = ccat.memory.vectors
        
        ret = vector_memory.vector_db.delete_collection(collection_name=collection_id)
        logging.debug(ret)
        to_return[collection_id] = ret
            
        ccat.load_memory() # recreate the long term memories
        ccat.reset_history() # reset history conversation of the cat

    return (to_return)


# DELETE all collections
@router.delete("/wipe_collections/")
async def wipe_collections(
    request: Request,
) -> Dict:
    """Delete and create all collection and reset the history of the cat """


    ccat = request.app.state.ccat
    collections = list(ccat.memory.vectors.collections.keys())
    vector_memory = ccat.memory.vectors
    
    to_return = {}
    for c in collections:
        ret = vector_memory.vector_db.delete_collection(collection_name=c)
        logging.debug(ret)
        to_return[c] = ret
        
    ccat.load_memory() # recreate the long term memories
    ccat.reset_history() # reset history conversation of the cat

    return (to_return)
