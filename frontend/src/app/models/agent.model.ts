export interface AgentInput {
    fen: string;
    depth:number;
    max_articles : number;
    max_video : number;
}

export interface AgentOutput {
    final_answer: string;
}

export interface RequestState<T> {
    data: AgentOutput | null;
    isLoading: boolean;
    error: string | null;
}