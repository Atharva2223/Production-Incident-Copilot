from pydantic import BaseModel, Field


class IndexLogsRequest(BaseModel):
    file_path: str = Field(..., description="Path to the log file to index")
    chroma_path: str = Field(
        default="chroma_db",
        description="Path to the ChromaDB storage directory",
    )
    collection_name: str = Field(
        default="log_chunks",
        description="ChromaDB collection name",
    )
    window_seconds: int = Field(
        default=60,
        description="Time window in seconds for chunking logs",
    )


class IndexLogsResponse(BaseModel):
    message: str
    total_records: int
    total_chunks: int
    total_embedded_chunks: int


class AnalyzeRequest(BaseModel):
    question: str = Field(..., description="User question about the logs")
    n_results: int = Field(
        default=3,
        description="Number of relevant chunks to retrieve",
    )
    chroma_path: str = Field(
        default="chroma_db",
        description="Path to the ChromaDB storage directory",
    )
    collection_name: str = Field(
        default="log_chunks",
        description="ChromaDB collection name",
    )