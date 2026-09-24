"""Data models and validation schemas using Pydantic.

This module defines the request and response schemas for the Product/Item
Processing API, enforcing strict data types, positive values, and required constraints.
"""

from pydantic import BaseModel, Field


class ItemCreate(BaseModel):
    """Request schema for creating and processing an item.

    Validates:
    - name: Required, between 2 and 100 characters.
    - quantity: Required, strictly positive integer (> 0).
    - price: Required, strictly positive float (> 0.0).
    """

    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Name of the product or item",
        examples=["Laptop"],
    )
    quantity: int = Field(
        ...,
        gt=0,
        description="Quantity of the item (must be a positive integer)",
        examples=[2],
    )
    price: float = Field(
        ...,
        gt=0.0,
        description="Unit price of the item (must be greater than 0)",
        examples=[75000.0],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Laptop",
                "quantity": 2,
                "price": 75000.0,
            }
        }
    }


class ItemResponse(BaseModel):
    """Response schema returned after item processing.

    Includes processed details, computed total price, unique transaction ID,
    timestamp, and whether synchronous or asynchronous handling was used.
    """

    id: str = Field(..., description="Unique generated transaction identifier")
    name: str = Field(..., description="Item name")
    quantity: int = Field(..., description="Item quantity")
    price: float = Field(..., description="Item unit price")
    total_price: float = Field(..., description="Calculated total price (quantity * price)")
    status: str = Field(..., description="Processing status (e.g., 'completed')")
    processing_type: str = Field(..., description="Mode of processing: 'sync' or 'async'")
    processed_at: str = Field(..., description="ISO 8601 formatted processing timestamp")
    message: str = Field(..., description="Informational message regarding the operation")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "e3b0c442-98fc-1c14-9afb-4c7b887a0001",
                "name": "Laptop",
                "quantity": 2,
                "price": 75000.0,
                "total_price": 150000.0,
                "status": "completed",
                "processing_type": "async",
                "processed_at": "2026-09-24T17:49:33.123456Z",
                "message": "Item Laptop processed successfully via async pipeline.",
            }
        }
    }
