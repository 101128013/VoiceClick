"""
Auto-update system for VoiceClick.

Checks for updates and handles the update process.
"""

import logging
import json
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional, Dict
from dataclasses import dataclass

from src.config import constants

logger = logging.getLogger(__name__)


@dataclass
class UpdateInfo:
    """Information about an available update."""
    version: str
    download_url: str
    changelog: str
    release_date: str
    is_available: bool = False


class Updater:
    """
    Handles checking for and downloading updates.
    
    Supports both GitHub Releases and custom update servers.
    """
    
    def __init__(self, update_url: Optional[str] = None, check_on_startup: bool = True):
        """
        Initializes the Updater.
        
        Args:
            update_url: URL to check for updates (GitHub Releases API or custom endpoint)
            check_on_startup: Whether to check for updates on startup
        """
        self.current_version = constants.APP_VERSION
        self.update_url = update_url or self._get_default_update_url()
        self.check_on_startup = check_on_startup
        self.update_info: Optional[UpdateInfo] = None
    
    def _get_default_update_url(self) -> str:
        """Gets the default update URL (GitHub Releases API)."""
        # Update this with your actual GitHub repository
        # Format: "username/repository"
        repo = "your-username/VoiceClick"  # TODO: Update this with your actual repo
        return f"https://api.github.com/repos/{repo}/releases/latest"
    
    def check_for_updates(self) -> Optional[UpdateInfo]:
        """
        Checks for available updates.
        
        Returns:
            UpdateInfo if update is available, None otherwise
        """
        try:
            logger.info(f"Checking for updates from {self.update_url}")
            
            # Create request with user agent
            req = urllib.request.Request(
                self.update_url,
                headers={'User-Agent': f'VoiceClick/{self.current_version}'}
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
            
            # Parse GitHub Releases format
            if 'tag_name' in data:
                latest_version = data['tag_name'].lstrip('v')
                download_url = None
                
                # Find Windows installer in assets
                for asset in data.get('assets', []):
                    if 'Setup' in asset['name'] and asset['name'].endswith('.exe'):
                        download_url = asset['browser_download_url']
                        break
                
                if download_url and self._is_newer_version(latest_version):
                    self.update_info = UpdateInfo(
                        version=latest_version,
                        download_url=download_url,
                        changelog=data.get('body', ''),
                        release_date=data.get('published_at', ''),
                        is_available=True
                    )
                    logger.info(f"Update available: {latest_version}")
                    return self.update_info
            
            logger.info("No updates available")
            return None
            
        except urllib.error.URLError as e:
            logger.warning(f"Failed to check for updates: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse update response: {e}")
            return None
        except Exception as e:
            logger.error(f"Error checking for updates: {e}", exc_info=True)
            return None
    
    def _is_newer_version(self, version: str) -> bool:
        """
        Compares version strings to determine if the new version is newer.
        
        Args:
            version: Version string to compare (e.g., "1.1.0")
            
        Returns:
            True if version is newer than current version
        """
        try:
            current_parts = [int(x) for x in self.current_version.split('.')]
            new_parts = [int(x) for x in version.split('.')]
            
            # Pad to same length
            max_len = max(len(current_parts), len(new_parts))
            current_parts.extend([0] * (max_len - len(current_parts)))
            new_parts.extend([0] * (max_len - len(new_parts)))
            
            return new_parts > current_parts
        except Exception:
            logger.warning(f"Could not compare versions: {self.current_version} vs {version}")
            return False
    
    def download_update(self, download_path: Optional[Path] = None) -> Optional[Path]:
        """
        Downloads the update installer.
        
        Args:
            download_path: Optional path to save the installer
            
        Returns:
            Path to downloaded file, or None if download failed
        """
        if not self.update_info or not self.update_info.is_available:
            logger.error("No update available to download")
            return None
        
        try:
            if download_path is None:
                download_path = Path.home() / '.voice_click' / f'VoiceClick-Setup-v{self.update_info.version}.exe'
            
            download_path.parent.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Downloading update from {self.update_info.download_url}")
            
            urllib.request.urlretrieve(
                self.update_info.download_url,
                download_path
            )
            
            logger.info(f"Update downloaded to {download_path}")
            return download_path
            
        except Exception as e:
            logger.error(f"Failed to download update: {e}", exc_info=True)
            return None
    
    def get_changelog(self) -> str:
        """Gets the changelog for the available update."""
        if self.update_info:
            return self.update_info.changelog
        return ""

