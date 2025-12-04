# Copyright (c) 2025 Special Agents
# Licensed under MIT License - See LICENSE file for details

"""
Special Agents Package (.sagent) handler
Validates, extracts, and processes agent packages
"""
import os
import yaml
import zipfile
import tempfile
import shutil
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class AgentPackageValidator:
    """Validates .sagent packages according to specification."""

    # Valid categories
    VALID_CATEGORIES = ['productivity', 'education', 'travel', 'health', 'finance', 'creative']

    # Max sizes
    MAX_PACKAGE_SIZE = 50 * 1024 * 1024  # 50MB
    MAX_SYSTEM_PROMPT_SIZE = 50000  # characters
    MIN_SYSTEM_PROMPT_SIZE = 100

    def __init__(self):
        self.errors = []
        self.warnings = []

    def validate_package(self, package_path):
        """
        Validate a .sagent package file.

        Args:
            package_path: Path to the .sagent (ZIP) file

        Returns:
            dict: {
                'valid': bool,
                'errors': list of error messages,
                'warnings': list of warning messages,
                'metadata': extracted agent metadata (if valid)
            }
        """
        self.errors = []
        self.warnings = []

        try:
            # Check file exists
            if not os.path.exists(package_path):
                self.errors.append("Package file does not exist")
                return self._result(False)

            # Check file size
            file_size = os.path.getsize(package_path)
            if file_size > self.MAX_PACKAGE_SIZE:
                self.errors.append(f"Package exceeds max size of {self.MAX_PACKAGE_SIZE / 1024 / 1024}MB")
                return self._result(False)

            # Check it's a valid ZIP
            if not zipfile.is_zipfile(package_path):
                self.errors.append("Package is not a valid ZIP file")
                return self._result(False)

            # Extract to temp directory
            with tempfile.TemporaryDirectory() as temp_dir:
                with zipfile.ZipFile(package_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)

                # Validate contents
                metadata = self._validate_contents(temp_dir)

                if not self.errors:
                    return self._result(True, metadata)

        except Exception as e:
            logger.error(f"Error validating package: {str(e)}")
            self.errors.append(f"Validation error: {str(e)}")

        return self._result(False)

    def _validate_contents(self, package_dir):
        """Validate the contents of extracted package."""
        metadata = {}

        # Check required files - first at root, then in single subdirectory
        agent_yaml_path = os.path.join(package_dir, 'agent.yaml')
        system_prompt_path = os.path.join(package_dir, 'system_prompt.txt')

        # If not at root, check for single top-level directory
        if not os.path.exists(agent_yaml_path):
            subdirs = [d for d in os.listdir(package_dir)
                      if os.path.isdir(os.path.join(package_dir, d)) and not d.startswith('.')]
            if len(subdirs) == 1:
                # Try inside the single subdirectory
                inner_dir = os.path.join(package_dir, subdirs[0])
                agent_yaml_path = os.path.join(inner_dir, 'agent.yaml')
                system_prompt_path = os.path.join(inner_dir, 'system_prompt.txt')
                # Update package_dir to point to inner directory for subsequent checks
                package_dir = inner_dir

        if not os.path.exists(agent_yaml_path):
            self.errors.append("Missing required file: agent.yaml")
            return metadata

        if not os.path.exists(system_prompt_path):
            self.errors.append("Missing required file: system_prompt.txt")
            return metadata

        # Validate agent.yaml
        try:
            with open(agent_yaml_path, 'r') as f:
                agent_config = yaml.safe_load(f)

            metadata = self._validate_agent_yaml(agent_config)

        except yaml.YAMLError as e:
            self.errors.append(f"Invalid YAML in agent.yaml: {str(e)}")
            return metadata
        except Exception as e:
            self.errors.append(f"Error reading agent.yaml: {str(e)}")
            return metadata

        # Validate system_prompt.txt
        try:
            with open(system_prompt_path, 'r') as f:
                system_prompt = f.read()

            self._validate_system_prompt(system_prompt)
            metadata['system_prompt'] = system_prompt

        except Exception as e:
            self.errors.append(f"Error reading system_prompt.txt: {str(e)}")
            return metadata

        # Check optional files
        self._check_optional_files(package_dir, metadata)

        return metadata

    def _validate_agent_yaml(self, config):
        """Validate agent.yaml structure and content."""
        metadata = {}

        # Check version
        if 'version' not in config:
            self.errors.append("agent.yaml missing required field: version")
        else:
            metadata['package_version'] = config['version']

        # Check metadata section
        if 'metadata' not in config:
            self.errors.append("agent.yaml missing required section: metadata")
            return metadata

        meta = config['metadata']

        # Validate required metadata fields
        required_fields = ['name', 'version', 'author', 'description', 'category', 'price', 'currency']
        for field in required_fields:
            if field not in meta:
                self.errors.append(f"metadata missing required field: {field}")
            else:
                metadata[field] = meta[field]

        # Optional llm_provider field
        if 'llm_provider' in meta:
            llm_provider = meta['llm_provider'].lower()
            if llm_provider not in ['anthropic', 'openai']:
                self.errors.append(f"Invalid llm_provider. Must be 'anthropic' or 'openai'")
            else:
                metadata['llm_provider'] = llm_provider
        else:
            # Default to anthropic if not specified
            metadata['llm_provider'] = 'anthropic'
            self.warnings.append("No llm_provider specified - defaulting to 'anthropic'")

        # Validate specific fields
        if 'name' in meta:
            name = meta['name']
            if not (3 <= len(name) <= 100):
                self.errors.append("Agent name must be 3-100 characters")

        if 'category' in meta:
            if meta['category'] not in self.VALID_CATEGORIES:
                self.errors.append(f"Invalid category. Must be one of: {', '.join(self.VALID_CATEGORIES)}")

        if 'price' in meta:
            try:
                price = float(meta['price'])
                if price < 0:
                    self.errors.append("Price cannot be negative")
            except:
                self.errors.append("Price must be a number")

        if 'version' in meta:
            # Basic semver check (X.Y.Z)
            import re
            if not re.match(r'^\d+\.\d+\.\d+$', meta['version']):
                self.warnings.append("Agent version should follow semantic versioning (e.g., 1.0.0)")

        # Optional but recommended fields
        if 'tags' not in meta:
            self.warnings.append("No tags specified - consider adding tags for better discoverability")

        # Extract agent configuration
        if 'agent' in config:
            metadata['agent_config'] = config['agent']

        # Extract capabilities
        if 'capabilities' in config:
            metadata['capabilities'] = config['capabilities']

        # Extract ethics
        if 'ethics' in config:
            metadata['ethics'] = config['ethics']
        else:
            self.warnings.append("No ethical guidelines specified")

        return metadata

    def _validate_system_prompt(self, prompt):
        """Validate system prompt content."""
        prompt_length = len(prompt)

        if prompt_length < self.MIN_SYSTEM_PROMPT_SIZE:
            self.errors.append(f"System prompt too short (min {self.MIN_SYSTEM_PROMPT_SIZE} characters)")

        if prompt_length > self.MAX_SYSTEM_PROMPT_SIZE:
            self.errors.append(f"System prompt too long (max {self.MAX_SYSTEM_PROMPT_SIZE} characters)")

        # Check for common issues
        if prompt.strip() == '':
            self.errors.append("System prompt is empty")

        # Basic harmful content check (very basic - should use Claude API for real check)
        harmful_keywords = ['hack', 'exploit', 'malware', 'phishing', 'scam']
        prompt_lower = prompt.lower()
        for keyword in harmful_keywords:
            if keyword in prompt_lower:
                self.warnings.append(f"System prompt contains potentially harmful keyword: {keyword}")

    def _check_optional_files(self, package_dir, metadata):
        """Check for optional files and add warnings if missing."""
        # Check for examples
        examples_dir = os.path.join(package_dir, 'examples')
        if not os.path.exists(examples_dir):
            self.warnings.append("No examples/ directory - consider adding example conversations")
        else:
            example_files = list(Path(examples_dir).glob('*.yaml'))
            metadata['example_count'] = len(example_files)

        # Check for knowledge base
        knowledge_dir = os.path.join(package_dir, 'knowledge')
        if not os.path.exists(knowledge_dir):
            self.warnings.append("No knowledge/ directory - consider adding reference materials")
        else:
            knowledge_files = list(Path(knowledge_dir).rglob('*'))
            metadata['knowledge_files'] = len([f for f in knowledge_files if f.is_file()])

        # Check for README
        readme_path = os.path.join(package_dir, 'README.md')
        if not os.path.exists(readme_path):
            self.warnings.append("No README.md - consider adding documentation for buyers")
        else:
            metadata['has_readme'] = True

    def _result(self, valid, metadata=None):
        """Build validation result."""
        return {
            'valid': valid,
            'errors': self.errors,
            'warnings': self.warnings,
            'metadata': metadata or {}
        }


