export interface AgentInput {
    fen: string;
}

export interface AgentOutput {
    answer: string;
}

export interface RequestState<T> {
    data: AgentOutput | null;
    isLoading: boolean;
    error: string | null;
}