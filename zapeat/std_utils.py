from rest_framework.response import Response
from rest_framework import status
from typing import Any, Dict, Optional
from rest_framework.pagination import PageNumberPagination

class CustomAPIModule:
    """
    A base class for standardizing API responses across views.
    Provides consistent response structure and helper methods for common API operations.
    """

    @staticmethod
    def create_response(
            data: Any = None,
            message: str = "",
            success: bool = True,
            status_code: int = status.HTTP_200_OK,
            errors: Optional[Dict] = None,
            meta: Optional[Dict] = None
    ) -> Response:
        """
        Creates a standardized response format for all API endpoints.

        Args:
            data: The main response data
            message: A human-readable message about the response
            success: Boolean indicating if the operation was successful
            status_code: HTTP status code for the response
            errors: Dictionary of validation or processing errors
            meta: Additional metadata like pagination info

        Returns:
            DRF Response object with standardized format
        """
        response_data = {
            "success": success,
            "message": message,
            "data": data or {},
            "errors": errors or {},
            "meta": meta or {}
        }

        return Response(response_data, status=status_code)

    def success_response(
            self,
            data: Any = None,
            message: str = "Operation successful",
            status_code: int = status.HTTP_200_OK,
            meta: Optional[Dict] = None
    ) -> Response:
        """Helper method for successful responses"""
        return self.create_response(
            data=data,
            message=message,
            success=True,
            status_code=status_code,
            meta=meta
        )

    def error_response(
            self,
            message: str = "Operation failed",
            errors: Optional[Dict] = None,
            status_code: int = status.HTTP_400_BAD_REQUEST,
            data: Any = None
    ) -> Response:
        """Helper method for error responses"""
        return self.create_response(
            data=data,
            message=message,
            success=False,
            status_code=status_code,
            errors=errors
        )

    def not_found_response(
            self,
            message: str = "Resource not found",
            errors: Optional[Dict] = None
    ) -> Response:
        """Helper method for 404 responses"""
        return self.create_response(
            message=message,
            success=False,
            status_code=status.HTTP_404_NOT_FOUND,
            errors=errors
        )

    def validation_error_response(
            self,
            errors: Dict,
            message: str = "Validation failed"
    ) -> Response:
        """Helper method for validation error responses"""
        return self.create_response(
            message=message,
            success=False,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            errors=errors
        )
    
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
