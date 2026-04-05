# config_loader.py
#  Utility to parse YAML config files and identify the configuration variables  for 
# Arachnet Clinical Embeddings.
# Usage:

import sys
import omegaconf
from src.common.logger import get_logger

logger = get_logger(__name__)
logger.info("Loading RF2 file: %s", filepath)


with open(yaml_file) as f:
    cfg = yaml.safe_load(f)

env_cfg = cfg["environments"][env]["paths"]

# resolve {base} templates
resolved = {}
base = env_cfg["base"]

for key, value in env_cfg.items():
    resolved[key] = value.format(base=base)

# emit shell exports
for k, v in resolved.items():
    print(f'export {k.upper()}="{v}"')