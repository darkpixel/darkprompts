from contextlib import ContextDecorator, AbstractContextManager, contextmanager
from folder_paths import get_output_directory
from pathlib import Path

import folder_paths
import glob
import json
import logging
import os
import os.path
import random
import re

logger = logging.getLogger(__name__)


class DarkData(object):
    """Basic management of a temporary datafile (JSON) for tracking changes or saving settings"""

    filename = None
    data = {}
    changed_data = {}

    def __init__(self, filename):
        # logger.info("DarkData init start: data: %s" % (self.data))
        # logger.info("DarkData init start: changed_data: %s" % (self.changed_data))

        self.filename = filename
        # logger.info("DarkData read: %s" % (self.data))
        # logger.info("DarkData init finished: data: %s" % (self.data))
        # logger.info("DarkData init finished: changed_data: %s" % (self.changed_data))

    def __enter__(self):
        # logger.info("__enter__: %s" % (self.changed_data))
        try:
            with open(
                os.path.join(
                    folder_paths.temp_directory,
                    self.filename,
                ),
                "r",
            ) as F:
                self.data.update(json.loads(F.read()))
        except FileNotFoundError:
            # Probably the first run
            logger.info("%s does not exist, probably first run", self.filename)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # logger.info("__exit__")
        # logger.info("About to exit with filename: %s" % (self.filename))
        # logger.info("data: %s" % (self.data))
        # logger.info("changed_data: %s" % (self.changed_data))

        if self.filename and self.changed_data:
            # There appears to be a bug in ComfyUI when you pass the arg
            # --temp-directory /some/folder
            # folder_paths.temp_directory will actually contain /some/folder/temp
            # so just make sure it exists before trying to write to it
            Path(folder_paths.temp_directory).mkdir(parents=True, exist_ok=True)

            save_path = os.path.join(folder_paths.temp_directory, self.filename)
            try:
                with open(
                    save_path,
                    "w",
                ) as F:
                    F.write(json.dumps(self.changed_data))
                    logger.info("DarkData wrote: %s" % (self.changed_data))
            except FileNotFoundError:
                logger.error("Unable to write file %s" % (save_path))
                pass

    def get_key(self, key, default=None):
        """Get a key by name from the datafile.  If the key does not exist, return None."""
        return self.data.get(key, default)

    def set_key(self, key, data):
        """Set a key by name to the value in data."""
        self.changed_data.update({key: data})


#    def update(self, data):
#        """Update all the data in the file"""
#        self.changed_data.update(data)
#
#    def replace(self, data):
#        """Replace all the data in the file."""
#        self.changed_data = data

#    def save(self):
#        """Write the data dictionary to the file"""
#        data_to_write = {}
#        data_to_write.update(self.data)
#        data_to_write.update(self.changed_data)
#        logger.info("save() data_to_write: %s" % (data_to_write))
#        # There appears to be a bug in ComfyUI when you pass the arg
#        # --temp-directory /some/folder
#        # folder_paths.temp_directory will actually contain /some/folder/temp
#        # so just make sure it exists before trying to write to it
#        Path(folder_paths.temp_directory).mkdir(parents=True, exist_ok=True)
#        with open(
#            os.path.join(folder_paths.temp_directory, self.filename),
#            "w",
#        ) as F:
#            F.write(json.dumps(self.data_to_write))
#
#        logger.info("Wrote data: %s" % (self.data_to_write))
#        return self.changed_data


class DarkFolderBase(DarkData):
    """Provides information on folders given a prefix.  Allows getting folders based on various information such as file count."""

    folders = {}
    base_path = get_output_directory()
    prefix = None
    prefix_path = None
    prefix = ""
    highest_folder_number = 0

    def __init__(self, filename, prefix=""):
        super().__init__(filename)

        self.prefix = prefix
        self.prefix_path = os.path.join(self.base_path, self.prefix)

    def __enter__(self):
        super().__enter__()

        # Look at all folders that start with our prefix
        prefix_matches = glob.glob(self.prefix_path + "*")
        for m in prefix_matches:
            if os.path.isdir(m):
                try:
                    # Create a dict of folders keyed with the number and valued
                    # with the number of files in it
                    self.folders.update(
                        {
                            int(m.replace(self.prefix_path, "")): len(
                                [
                                    fname
                                    for fname in os.listdir(m)
                                    if os.path.isfile(os.path.join(m, fname))
                                ]
                            )
                        }
                    )
                except ValueError:
                    # This happens when there is a folder matching the prefix
                    # but it does not have a numeric entry.  Given a prefix of
                    # 'batch-' a folder named 'batch-' or 'batch-abc' would
                    # cause this.  Just ignore it
                    pass

        for key in list(self.folders.keys()):
            # Remove folders from the list that have zero items
            if self.folders[key] == 0:
                del self.folders[key]

        # Get the highest folder number with data in it
        if self.folders:
            self.highest_folder_number = list(self.folders.keys())[-1]

        # logger.info("DarFolderBase entered with folders: %s" % (self.folders))
        return self

    def get_highest_not_full(self, max_size):
        ret = ""

        key_list = list(self.folders.keys())
        key_list.sort(key=int)
        if key_list:
            key = key_list.pop()
            if self.folders[key] < max_size:
                ret = self.prefix_path + str(key)
            else:
                ret = self.prefix_path + str(key + 1)
        else:
            ret = self.prefix_path + "0"
        return ret

    def get_first_available(self, max_size):
        ret = ""
        for i in range(0, self.highest_folder_number + 10):
            if i in self.folders:
                if self.folders[i] < max_size:
                    ret = self.prefix_path + str(i)
                    break
            else:
                ret = self.prefix_path + str(i)
        print("get_first_available: %s" % (ret))
        return ret

    def get_new(self):
        ret = ""
        if self.folders:
            key_list = list(self.folders.keys())
            key_list.sort(key=int)
            ret = self.prefix_path + str(key_list[-1] + 1)
        else:
            ret = self.prefix_path + "0"
        print("get_new: %s" % (ret))
        return ret

    def get_new_on_input_change(self, max_size, new_input):
        # logger.info("get_new_on_input_change() data: %s" % (self.data))
        # logger.info("get_new_on_input_change() changed_data: %s" % (self.changed_data))
        folder_to_use = ""
        existing_data = self.get_key("input_data")
        if existing_data and existing_data == str(new_input):
            folder_to_use = self.get_highest_not_full(max_size)
        else:
            logger.info(
                "Input changed from %s to %s" % (str(existing_data), str(new_input))
            )
            folder_to_use = self.get_new()

        self.set_key("input_data", str(new_input))

        print("get_new_on_input_change: %s" % (folder_to_use))

        return folder_to_use
