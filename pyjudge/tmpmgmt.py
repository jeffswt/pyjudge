
import os
import uuid

from . import config

__tmp_files = set()

def create_tmpfile():
    tmp_dir = config.get_config('tmp_dir')
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)
    while True:
        uid = str(uuid.uuid4())
        pth = os.path.join(tmp_dir, uid)
        if not os.path.exists(pth):
            break
        continue
    __tmp_files.add(uid)
    return pth

def remove_tmpfile(fil):
    tmp_dir = config.get_config('tmp_dir')
    fn = os.path.basename(fil)
    pth = os.path.join(tmp_dir, fn)
    if os.path.exists(pth):
        try:
            os.remove(pth)
        except:
            pass
    if fn in __tmp_files:
        __tmp_files.remove(fn)
    return
