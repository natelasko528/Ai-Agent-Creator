"""Code editing and execution tools."""
import asyncio
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class CodeEditRequest(BaseModel):
    """Request model for code editing."""
    file_path: str
    old_content: str
    new_content: str
    description: str = ""


class CodeRunRequest(BaseModel):
    """Request model for code execution."""
    code: str
    language: str = "python"
    timeout: int = 30


class CodeEditor:
    """Tool for editing code files with precise modifications."""

    def __init__(self, workspace_path: str = "."):
        self.workspace = Path(workspace_path).resolve()

    async def read_file(self, file_path: str) -> Dict[str, Any]:
        """Read a file and return its contents."""
        path = self._resolve_path(file_path)

        if not path.exists():
            return {"success": False, "error": f"File not found: {file_path}"}

        try:
            content = path.read_text(encoding="utf-8")
            return {
                "success": True,
                "content": content,
                "lines": len(content.splitlines()),
                "path": str(path),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def write_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Write content to a file."""
        path = self._resolve_path(file_path)

        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            return {
                "success": True,
                "path": str(path),
                "lines": len(content.splitlines()),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def edit_file(
        self,
        file_path: str,
        old_content: str,
        new_content: str,
    ) -> Dict[str, Any]:
        """Edit a file by replacing old content with new content."""
        path = self._resolve_path(file_path)

        if not path.exists():
            return {"success": False, "error": f"File not found: {file_path}"}

        try:
            current = path.read_text(encoding="utf-8")

            if old_content not in current:
                return {
                    "success": False,
                    "error": "Old content not found in file",
                }

            updated = current.replace(old_content, new_content, 1)
            path.write_text(updated, encoding="utf-8")

            return {
                "success": True,
                "path": str(path),
                "changes": 1,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def list_files(
        self,
        pattern: str = "**/*",
        exclude_dirs: list = None,
    ) -> Dict[str, Any]:
        """List files matching a pattern."""
        exclude = set(exclude_dirs or [".git", "__pycache__", "node_modules", ".venv"])

        try:
            files = []
            for path in self.workspace.glob(pattern):
                if path.is_file() and not any(e in path.parts for e in exclude):
                    files.append(str(path.relative_to(self.workspace)))

            return {
                "success": True,
                "files": sorted(files),
                "count": len(files),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _resolve_path(self, file_path: str) -> Path:
        """Resolve a file path relative to workspace."""
        path = Path(file_path)
        if not path.is_absolute():
            path = self.workspace / path
        return path.resolve()


class CodeRunner:
    """Tool for executing code safely."""

    SUPPORTED_LANGUAGES = {
        "python": {"cmd": ["python3", "-c"], "ext": ".py"},
        "javascript": {"cmd": ["node", "-e"], "ext": ".js"},
        "bash": {"cmd": ["bash", "-c"], "ext": ".sh"},
        "typescript": {"cmd": ["npx", "ts-node", "-e"], "ext": ".ts"},
    }

    def __init__(self, timeout: int = 30, sandbox: bool = True):
        self.timeout = timeout
        self.sandbox = sandbox

    async def run_code(
        self,
        code: str,
        language: str = "python",
        timeout: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Execute code and return the result."""
        if language not in self.SUPPORTED_LANGUAGES:
            return {
                "success": False,
                "error": f"Unsupported language: {language}",
                "supported": list(self.SUPPORTED_LANGUAGES.keys()),
            }

        lang_config = self.SUPPORTED_LANGUAGES[language]
        timeout = timeout or self.timeout

        try:
            # Run in subprocess
            process = await asyncio.create_subprocess_exec(
                *lang_config["cmd"],
                code,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout,
            )

            return {
                "success": process.returncode == 0,
                "stdout": stdout.decode("utf-8"),
                "stderr": stderr.decode("utf-8"),
                "return_code": process.returncode,
            }
        except asyncio.TimeoutError:
            process.kill()
            return {
                "success": False,
                "error": f"Execution timed out after {timeout}s",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def run_file(
        self,
        file_path: str,
        args: list = None,
        timeout: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Execute a file and return the result."""
        path = Path(file_path)

        if not path.exists():
            return {"success": False, "error": f"File not found: {file_path}"}

        # Determine language from extension
        ext = path.suffix
        language = None
        for lang, config in self.SUPPORTED_LANGUAGES.items():
            if config["ext"] == ext:
                language = lang
                break

        if language is None:
            return {"success": False, "error": f"Unknown file type: {ext}"}

        code = path.read_text(encoding="utf-8")
        return await self.run_code(code, language, timeout)


# Function tools for ADK integration
async def read_file(file_path: str) -> Dict[str, Any]:
    """Read a file and return its contents.

    Args:
        file_path: Path to the file to read

    Returns:
        Dictionary with file contents or error
    """
    editor = CodeEditor()
    return await editor.read_file(file_path)


async def write_file(file_path: str, content: str) -> Dict[str, Any]:
    """Write content to a file.

    Args:
        file_path: Path to the file to write
        content: Content to write to the file

    Returns:
        Dictionary with success status
    """
    editor = CodeEditor()
    return await editor.write_file(file_path, content)


async def edit_file(
    file_path: str,
    old_content: str,
    new_content: str,
) -> Dict[str, Any]:
    """Edit a file by replacing content.

    Args:
        file_path: Path to the file to edit
        old_content: Content to replace
        new_content: New content to insert

    Returns:
        Dictionary with success status
    """
    editor = CodeEditor()
    return await editor.edit_file(file_path, old_content, new_content)


async def run_code(
    code: str,
    language: str = "python",
) -> Dict[str, Any]:
    """Execute code and return the result.

    Args:
        code: Code to execute
        language: Programming language (python, javascript, bash, typescript)

    Returns:
        Dictionary with execution result
    """
    runner = CodeRunner()
    return await runner.run_code(code, language)
