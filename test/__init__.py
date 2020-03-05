'''
This file adds the directory just before Blendkrieg to path. Which makes it so
you can import Blendkrieg using `import Blendkrieg` without installing to the
addons directory.

This file is ran whenever you import the test folder. So if you start the tests
off in the Blendkrieg folder as the current directory all you would need to do
is `import .test` and you can start using `import Blendkrieg`.

Suggested usage: ```py
import .test
import Blendkrieg # The tests themselves should be able to handle this.
```
'''

import sys
from os import path

# Adds the directory that contains Blendkrieg to path so it can be imported
# using import Blendkrieg.
sys.path.insert(0, path.dirname(path.dirname(__file__)))

del sys, path
