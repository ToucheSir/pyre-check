# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import typing

class MultiValueDict(typing.Dict[typing.Any, typing.Any]):
    def copy(self) -> MultiValueDict: ...
