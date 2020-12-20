from dataclasses import dataclass
from typing import Optional, Tuple, List, Any, Literal, Union

@dataclass
class Capabilities:

    supportsConfigurationDoneRequest: Optional[bool] = None
    supportsFunctionBreakpoints: Optional[bool] = None
    supportsConditionalBreakpoints: Optional[bool] = None
    supportsHitConditionalBreakpoints: Optional[bool] = None
    supportsEvaluateForHovers: Optional[bool] = None
    exceptionBreakpointFilters: Optional[List[Any]] = None
    supportsStepBack: Optional[bool] = None
    supportsSetVariable: Optional[bool] = None
    supportsRestartFrame: Optional[bool] = None
    supportsGotoTargetsRequest: Optional[bool] = None
    supportsStepInTargetsRequest: Optional[bool] = None
    supportsCompletionsRequest: Optional[bool] = None
    completionTriggerCharacters: Optional[List[str]] = None
    supportsModulesRequest: Optional[bool] = None
    additionalModuleColumns: Optional[List[Any]] = None
    supportedChecksumAlgorithms: Optional[List[Any]] = None
    supportsRestartRequest: Optional[bool] = None
    supportsExceptionOptions: Optional[bool] = None
    supportsValueFormattingOptions: Optional[bool] = None
    supportsExceptionInfoRequest: Optional[bool] = None
    supportTerminateDebuggee: Optional[bool] = None
    supportsDelayedStackTraceLoading: Optional[bool] = None
    supportsLoadedSourcesRequest: Optional[bool] = None
    supportsLogPoints: Optional[bool] = None
    supportsTerminateThreadsRequest: Optional[bool] = None
    supportsSetExpression: Optional[bool] = None
    supportsTerminateRequest: Optional[bool] = None
    supportsDataBreakpoints: Optional[bool] = None
    supportsReadMemoryRequest: Optional[bool] = None
    supportsDisassembleRequest: Optional[bool] = None
    supportsCancelRequest: Optional[bool] = None
    supportsBreakpointLocationsRequest: Optional[bool] = None


@dataclass
class Thread:

    id: int
    name: str

    stackframes: Optional[List['StackFrame']] = None

    def get_stackframe(self, stackframe_id):
        for stackframe in self.stackframes:
            if stackframe.id == stackframe_id:
                return stackframe

@dataclass
class Source:

    name: Optional[str] = None
    path: Optional[str] = None
    sourceReference: Optional[str] = None
    presentationHint: Optional[Literal['normal', 'emphazise', 'deemphasize']] = None
    origin: Optional[str] = None
    sources: Optional[List['Source']] = None
    adapterData: Optional[Any] = None
    checksums: Optional[Any] = None

@dataclass
class StackFrame:

    id: int
    name: str
    line: int
    column: int
    source: Optional['Source'] = None
    endLine: Optional[int] = None
    endColumn: Optional[int] = None
    instructionPointerReference: Optional[str] = None
    moduleId: Optional[Union[int, str]] = None
    presentationHint: Optional[Literal['normal', 'label', 'subtle']] = None

    scopes: Optional[List['Scope']] = None

@dataclass
class Scope:

    name: str
    variablesReference: int
    expensive: bool
    presentationHint: Optional[Literal['arguments', 'locals', 'registers']] = None
    namedVariables: Optional[int] = None
    indexedVariables: Optional[int] = None
    indexedVariables: Optional[int] = None
    source: Optional['Source'] = None
    line: Optional[int] = None
    column: Optional[int] = None
    endLine: Optional[int] = None
    endColumn: Optional[int] = None

    variables: Optional[List['Variable']] = None

@dataclass
class Variable:

    name: str
    value: str
    variablesReference: int
    type: Optional[str] = None
    presentationHint: Optional[Any] = None
    evaluateName: Optional[str] = None
    namedVariables: Optional[int] = None
    indexedVariables: Optional[int] = None
    memoryReference: Optional[str] = None

    properties: Optional[List['Variable']] = None

@dataclass
class BreakpointLocation:

    line: int
    column: Optional[int] = None
    endLine: Optional[int] = None
    endColumn: Optional[int] = None

@dataclass
class SourceBreakpoint:

    line: int
    column: Optional[int] = None
    condition: Optional[str] = None
    hitCondition: Optional[str] = None
    logMessage: Optional[str] = None

@dataclass
class Breakpoint:

    verified: bool
    id: Optional[int] = None
    message: Optional[str] = None
    source: Optional[Source] = None
    line: Optional[int] = None
    column: Optional[int] = None
    endLine: Optional[int] = None
    endColumn: Optional[int] = None
    instructionReference: Optional[str] = None
    offset: Optional[int] = None

@dataclass
class StepInTarget:

    pass

@dataclass
class GotoTarget:

    pass


