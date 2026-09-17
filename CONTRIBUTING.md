# Contributing

Thank you for your interest in contributing to the Nvisy Python SDK.

## Requirements

- Python 3.11 or higher
- uv (recommended) or pip
- ruff for linting and formatting
- mypy for type checking

## Development Setup

```bash
git clone https://github.com/your-username/sdk-py.git
cd sdk-py
make setup
```

## Development

### Scripts

- `make build` - Build the package for distribution
- `make dev` - Run development checks (format + lint + test)
- `make test` - Run test suite
- `make test-cov` - Run tests with coverage report
- `make security` - Audit dependencies and run static analysis
- `make lint` - Check code style and quality
- `make format` - Format code with ruff
- `make check` - Run all linting, formatting, and type checks
- `make type-check` - Verify type hints with mypy
- `make clean` - Remove build artifacts

### Quality Checks

Before submitting changes:

```bash
make check    # Lint, format, and type check
make test     # Run test suite
make build    # Verify build works
```

## Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run quality checks: `make check`
6. Submit a pull request

### Pull Request Checklist

- [ ] Tests pass
- [ ] Code follows project style
- [ ] Type hints are correct
- [ ] Documentation updated if needed
- [ ] No breaking changes (or documented)

## Code Standards

- Follow existing Python patterns and PEP 8
- Use type hints for all public APIs
- Write tests for new features
- Include docstrings for public APIs
- Follow semantic versioning for changes
- Use ruff for code formatting and linting
- Maintain backwards compatibility when possible

## Testing

- Write unit tests for new functionality
- Use pytest for testing framework
- Include both async and sync test cases where applicable
- Mock external dependencies in unit tests
- Integration tests should use real API endpoints when possible

## Documentation

- Update README.md for user-facing changes
- Add docstrings to all public classes and methods
- Use Google-style docstrings for consistency
- Update type hints when changing function signatures

## License

By contributing, you agree your contributions will be licensed under the MIT
License.
