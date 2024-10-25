from tenacity import (
    retry,
    stop_after_attempt,
    stop_after_delay,
    wait_exponential,
    wait_random,
    retry_if_exception_type,
    retry_if_result,
    before_sleep_log,
    RetryError
)
import logging
from typing import TypeVar, Callable, Optional, Any
from functools import wraps

T = TypeVar('T')  # Generic type for function return value

def make_retriable(
    max_attempts: int = 3,
    max_delay: int = 60,
    min_wait: float = 1,
    max_wait: float = 10,
    exception_types: tuple = (Exception,),
    retry_on_result: Optional[Callable[[Any], bool]] = None,
    logger: Optional[logging.Logger] = None,
) -> Callable:
    """
    Decorator to make any function retriable with configurable retry behavior.
    
    Args:
        max_attempts: Maximum number of retry attempts
        max_delay: Maximum total delay in seconds
        min_wait: Minimum wait time between retries in seconds
        max_wait: Maximum wait time between retries in seconds
        exception_types: Tuple of exception types to retry on
        retry_on_result: Optional function that takes the result and returns True if retry is needed
        logger: Optional logger instance for retry logging
    
    Returns:
        Decorated function with retry behavior
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        # Use provided logger or default one
        retry_logger = logger or logging.getLogger(__name__)
        
        # Configure retry behavior
        @retry(
            # Stop conditions (whichever comes first)
            stop=(
                stop_after_attempt(max_attempts) |
                stop_after_delay(max_delay)
            ),
            # Wait behavior - exponential backoff with random jitter
            wait=wait_exponential(multiplier=min_wait, max=max_wait) + wait_random(0, 1),
            # Retry conditions
            retry=(
                retry_if_exception_type(exception_types) |
                (retry_if_result(retry_on_result) if retry_on_result else retry_if_exception_type(()))
            ),
            # Logging
            before_sleep=before_sleep_log(retry_logger, logging.WARNING),
            # Reraise the original exception
            reraise=True
        )
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            try:
                return func(*args, **kwargs)
            except RetryError as retry_err:
                # Log the final failure
                retry_logger.error(
                    f"All retry attempts failed for {func.__name__}. "
                    f"Final exception: {retry_err.last_attempt.exception()}"
                )
                raise
        
        return wrapper
    
    return decorator

# Example usage with different retry scenarios
# class RetryExamples:
#     @make_retriable(
#         max_attempts=3,
#         exception_types=(ConnectionError, TimeoutError)
#     )
#     def unstable_network_call(self, url: str) -> str:
#         """Example of retrying network calls."""
#         # Simulate unstable network
#         if random.random() < 0.7:  # 70% chance of failure
#             raise ConnectionError("Network unstable")
#         return f"Success: {url}"
    
#     @make_retriable(
#         max_attempts=5,
#         min_wait=0.1,
#         max_wait=1,
#         retry_on_result=lambda x: x is None
#     )
#     def wait_for_resource(self, resource_id: str) -> Optional[dict]:
#         """Example of retrying until a resource is available."""
#         # Simulate resource check
#         if random.random() < 0.8:  # 80% chance resource isn't ready
#             return None
#         return {"id": resource_id, "status": "ready"}
    
#     @make_retriable(
#         max_attempts=3,
#         exception_types=(ValueError,),
#         retry_on_result=lambda x: x < 0
#     )
#     def process_with_validation(self, value: int) -> int:
#         """Example of retrying on both exceptions and result conditions."""
#         # Simulate processing that might fail or return invalid results
#         result = value * random.randint(-1, 1)
#         if result == 0:
#             raise ValueError("Invalid result")
#         return result

# # Custom exception for database errors
# class DatabaseError(Exception):
#     pass

# # Example of a more complex retry scenario
# @make_retriable(
#     max_attempts=5,
#     min_wait=0.5,
#     max_wait=5,
#     exception_types=(DatabaseError, ConnectionError),
#     retry_on_result=lambda x: not x.get('success', False)
# )
# def database_operation(query: str, retries_left: int = 3) -> dict:
#     """
#     Example of a database operation with custom retry logic.
    
#     Args:
#         query: SQL query to execute
#         retries_left: Number of retries left (for demonstration)
    
#     Returns:
#         Dict containing operation result
#     """
#     # Simulate database operation that might fail
#     if retries_left > 0:
#         if random.random() < 0.5:
#             raise DatabaseError("Database connection lost")
#         if random.random() < 0.3:
#             return {"success": False, "error": "Deadlock detected"}
        
#     return {
#         "success": True,
#         "result": f"Query executed: {query}",
#         "timestamp": time.time()
#     }