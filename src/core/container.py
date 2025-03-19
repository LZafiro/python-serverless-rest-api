from typing import Dict, Any, Type, Callable
import inspect
from functools import wraps

class DIContainer:
    """
    DI Container
    """
    _instance = None
    _services: Dict[Type, Dict[str, Any]] = {}
    _instances: Dict[Type, Any] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DIContainer, cls).__new__(cls)
            # Initialize the dictionaries if they haven t been already
            cls._instance._services = {}
            cls._instance._instances = {}
        return cls._instance

    def register(self, interface: Type, implementation: Type | None = None, **kwargs):
        """
        Register a service implementation with the container.

        Args:
            interface: The interface/class type to register
            implementation: The concrete implementation class (optional if same as interface)
            **kwargs: Additional arguments to pass to the implementation constructor
        """
        if implementation is None:
            implementation = interface

        self._services[interface] = {
            'implementation': implementation,
            'kwargs': kwargs
        }

        # clear cached instance if it exists
        if interface in self._instances:
            del self._instances[interface]

        return self

    def resolve(self, interface: Type) -> Any:
        """
        Resolve an implementation for the requested interface.

        Args:
            interface: The interface/class type to resolve

        Returns:
            An instance of the registered implementation
        """
        # Return cached instance if available
        if interface in self._instances:
            return self._instances[interface]

        if interface not in self._services:
            raise KeyError(f"No implementation registered for {interface.__name__}")

        service_info = self._services[interface]
        implementation = service_info['implementation']
        kwargs = service_info['kwargs']

        # Handle constructor dependencies by inspecting the signature
        constructor_params = inspect.signature(implementation.__init__).parameters

        # Skip 'self' parameter
        constructor_params = {k: v for k, v in constructor_params.items() if k != 'self'}

        # Resolve dependencies
        for param_name, param in constructor_params.items():
            # If the parameter is not provided in kwargs and has a type annotation
            if param_name not in kwargs and param.annotation != inspect.Parameter.empty:
                try:
                    # Try to resolve the dependency from the container
                    kwargs[param_name] = self.resolve(param.annotation)
                except KeyError:
                    # If dependency cannot be resolved and is not optional
                    if param.default == inspect.Parameter.empty:
                        raise ValueError(f"Cannot resolve dependency {param_name} of type {param.annotation}")

        # Create the instance
        instance = implementation(**kwargs)

        # Cache the instance
        self._instances[interface] = instance

        return instance

    def inject(self, func):
        """
        Decorator to inject dependencies into function parameters.

        Args:
            func: The function to inject dependencies into

        Returns:
            A wrapped function with dependencies injected
        """
        signature = inspect.signature(func)

        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get the parameters that aren't supplied
            bound_args = signature.bind_partial(*args, **kwargs)
            remaining_params = {
                name: param for name, param in signature.parameters.items()
                if name not in bound_args.arguments
            }

            # Resolve the dependencies for the remaining parameters
            for name, param in remaining_params.items():
                if param.annotation != inspect.Parameter.empty:
                    try:
                        kwargs[name] = self.resolve(param.annotation)
                    except KeyError:
                        # Skip if parameter has a default value
                        if param.default == inspect.Parameter.empty:
                            raise ValueError(f"Cannot resolve dependency {name} of type {param.annotation}")

            return func(*args, **kwargs)

        return wrapper

    def clear(self):
        """Clear all registered services and cached instances."""
        self._services.clear()
        self._instances.clear()
