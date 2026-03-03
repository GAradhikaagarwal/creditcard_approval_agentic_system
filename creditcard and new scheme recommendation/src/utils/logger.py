import logging
import sys
import os

def setup_logger():
    """
    Configures a centralized logger that outputs to both the console 
    and a dedicated agents.log file.
    """
    logger = logging.getLogger("src")
    logger.setLevel(logging.INFO)
    
    # Prevent adding handlers multiple times if instantiated repeatedly
    if not logger.handlers:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Console Handler
        ch = logging.StreamHandler(sys.stdout)
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        
        # File Handler
        try:
            # Ensure the logs directory exists relative to the project root
            log_dir = os.path.join(os.getcwd(), "logs")
            os.makedirs(log_dir, exist_ok=True)
            
            fh = logging.FileHandler(os.path.join(log_dir, "agents.log"))
            fh.setFormatter(formatter)
            logger.addHandler(fh)
        except Exception as e:
            print(f"Failed to setup file logging: {e}")
            
    return logger

# Expose a pre-configured universal logger
app_logger = setup_logger()
