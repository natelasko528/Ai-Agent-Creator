"""File system tools for the AI assistant."""
import os
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional
import aiofiles
import aiofiles.os


class FileReader:
    """Async file reading operations."""

    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path).resolve()

    async def read(self, file_path: str, encoding: str = "utf-8") -> Dict[str, Any]:
        """Read file contents asynchronously."""
        path = self._resolve(file_path)

        if not path.exists():
            return {"success": False, "error": f"File not found: {file_path}"}

        try:
            async with aiofiles.open(path, "r", encoding=encoding) as f:
                content = await f.read()

            return {
                "success": True,
                "content": content,
                "path": str(path),
                "size": path.stat().st_size,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def read_lines(
        self,
        file_path: str,
        start: int = 0,
        count: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Read specific lines from a file."""
        path = self._resolve(file_path)

        if not path.exists():
            return {"success": False, "error": f"File not found: {file_path}"}

        try:
            async with aiofiles.open(path, "r") as f:
                lines = await f.readlines()

            if count is None:
                selected = lines[start:]
            else:
                selected = lines[start:start + count]

            return {
                "success": True,
                "lines": selected,
                "start": start,
                "count": len(selected),
                "total_lines": len(lines),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def search(
        self,
        pattern: str,
        file_path: str,
    ) -> Dict[str, Any]:
        """Search for a pattern in a file."""
        import re

        path = self._resolve(file_path)

        if not path.exists():
            return {"success": False, "error": f"File not found: {file_path}"}

        try:
            async with aiofiles.open(path, "r") as f:
                content = await f.read()

            matches = []
            for i, line in enumerate(content.splitlines(), 1):
                if re.search(pattern, line):
                    matches.append({"line": i, "content": line})

            return {
                "success": True,
                "matches": matches,
                "count": len(matches),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _resolve(self, file_path: str) -> Path:
        path = Path(file_path)
        if not path.is_absolute():
            path = self.base_path / path
        return path.resolve()


class FileWriter:
    """Async file writing operations."""

    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path).resolve()

    async def write(
        self,
        file_path: str,
        content: str,
        encoding: str = "utf-8",
    ) -> Dict[str, Any]:
        """Write content to a file."""
        path = self._resolve(file_path)

        try:
            path.parent.mkdir(parents=True, exist_ok=True)

            async with aiofiles.open(path, "w", encoding=encoding) as f:
                await f.write(content)

            return {
                "success": True,
                "path": str(path),
                "size": len(content.encode(encoding)),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def append(
        self,
        file_path: str,
        content: str,
        encoding: str = "utf-8",
    ) -> Dict[str, Any]:
        """Append content to a file."""
        path = self._resolve(file_path)

        try:
            path.parent.mkdir(parents=True, exist_ok=True)

            async with aiofiles.open(path, "a", encoding=encoding) as f:
                await f.write(content)

            return {
                "success": True,
                "path": str(path),
                "appended": len(content.encode(encoding)),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def delete(self, file_path: str) -> Dict[str, Any]:
        """Delete a file."""
        path = self._resolve(file_path)

        if not path.exists():
            return {"success": False, "error": f"File not found: {file_path}"}

        try:
            await aiofiles.os.remove(path)
            return {"success": True, "deleted": str(path)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def copy(self, src: str, dst: str) -> Dict[str, Any]:
        """Copy a file."""
        src_path = self._resolve(src)
        dst_path = self._resolve(dst)

        if not src_path.exists():
            return {"success": False, "error": f"Source not found: {src}"}

        try:
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dst_path)
            return {
                "success": True,
                "source": str(src_path),
                "destination": str(dst_path),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def move(self, src: str, dst: str) -> Dict[str, Any]:
        """Move a file."""
        src_path = self._resolve(src)
        dst_path = self._resolve(dst)

        if not src_path.exists():
            return {"success": False, "error": f"Source not found: {src}"}

        try:
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(src_path, dst_path)
            return {
                "success": True,
                "source": str(src_path),
                "destination": str(dst_path),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _resolve(self, file_path: str) -> Path:
        path = Path(file_path)
        if not path.is_absolute():
            path = self.base_path / path
        return path.resolve()
