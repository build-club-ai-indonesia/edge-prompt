"""
TemplateEngine - Handles template processing and variable substitution.

This module is responsible for loading templates and processing them
with variables according to the EdgePrompt specifications.
"""

import logging
import re
import os
import json
from typing import Dict, Any, Optional, List, Tuple

class TemplateEngine:
    """
    Processes templates with variable substitution and constraint encoding.
    
    This class implements the TemplateProcessing algorithm as specified in the
    EdgePrompt methodology, handling:
    - Template validation against schemas
    - Variable substitution
    - Constraint encoding
    - Token efficiency optimization
    """
    
    def __init__(self, template_dir: Optional[str] = None):
        """
        Initialize the TemplateEngine.
        
        Args:
            template_dir: Directory containing template definitions (optional)
        """
        self.logger = logging.getLogger("edgeprompt.runner.template")
        self.template_dir = template_dir
        self.logger.info("TemplateEngine initialized")
        
        # Regular expression for extracting variables from templates
        self.var_pattern = re.compile(r'\[([a-zA-Z_]+)\]')
    
    def load_template(self, template_name: str) -> Dict[str, Any]:
        """
        Load a template from file.
        
        Args:
            template_name: Name or path of the template
            
        Returns:
            Dict containing the template configuration
            
        Raises:
            FileNotFoundError: If template cannot be found
        """
        # Handle both direct paths and template names
        if os.path.isfile(template_name):
            template_path = template_name
        elif self.template_dir and os.path.isfile(os.path.join(self.template_dir, f"{template_name}.json")):
            template_path = os.path.join(self.template_dir, f"{template_name}.json")
        else:
            # Try common locations
            locations = [
                f"{template_name}.json",
                f"configs/templates/{template_name}.json",
                f"../configs/templates/{template_name}.json"
            ]
            for loc in locations:
                if os.path.isfile(loc):
                    template_path = loc
                    break
            else:
                raise FileNotFoundError(f"Template not found: {template_name}")
        
        self.logger.info(f"Loading template from: {template_path}")
        try:
            with open(template_path, 'r') as f:
                template = json.load(f)
            
            # Basic schema validation
            required_fields = ['id', 'type', 'pattern']
            missing = [field for field in required_fields if field not in template]
            if missing:
                self.logger.error(f"Template missing required fields: {', '.join(missing)}")
                raise ValueError(f"Invalid template format: missing {', '.join(missing)}")
                
            return template
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in template file: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Error loading template: {str(e)}")
            raise
    
    def process_template(self, template: Dict[str, Any], variables: Dict[str, str]) -> str:
        """
        Process a template by substituting variables and encoding constraints.
        
        Args:
            template: The template configuration
            variables: Dictionary of variable values to substitute
            
        Returns:
            Processed template string ready for model input
            
        Raises:
            ValueError: If required variables are missing
        """
        self.logger.info(f"Processing template: {template.get('id', 'unknown')}")
        
        # 1. Extract template pattern and validate
        pattern = template.get('pattern', '')
        if not pattern:
            raise ValueError("Template has no pattern")
            
        # 2. Extract all variables from pattern
        template_vars = self.var_pattern.findall(pattern)
        self.logger.debug(f"Found variables in template: {template_vars}")
        
        # 3. Check for missing variables
        missing_vars = [var for var in template_vars if var not in variables]
        if missing_vars:
            self.logger.error(f"Missing variables for template: {missing_vars}")
            raise ValueError(f"Missing required variables: {', '.join(missing_vars)}")
        
        # 4. Substitute variables
        processed = pattern
        for var in template_vars:
            if var in variables:
                processed = processed.replace(f"[{var}]", variables[var])
        
        # 5. Apply constraint encoding
        constraints = template.get('constraints', [])
        if constraints:
            constraint_text = self._format_constraints(constraints, template.get('type', 'generic'))
            processed = self._apply_constraints(processed, constraint_text, template.get('type', 'generic'))
        
        # 6. Optimize for token efficiency
        processed = self._optimize_tokens(processed)
        
        self.logger.info(f"Template processing complete: {len(processed)} characters")
        return processed
    
    def _format_constraints(self, constraints: List[str], template_type: str) -> str:
        """
        Format constraints according to template type.
        
        Args:
            constraints: List of constraint strings
            template_type: The type of template (affects formatting)
            
        Returns:
            Formatted constraint string
        """
        if not constraints:
            return ""
            
        if template_type == "question_generation":
            return "CONSTRAINTS:\n- " + "\n- ".join(constraints)
        elif template_type == "validation":
            return "Validation criteria:\n- " + "\n- ".join(constraints)
        else:
            return "Constraints:\n- " + "\n- ".join(constraints)
    
    def _apply_constraints(self, processed: str, constraint_text: str, template_type: str) -> str:
        """
        Apply constraints to the processed template in the appropriate location.
        
        Args:
            processed: The processed template so far
            constraint_text: Formatted constraint text
            template_type: The type of template
            
        Returns:
            Template with constraints applied
        """
        if not constraint_text:
            return processed
            
        # Different template types may have constraints in different locations
        if template_type == "question_generation":
            # For question generation, add constraints after the task description
            if "TASK:" in processed:
                parts = processed.split("TASK:", 1)
                return f"{parts[0]}TASK:{parts[1]}\n\n{constraint_text}"
            else:
                return f"{processed}\n\n{constraint_text}"
        elif template_type == "validation":
            # For validation templates, add criteria at the end
            return f"{processed}\n\n{constraint_text}"
        else:
            # Default: append constraints at the end
            return f"{processed}\n\n{constraint_text}"
    
    def _optimize_tokens(self, text: str) -> str:
        """
        Optimize the template for token efficiency.
        
        Args:
            text: The processed template text
            
        Returns:
            Optimized template text
        """
        # Basic optimizations
        # 1. Eliminate redundant whitespace
        optimized = re.sub(r'\n\s*\n', '\n\n', text)
        optimized = re.sub(r' +', ' ', optimized)
        
        # 2. Consolidate similar constraints (future enhancement)
        
        # 3. Ensure proper spacing
        optimized = optimized.strip()
        
        return optimized
        
    def extract_template_variables(self, template: Dict[str, Any]) -> List[str]:
        """
        Extract all variables from a template pattern.
        
        Args:
            template: The template configuration
            
        Returns:
            List of variable names found in the pattern
        """
        pattern = template.get('pattern', '')
        return self.var_pattern.findall(pattern)
    
    def get_template_schema(self, template_type: str) -> Dict[str, Any]:
        """
        Get the JSON schema for a template type.
        
        Args:
            template_type: Type of template
            
        Returns:
            JSON schema dict for validation
        """
        schema_paths = {
            "question_generation": "schemas/teacher_input_template_schema.json",
            "validation": "schemas/validation_sequence_schema.json",
            "rubric": "schemas/rubric_schema.json"
        }
        
        if template_type not in schema_paths:
            self.logger.warning(f"No schema defined for template type: {template_type}")
            return {}
            
        schema_path = schema_paths[template_type]
        if not os.path.isfile(schema_path):
            self.logger.warning(f"Schema file not found: {schema_path}")
            return {}
            
        try:
            with open(schema_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading schema: {str(e)}")
            return {} 