class AgentPackageExtractor:
    """Extract and process validated .sagent packages."""

    def __init__(self, storage_path):
        """
        Initialize extractor.

        Args:
            storage_path: Directory to store extracted packages
        """
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)

    def extract_package(self, package_path, agent_id):
        """
        Extract package to storage.

        Args:
            package_path: Path to validated .sagent file
            agent_id: Unique agent ID

        Returns:
            str: Path to extracted package directory
        """
        agent_dir = os.path.join(self.storage_path, str(agent_id))

        # Remove existing if present
        if os.path.exists(agent_dir):
            shutil.rmtree(agent_dir)

        # Extract
        with zipfile.ZipFile(package_path, 'r') as zip_ref:
            zip_ref.extractall(agent_dir)

        return agent_dir

    def load_agent_data(self, agent_id):
        """
        Load agent configuration from storage.

        Args:
            agent_id: Agent ID

        Returns:
            dict: {
                'metadata': dict from agent.yaml,
                'system_prompt': str from system_prompt.txt,
                'examples': list of example conversations,
                'knowledge': combined knowledge base text
            }
        """
        agent_dir = os.path.join(self.storage_path, str(agent_id))

        if not os.path.exists(agent_dir):
            raise FileNotFoundError(f"Agent {agent_id} package not found")

        # Check if files are in root or subdirectory
        agent_yaml_path = os.path.join(agent_dir, 'agent.yaml')
        if not os.path.exists(agent_yaml_path):
            # Look for single subdirectory
            subdirs = [d for d in os.listdir(agent_dir)
                      if os.path.isdir(os.path.join(agent_dir, d)) and not d.startswith('.')]
            if len(subdirs) == 1:
                agent_dir = os.path.join(agent_dir, subdirs[0])

        data = {}

        # Load agent.yaml
        with open(os.path.join(agent_dir, 'agent.yaml'), 'r') as f:
            data['metadata'] = yaml.safe_load(f)

        # Load system_prompt.txt
        with open(os.path.join(agent_dir, 'system_prompt.txt'), 'r') as f:
            data['system_prompt'] = f.read()

        # Load examples (if present)
        examples_dir = os.path.join(agent_dir, 'examples')
        if os.path.exists(examples_dir):
            examples = []
            for example_file in Path(examples_dir).glob('*.yaml'):
                with open(example_file, 'r') as f:
                    examples.append(yaml.safe_load(f))
            data['examples'] = examples
        else:
            data['examples'] = []

        # Load knowledge base (if present)
        knowledge_dir = os.path.join(agent_dir, 'knowledge')
        if os.path.exists(knowledge_dir):
            knowledge_texts = []
            for knowledge_file in Path(knowledge_dir).rglob('*'):
                if knowledge_file.is_file():
                    try:
                        with open(knowledge_file, 'r') as f:
                            knowledge_texts.append(f.read())
                    except:
                        pass  # Skip binary files
            data['knowledge'] = '\n\n---\n\n'.join(knowledge_texts)
        else:
            data['knowledge'] = ''

        return data
