'''
This script adds the the project root to path. This makes it so you can import
Blendkrieg using `import Blendkrieg` within Blender's Python environment without
installing to the addons directory.

This file is ran whenever you import the test folder. So if you start the tests
off in the Blendkrieg folder as the current directory all you would need to do
is `import .test` and you can start using `import Blendkrieg`.

Suggested usage: ```py
import .test
import Blendkrieg # The tests themselves should be able to handle this.
```
'''

import sys
from pathlib import Path

# Peel back directories until we find the project root.
location = Path(__file__).resolve()
while not location.samefile(location.root)  \
  and not location.joinpath('.git').exists():
	location = location.parent

sys.path.insert(0, location.parent)

del sys, Path
