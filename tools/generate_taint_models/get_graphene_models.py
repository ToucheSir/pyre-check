# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

import logging
import re
from typing import Callable, Iterable, List, Optional

from ...api.connection import PyreConnection
from .generator_specifications import (
    AnnotationSpecification,
    WhitelistSpecification,
    default_entrypoint_taint,
)
from .get_methods_of_subclasses import MethodsOfSubclassesGenerator
from .get_models_filtered_by_callable import ModelsFilteredByCallableGenerator
from .model import PyreFunctionDefinitionModel
from .model_generator import ModelGenerator


LOG: logging.Logger = logging.getLogger(__name__)


class GrapheneModelsGenerator(ModelGenerator[PyreFunctionDefinitionModel]):
    def __init__(
        self,
        pyre_connection: PyreConnection,
        annotations: Optional[AnnotationSpecification] = None,
        whitelist: Optional[WhitelistSpecification] = None,
    ) -> None:
        self.pyre_connection = pyre_connection

        self.annotations: AnnotationSpecification = (
            annotations or default_entrypoint_taint
        )
        self.whitelist: WhitelistSpecification = whitelist or WhitelistSpecification(
            parameter_name={"self", "cls", "*_"},
            parameter_type={"graphql.execution.base.ResolveInfo"},
        )

    def gather_functions_to_model(self) -> Iterable[Callable[..., object]]:
        return []

    def compute_models(
        self, functions_to_model: Iterable[Callable[..., object]]
    ) -> List[PyreFunctionDefinitionModel]:
        resolver_models = self._models_for_subclass_methods_matching_pattern(
            pattern=re.compile("resolve_.*"),
            base_classes=[
                "graphene.types.objecttype.ObjectType",
                "graphene.ObjectType",
            ],
        )
        mutator_models = self._models_for_subclass_methods_matching_pattern(
            pattern=re.compile("\\.mutate$"),
            base_classes=["graphene.types.mutation.Mutation", "graphene.Mutation"],
        )
        return resolver_models + mutator_models

    def _models_for_subclass_methods_matching_pattern(
        self, pattern: re.Pattern, base_classes: List[str]
    ) -> List[PyreFunctionDefinitionModel]:
        def matches_pattern(method: PyreFunctionDefinitionModel) -> bool:
            return bool(pattern.search(method.callable_name))

        return list(
            ModelsFilteredByCallableGenerator(
                generator_to_filter=MethodsOfSubclassesGenerator(
                    base_classes=base_classes,
                    pyre_connection=self.pyre_connection,
                    annotations=self.annotations,
                    whitelist=self.whitelist,
                ),
                filter=matches_pattern,
            ).generate_models()
        )
