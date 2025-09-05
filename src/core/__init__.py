# -*- coding: utf-8 -*-
"""
把老包名 'core' 映射到新的 'src.core'，让历史代码/测试继续可用。
"""
import importlib
import sys as _sys

# 让 `import core` 指向当前包
_sys.modules.setdefault("core", importlib.import_module(__name__))

# 同时把子包 core.workflows 指到 src.core.workflows
try:
    _sys.modules.setdefault(
        "core.workflows",
        importlib.import_module("src.core.workflows"),
    )
except Exception:
    # 如果运行环境特殊（例如直接以 'core' 为顶层包），静默忽略
    pass
