export interface AgentInput {
    fen: string;
    depth:number;
    maxArticles : number;
    max_videos : number;
}

export interface AgentOutput {
    answer: string;
}

export interface RequestState<T> {
    data: AgentOutput | null;
    isLoading: boolean;
    error: string | null;
}