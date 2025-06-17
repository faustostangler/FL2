from pathlib import Path

class Config:
    def __init__(self):
        """ Initializes the configuration settings for the application.
        This includes setting up paths for logging and other necessary directories.
        """
        # Folders and files
        TEMP_FOLDER = "temp"
        LOG_FILE = "fly_logger.log"

        # Initialize paths
        temp_path = Path(TEMP_FOLDER)
        self.paths = {
            "root_folder": Path(__file__).parent.parent.resolve(),
            "log_file": temp_path / LOG_FILE,
            # more paths...
        }

        # Create necessary directories
        for path in self.paths.values():
            path_obj = Path(path)
            folder = path_obj.parent if path_obj.suffix else path_obj
            folder.mkdir(parents=True, exist_ok=True)
